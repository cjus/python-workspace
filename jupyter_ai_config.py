# Jupyter AI configuration for the python-workspace repo.
#
# Tries to cap the Ollama context window (num_ctx) for the default model to 128K
# tokens to reduce KV-cache memory use. 128K = 131072 tokens.
#
# Jupyter AI v3 reaches Ollama through LiteLLM (not langchain). The keys under
# each "provider/model" entry are unpacked and passed to the model call, and the
# key is matched exactly against the LiteLLM model id "<provider>/<model>".
#
# CAVEAT: LiteLLM does not reliably forward a top-level `num_ctx` to Ollama
# (see https://github.com/BerriAI/litellm/issues/12930 and
# https://github.com/BerriAI/litellm/issues/13904). If the cap doesn't take
# effect (check `ollama ps` / the model's loaded context), set it on the Ollama
# side instead with a Modelfile:
#
#     # Modelfile
#     FROM gemma4:26b-mlx
#     PARAMETER num_ctx 131072
#     # then: ollama create gemma4:26b-mlx-128k -f Modelfile
#
# Loaded via:  jupyter lab --config=jupyter_ai_config.py   (wired up in start.sh)

c = get_config()  # noqa: F821  (provided by the Jupyter config loader)

c.AiExtension.model_parameters = {
    "ollama/gemma4:26b-mlx": {
        "num_ctx": 131072,  # 128K context window (verify it takes effect — see caveat above)
    },
}

# ── Default responder for un-mentioned messages ──────────────────────────────
# With multiple personas loaded (Jupyternaut + the ACP personas + any local
# persona under `.jupyter/personas/`), a single-user chat only auto-routes a
# message that has NO `@`-mention if a *default* persona is set. The upstream
# trait default points at a stale id (`...::jupyter_ai::JupyternautPersona`),
# but the real id is `...::jupyter_ai_jupyternaut::JupyternautPersona`, so it
# never resolves and bare messages reach no one ("No default persona is set").
# Pin the correct id so plain messages go to Jupyternaut (→ the configured
# OpenRouter / Ollama model). `@`-mention any other persona to override per-message.
c.PersonaManager.default_persona_id = (
    "jupyter-ai-personas::jupyter_ai_jupyternaut::JupyternautPersona"
)


# ── Workaround: fix the upstream `/refresh-personas` crash ───────────────────
# jupyter_ai_jupyternaut 3.0.0 ships `JupyternautPersona.shutdown` as a *sync*
# method, but `BasePersona.shutdown` (and the caller in
# `PersonaManager.shutdown_personas`, `await persona.shutdown()`) are async. So
# running `/refresh-personas` raises:
#   TypeError: object NoneType can't be used in 'await' expression
# and `RuntimeWarning: coroutine 'BasePersona.shutdown' was never awaited`.
# shutdown_personas() runs *before* the reload, so the whole refresh aborts and
# no personas get hot-reloaded.
#
# We patch the method to be async here (at config-load time, before any persona
# is initialized). This lives in the repo so it survives `.venv` rebuilds, and
# is guarded so a future upstream fix / API change can never break startup.
# Remove once jupyter_ai_jupyternaut fixes shutdown to be `async def`.
try:
    from jupyter_ai_jupyternaut.jupyternaut.jupyternaut import JupyternautPersona
    from jupyter_ai_persona_manager import BasePersona
    import inspect

    if not inspect.iscoroutinefunction(JupyternautPersona.shutdown):

        async def _jupyternaut_shutdown_async(self):
            # Mirror the upstream body, but await the async base shutdown.
            # Call BasePersona.shutdown explicitly — a reassigned function has no
            # `__class__` cell, so `super()` is unavailable here.
            if hasattr(self, "_memory_store"):
                self.parent.event_loop.create_task(self._memory_store.conn.close())
            await BasePersona.shutdown(self)

        JupyternautPersona.shutdown = _jupyternaut_shutdown_async
except Exception as exc:  # never let a patch failure block server startup
    import logging

    logging.getLogger("jupyter_ai_config").warning(
        "Could not patch JupyternautPersona.shutdown (/refresh-personas may "
        "still crash): %s",
        exc,
    )
