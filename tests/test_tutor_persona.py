"""
Unit tests for the Tutor persona's pure helpers (parsing, slugs, notebook
rewriting). Run from the workspace venv:

    .venv/bin/python -m unittest discover -s tests

The persona file lives in `.jupyter/personas/` (not a package), so it's loaded
by path. Importing it pulls in `jupyter_ai_persona_manager`, which is part of
the workspace deps — if those aren't installed (running outside the venv), the
whole module is skipped rather than erroring.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

PERSONA_PATH = (
    Path(__file__).resolve().parents[1]
    / ".jupyter"
    / "personas"
    / "tutor_persona.py"
)


def _load_tutor_module():
    spec = importlib.util.spec_from_file_location("tutor_persona", PERSONA_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    tutor = _load_tutor_module()
except ImportError as e:  # deps not installed — skip, don't error
    raise unittest.SkipTest(f"workspace deps not installed: {e}")


class TestStripMentions(unittest.TestCase):
    def test_single_mention(self):
        self.assertEqual(tutor.strip_mentions("@Tutor help"), "help")

    def test_multiple_mentions(self):
        self.assertEqual(tutor.strip_mentions("@Tutor @Jupyternaut hi"), "hi")

    def test_no_mention(self):
        self.assertEqual(tutor.strip_mentions("new dicts"), "new dicts")

    def test_mention_mid_text_kept(self):
        self.assertEqual(
            tutor.strip_mentions("ask @Jupyternaut instead"),
            "ask @Jupyternaut instead",
        )


class TestSlugifyTopic(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(tutor.slugify_topic("list comprehensions"), "list_comprehensions")

    def test_case_and_punctuation(self):
        self.assertEqual(tutor.slugify_topic("List Comprehensions!"), "list_comprehensions")

    def test_slashes(self):
        self.assertEqual(tutor.slugify_topic("pandas/numpy basics"), "pandas_numpy_basics")

    def test_nothing_safe_left(self):
        self.assertEqual(tutor.slugify_topic("🐍🐍🐍"), "")

    def test_truncated_to_48(self):
        self.assertEqual(len(tutor.slugify_topic("x" * 100)), 48)

    def test_separator_collapse_and_trim(self):
        self.assertEqual(tutor.slugify_topic("  __dunder   methods__  "), "dunder_methods")


class TestParseCommand(unittest.TestCase):
    def test_help_variants(self):
        for text in ("help", "?", "/help", "commands", "HELP"):
            self.assertEqual(tutor.parse_command(text)["kind"], "help", text)

    def test_list_variants(self):
        for text in ("list", "ls", "notebooks", "lessons"):
            self.assertEqual(tutor.parse_command(text)["kind"], "list", text)

    def test_new_with_multiword_topic(self):
        parsed = tutor.parse_command("new list comprehensions")
        self.assertEqual(parsed, {"kind": "new", "topic": "list comprehensions"})

    def test_new_verb_aliases(self):
        for verb in ("practice", "scaffold", "notebook"):
            parsed = tutor.parse_command(f"{verb} decorators")
            self.assertEqual(parsed, {"kind": "new", "topic": "decorators"}, verb)

    def test_new_without_topic(self):
        self.assertEqual(tutor.parse_command("new"), {"kind": "new", "topic": None})

    def test_free_form_is_chat(self):
        self.assertEqual(tutor.parse_command("explain decorators to me")["kind"], "chat")

    def test_empty_is_chat(self):
        self.assertEqual(tutor.parse_command("")["kind"], "chat")


class TestFormatListing(unittest.TestCase):
    def test_lessons_and_practice(self):
        text = tutor.format_listing(
            ["01-welcome-to-python.ipynb", "02-variables-and-data.ipynb"],
            ["practice_dicts.ipynb"],
        )
        self.assertIn("**Course lessons**", text)
        self.assertIn("- `lessons/01-welcome-to-python.ipynb`", text)
        self.assertIn("- `lessons/02-variables-and-data.ipynb`", text)
        self.assertIn("**Practice notebooks**", text)
        self.assertIn("- `practice_dicts.ipynb`", text)

    def test_lessons_only_still_hints_at_new(self):
        text = tutor.format_listing(["01-welcome-to-python.ipynb"], [])
        self.assertIn("**Course lessons**", text)
        self.assertIn("none yet", text)
        self.assertIn("`new <topic>`", text)

    def test_no_lessons_folder(self):
        text = tutor.format_listing([], [])
        self.assertNotIn("Course lessons", text)
        self.assertIn("none yet", text)


class TestResolveDest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _touch(self, name):
        (self.dir / name).write_text("{}", encoding="utf-8")

    def test_free_name_used_as_is(self):
        dest = tutor.resolve_dest(self.dir, "loops")
        self.assertEqual(dest, self.dir / "practice_loops.ipynb")

    def test_existing_name_is_kept_and_suffixed(self):
        self._touch("practice_loops.ipynb")
        dest = tutor.resolve_dest(self.dir, "loops")
        self.assertEqual(dest, self.dir / "practice_loops_2.ipynb")
        # the original is untouched (not clobbered)
        self.assertTrue((self.dir / "practice_loops.ipynb").exists())

    def test_suffix_increments_past_gaps(self):
        self._touch("practice_loops.ipynb")
        self._touch("practice_loops_2.ipynb")
        self._touch("practice_loops_3.ipynb")
        dest = tutor.resolve_dest(self.dir, "loops")
        self.assertEqual(dest, self.dir / "practice_loops_4.ipynb")


class TestSetTopic(unittest.TestCase):
    @staticmethod
    def _nb(source_lines):
        return {
            "cells": [
                {"cell_type": "markdown", "source": ["# TOPIC heading is untouched\n"]},
                {"cell_type": "code", "source": source_lines},
            ]
        }

    def test_replaces_topic_line(self):
        nb = self._nb(['TOPIC = "replace me"\n', 'print(TOPIC)\n'])
        count = tutor.set_topic(nb, "decorators")
        self.assertEqual(count, 1)
        self.assertEqual(
            nb["cells"][1]["source"][0],
            'TOPIC = "decorators"  # scaffolded by Tutor\n',
        )
        # other lines and non-code cells are untouched
        self.assertEqual(nb["cells"][1]["source"][1], "print(TOPIC)\n")
        self.assertEqual(nb["cells"][0]["source"], ["# TOPIC heading is untouched\n"])

    def test_escapes_quotes_in_topic(self):
        nb = self._nb(['TOPIC = "replace me"\n'])
        tutor.set_topic(nb, 'the "with" statement')
        self.assertEqual(
            nb["cells"][1]["source"][0],
            'TOPIC = "the \\"with\\" statement"  # scaffolded by Tutor\n',
        )

    def test_no_topic_line_returns_zero(self):
        nb = self._nb(["x = 1\n"])
        self.assertEqual(tutor.set_topic(nb, "anything"), 0)

    def test_string_source_handled(self):
        nb = {"cells": [{"cell_type": "code", "source": 'TOPIC = "replace me"\nprint(TOPIC)\n'}]}
        self.assertEqual(tutor.set_topic(nb, "generators"), 1)
        self.assertEqual(
            nb["cells"][0]["source"][0],
            'TOPIC = "generators"  # scaffolded by Tutor\n',
        )


class TestConfigManagerLookup(unittest.TestCase):
    """
    Regression: a persona's `parent` is the PersonaManager, and `serverapp`
    lives one level further up, on the PersonaManagerExtension. The lookup
    must walk the parent chain — reading `self.parent.serverapp` directly
    raises (swallowed) and made @Tutor report "no chat model is configured"
    even with a model set. `_config_manager` only touches `self.parent`, so
    it can be exercised unbound with a stand-in object chain.
    """

    @staticmethod
    def _persona_with_chain():
        sentinel = object()  # stands in for the ConfigManager
        extension = SimpleNamespace(  # PersonaManagerExtension: has serverapp
            serverapp=SimpleNamespace(
                web_app=SimpleNamespace(
                    settings={"jupyternaut.config_manager": sentinel}
                )
            ),
            parent=None,
        )
        manager = SimpleNamespace(parent=extension)  # PersonaManager: no serverapp
        return SimpleNamespace(parent=manager), sentinel

    def test_found_on_grandparent_extension(self):
        persona, sentinel = self._persona_with_chain()
        self.assertIs(tutor.TutorPersona._config_manager(persona), sentinel)

    def test_no_serverapp_anywhere_returns_none(self):
        persona = SimpleNamespace(parent=SimpleNamespace(parent=None))
        self.assertIsNone(tutor.TutorPersona._config_manager(persona))


if __name__ == "__main__":
    unittest.main()
