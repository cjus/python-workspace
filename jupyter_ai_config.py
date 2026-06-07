# Jupyter AI configuration for the python-workspace repo.
#
# Caps the Ollama context window (num_ctx) for the default model to 32K
# tokens to reduce KV-cache memory use. 32K = 32768 tokens.
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
#     FROM gemma4:12b
#     PARAMETER num_ctx 32768
#     # then: ollama create gemma4-32k -f Modelfile
#
# Loaded via:  jupyter lab --config=jupyter_ai_config.py   (wired up in start.sh)

c = get_config()  # noqa: F821  (provided by the Jupyter config loader)

# NOTE: keys are matched EXACTLY against the selected model id. Entries are
# provided for the repo defaults on each platform; if you pick a different
# model in Jupyternaut Settings, add/edit a key to match it or no cap applies.
#
# NOTE: the trait lives on `JupyternautExtension` in Jupyter AI v3 (the v2
# name, `AiExtension`, is silently ignored — the server logs
# "Configured model parameters: {}" if you use it).
_model_num_ctx = {
    # Repo default on ALL platforms (macOS / Windows / Linux):
    "gemma4:12b": 32768,  # 32K — sized for ~16 GB machines; raise if you have headroom
    # Advanced options (only apply if you select one of these in AI Settings):
    "gemma4:26b": 131072,  # 128K — for ≥32 GB RAM / large-GPU boxes
    "gemma4:26b-mlx": 131072,  # 128K — Apple-Silicon-only MLX build (≥36 GB memory)
}
# Each model is entered under BOTH LiteLLM prefixes so the cap applies however
# the model id is written. "ollama_chat/<model>" is the one to use for the
# chat (see the default-chat-model section below for why); "ollama/<model>"
# is kept so older docs/configs still get the cap.
c.JupyternautExtension.model_parameters = {
    f"{_prefix}/{_model}": {"num_ctx": _num_ctx}
    for _model, _num_ctx in _model_num_ctx.items()
    for _prefix in ("ollama_chat", "ollama")
}

# ── Default chat model: make the chat work out of the box ────────────────────
# Jupyternaut answers every message with "No chat model is configured." until
# `model_provider_id` is set in <jupyter-data-dir>/jupyter_ai/config.json (the
# file behind Settings -> AI Settings). A fresh install ships it as null, and a
# v2 -> v3 upgrade leaves it null too (v2 stored colon-format ids like
# "ollama:model" that v3/LiteLLM, which uses "ollama/model", does not migrate).
#
# `initial_language_model` seeds that file at startup — but upstream merges it
# with deepmerge's `always_merger`, where the DEFAULT wins over the saved
# config. Setting it unconditionally would reset a user's model choice on
# every server restart. So: only set it when no chat model is configured yet.
# Users keep full control via AI Settings afterwards.
try:
    import json as _json
    import os as _os

    from jupyter_core.paths import jupyter_data_dir as _jupyter_data_dir

    # Same default as start.sh / start.ps1 on every platform: the standard
    # GGUF build sized for ~16 GB machines. (Advanced options like the
    # Apple-only `-mlx` builds are covered in docs/TEACHERS-GUIDE.md.)
    #
    # Why the "ollama_chat/" prefix (not "ollama/")? Jupyternaut binds tools
    # to the chat agent, and LiteLLM's two Ollama providers handle tools very
    # differently:
    #   - "ollama_chat/<model>" → Ollama's native /api/chat tool calling.
    #   - "ollama/<model>"      → /api/generate with PROMPT-EMULATED tools:
    #     LiteLLM instructs the model to answer ONLY with a JSON tool call,
    #     so every chat reply leaks as raw `{"name": "bash", "arguments":
    #     ...}` text instead of an answer.
    # Always use "ollama_chat/" for the chat model.
    _default_chat_model = "ollama_chat/gemma4:12b"

    _jai_config_path = _os.path.join(_jupyter_data_dir(), "jupyter_ai", "config.json")
    _model_configured = False
    try:
        with open(_jai_config_path, encoding="utf-8") as _f:
            _model_configured = bool(_json.load(_f).get("model_provider_id"))
    except (FileNotFoundError, ValueError):
        pass  # no config yet (fresh install) or unreadable JSON — seed a default

    if not _model_configured:
        c.JupyternautExtension.initial_language_model = _default_chat_model
except Exception as _exc:  # never let this convenience block server startup
    import logging as _logging

    _logging.getLogger("jupyter_ai_config").warning(
        "Could not set a default chat model: %s", _exc
    )

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


# ── Workaround: Ctrl-C hang — reap leftover worker threads at exit ───────────
# Symptom: Ctrl-C (then 'y', or a second Ctrl-C) logs "Shutdown confirmed" and
# all the extension-shutdown messages, but the process NEVER exits; further
# Ctrl-C just prints "received signal 2, stopping" forever.
#
# Cause: jupyter_server stops by calling io_loop.stop() and ABANDONING the
# asyncio loop (pending tasks are never cancelled, the loop is never closed).
# Anything that used anyio.to_thread.run_sync() — jupyter_server's own async
# file I/O, the Jupyternaut '.env' watcher, etc. — leaves behind an idle
# "AnyIO worker thread". anyio >= 4.12 makes those threads NON-daemon and
# stops them only via a done-callback on their root task; with the loop
# abandoned, that callback never fires. Interpreter shutdown then blocks
# forever in threading._shutdown joining the thread. An unclosed
# aiosqlite.Connection (also a non-daemon Thread) hangs exit the same way.
#
# Fix: threading._register_atexit callbacks run BEFORE the interpreter joins
# non-daemon threads (the regular `atexit` module would run AFTER — too late).
# It is the same mechanism concurrent.futures uses to reap its own workers.
# Remove once jupyter_server shuts the loop down properly (or anyio reverts to
# daemon workers).
import threading as _threading


def _reap_leftover_worker_threads() -> None:
    try:
        from anyio._backends._asyncio import WorkerThread

        for _t in _threading.enumerate():
            if isinstance(_t, WorkerThread) and _t.is_alive():
                try:
                    _t.stop()  # enqueues the shutdown sentinel; thread exits
                except Exception:
                    pass
    except Exception:
        pass
    try:
        import aiosqlite

        for _t in _threading.enumerate():
            if isinstance(_t, aiosqlite.Connection) and _t.is_alive():
                try:
                    _t.stop()  # tells the connection thread's loop to finish
                except Exception:
                    pass
    except Exception:
        pass


try:
    _threading._register_atexit(_reap_leftover_worker_threads)
except Exception:  # private API: never let registration failure block startup
    pass


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
