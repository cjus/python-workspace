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
import unittest
from pathlib import Path

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
        for text in ("list", "ls", "notebooks"):
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


if __name__ == "__main__":
    unittest.main()
