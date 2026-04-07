import os
import stat
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAlphaLabAssets(unittest.TestCase):
    def test_alpha_lab_entry_points_exist(self):
        expected = [
            os.path.join(REPO_ROOT, "examples", "lab_01_first_flight.py"),
            os.path.join(REPO_ROOT, "examples", "lab_square_path.py"),
            os.path.join(REPO_ROOT, "examples", "lab_03_stop_before_wall.py"),
            os.path.join(REPO_ROOT, "examples", "run_alpha_labs.py"),
        ]
        for path in expected:
            self.assertTrue(os.path.exists(path), msg=f"Missing alpha lab file: {path}")

    def test_quickstart_uses_current_repo_commands(self):
        quickstart_path = os.path.join(REPO_ROOT, "docs", "STUDENT_QUICKSTART_ALPHA.md")
        with open(quickstart_path) as f:
            content = f.read()

        self.assertIn("python3 examples/lab_01_first_flight.py", content)
        self.assertIn("python3 examples/lab_square_path.py", content)
        self.assertIn("python3 examples/lab_03_stop_before_wall.py", content)
        self.assertIn("python3 examples/run_alpha_labs.py", content)
        self.assertIn("tools/run_alpha_regression.sh", content)

    def test_regression_runner_is_executable(self):
        runner_path = os.path.join(REPO_ROOT, "tools", "run_alpha_regression.sh")
        with open(runner_path) as f:
            content = f.read()

        self.assertIn("python3 -m unittest discover", content)
        self.assertTrue(os.stat(runner_path).st_mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
