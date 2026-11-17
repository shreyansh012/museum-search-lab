"""Command line checks: bad --limit is refused, odd characters do not crash."""

import os
import subprocess
import sys
import unittest

from tests import helpers


def run_cli(*args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, "-m", "museum_search", *args],
                          cwd=helpers.ROOT, capture_output=True, env=env, timeout=60)


class LimitTests(unittest.TestCase):
    def test_zero_limit_is_refused(self):
        proc = run_cli("search", "silk", "--limit", "0")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--limit must be at least 1", proc.stderr.decode("utf-8", "replace"))

    def test_negative_limit_is_refused(self):
        proc = run_cli("search", "silk", "--limit", "-1")
        self.assertEqual(proc.returncode, 2)


class NarrowConsoleTests(unittest.TestCase):
    def test_all_results_print_with_a_narrow_console_setting(self):
        proc = run_cli("search", "portrait", "--limit", "400",
                       env_extra={"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"})
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()
