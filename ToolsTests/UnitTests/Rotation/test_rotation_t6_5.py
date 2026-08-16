#!/usr/bin/env python3
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
"""Suite di test di non-regressione per la rotazione history (Task T6.5)."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CleanTestResult(unittest.TextTestResult):
    """ResultClass per formattare l'output di esecuzione dei test senza ridondanze."""

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        method = getattr(test, test._testMethodName)
        doc = method.__doc__.strip() if method.__doc__ else "Nessuna descrizione"
        self.stream.writeln(f"[TEST EXECUTION] {test._testMethodName}")
        self.stream.writeln(f"                 └─ {doc}")
        self.stream.flush()

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)


def discover_utility_root(start: Path) -> Path:
    """Risale l'albero delle cartelle per individuare la directory .catsw-utility live."""
    for candidate in (start, *start.parents):
        target = candidate / ".catsw-utility"
        if target.is_dir():
            return target
    raise RuntimeError(f"Impossibile trovare .catsw-utility risalendo da {start}")


class TestRotationT65(unittest.TestCase):

    def setUp(self):
        # 1. Individuazione dinamica della cartella .catsw-utility reale
        self.live_utility = discover_utility_root(Path(__file__).resolve())
        self.repo_root = self.live_utility.parent

        # 2. Creazione sandbox di test isolata
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_rotation_"))
        self.utility_root = self.test_dir / ".catsw-utility"
        self.artefacts_dir = self.utility_root / "artifacts"
        self.temp_dir = self.utility_root / "temp"
        self.history_dir = self.utility_root / "history"

        # 3. Copia gli artefatti attuali dalla repository nella sandbox
        shutil.copytree(self.live_utility, self.utility_root, dirs_exist_ok=True)

        # 4. Bonifica totale della sandbox: svuota history, temp e rimuove file sfusi non .cmd dalla root
        if self.history_dir.exists():
            shutil.rmtree(self.history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        for item in self.utility_root.iterdir():
            if item.is_file() and item.suffix.lower() != ".cmd":
                item.unlink()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _run_cmd(self, cmd_path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["cmd.exe", "/c", str(cmd_path)],
            cwd=self.utility_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_direct_python_rotation_logic(self):
        """Verifica la rotazione file di root/temp e la gestione suffissi anti-collisione."""
        (self.utility_root / "context-request-test.md").write_text("req", encoding="utf-8")
        (self.temp_dir / "stale.py").write_text("print('old')", encoding="utf-8")
        (self.utility_root / "unrelated.txt").write_text("keep", encoding="utf-8")

        script = self.artefacts_dir / "move-to-history.py"
        res = subprocess.run(
            [sys.executable, str(script)],
            cwd=self.utility_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(res.returncode, 0)

        history_files = [f.name for f in self.history_dir.iterdir()]
        self.assertEqual(len(history_files), 2, f"File inattesi trovati in history: {history_files}")
        self.assertTrue((self.utility_root / "unrelated.txt").exists())

    def test_move_to_history_cmd_wrapper(self):
        """Verifica l'esecuzione standalone del wrapper move-to-history.cmd."""
        (self.utility_root / "context-request-cmd.md").write_text("data", encoding="utf-8")
        cmd_script = self.utility_root / "move-to-history.cmd"

        res = self._run_cmd(cmd_script)
        self.assertEqual(res.returncode, 0)

        history_files = [f.name for f in self.history_dir.iterdir()]
        self.assertEqual(len(history_files), 1, f"File inattesi trovati in history: {history_files}")

    def test_no_duplicate_rotation_calls_in_python_sources(self):
        """Verifica l'assenza di chiamate interne duplicate a move-to-history nei sorgenti Python."""
        startup_py = (self.artefacts_dir / "startup-llm-session.py").read_text(encoding="utf-8")
        process_py = (self.artefacts_dir / "process-from-llm.py").read_text(encoding="utf-8")

        self.assertNotIn('subprocess.run(["python", "move-to-history.py"]', startup_py)
        self.assertNotIn('move_script = ARTEFACTS_ROOT / "move-to-history.py"', process_py)


if __name__ == "__main__":
    runner = unittest.TextTestRunner(resultclass=CleanTestResult, verbosity=1)
    unittest.main(testRunner=runner)