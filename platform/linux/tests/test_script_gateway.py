"""Developer gateway checks; these do not establish native Files support."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SETUP = Path(__file__).resolve().parents[1] / "setup_prototype.py"


class ScriptGatewayTests(unittest.TestCase):
    def test_selection_reaches_executable_without_shell_interpretation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "observer ' $ executable"
            binary.write_text(
                "#!/usr/bin/python3\n"
                "import os, sys\n"
                "with open(os.environ['OBSERVER_RESULT'], 'wb') as result:\n"
                "    result.write(b'\\0'.join([os.getcwdb()] + "
                "[os.fsencode(arg) for arg in sys.argv[1:]]))\n"
            )
            binary.chmod(0o700)
            scripts = root / "scripts"
            subprocess.run(
                [sys.executable, SETUP, "install", "--binary", binary,
                 "--scripts-dir", scripts], check=True, capture_output=True,
            )
            result = root / "result"
            selections = [b"two words.png", "雪.png".encode(), b"$(touch PWNED)",
                          b"quote'\".png", b"-option", b"line\nbreak", b"raw-\xff"]
            subprocess.run(
                [os.fsencode(scripts / "FileShift Prototype"), *selections],
                cwd=root, env={**os.environ, "OBSERVER_RESULT": str(result)}, check=True,
            )
            self.assertEqual(result.read_bytes().split(b"\0"),
                             [os.fsencode(root), b"--nautilus-script", b"--", *selections])
            self.assertFalse((root / "PWNED").exists())

    def test_setup_preserves_existing_scripts_and_removes_only_its_own_script(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command = [sys.executable, SETUP, "install", "--binary", "/bin/true",
                       "--scripts-dir", root]
            script = root / "FileShift Prototype"
            subprocess.run(command, check=True, capture_output=True)
            original = script.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(script.read_bytes(), original)
            command[2] = "remove"
            script.write_text("user-owned replacement\n")
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(script.read_text(), "user-owned replacement\n")
            script.write_bytes(original)
            subprocess.run(command, check=True, capture_output=True)
            self.assertFalse(script.exists())


if __name__ == "__main__":
    unittest.main()
