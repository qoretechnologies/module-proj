#!/usr/bin/python3
# Copyright (C) 2026 Qore Technologies, s.r.o.
# SPDX-License-Identifier: MIT
"""Verify uninstall handles staged paths and removes only manifest files."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class UninstallTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='proj uninstall ')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        template = (Path(__file__).resolve().parents[1] / 'cmake/cmake_uninstall.cmake.in').read_text()
        self.script = self.root / 'uninstall.cmake'
        self.script.write_text(template.replace('@CMAKE_CURRENT_BINARY_DIR@', str(self.root))
                               .replace('@CMAKE_COMMAND@', shutil.which('cmake')))

    def run_uninstall(self, destdir=''):
        return subprocess.run(['cmake', '-P', str(self.script)], capture_output=True, text=True,
                              env={**os.environ, 'DESTDIR': destdir})

    def test_staged_files_spaces_and_dangling_symlinks(self):
        stage = self.root / 'stage'
        directory = stage / 'usr/share/qore with spaces'
        directory.mkdir(parents=True)
        installed = directory / 'installed file'
        installed.write_text('installed')
        link = directory / 'dangling link'
        link.symlink_to(directory / 'nonexistent')
        retained = directory / 'unrelated file'
        retained.write_text('preserve')
        (self.root / 'install_manifest.txt').write_text('\n'.join(
            '/' + str(p.relative_to(stage)) for p in [installed, link, directory / 'already removed']) + '\n')
        result = self.run_uninstall(str(stage))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(installed.exists())
        self.assertFalse(link.is_symlink())
        self.assertEqual('preserve', retained.read_text())
        self.assertEqual(0, self.run_uninstall(str(stage)).returncode)

    def test_missing_manifest_fails(self):
        result = self.run_uninstall()
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Cannot find install manifest', result.stderr)

    def test_directory_is_preserved(self):
        directory = self.root / 'directory'
        directory.mkdir()
        (self.root / 'install_manifest.txt').write_text(str(directory) + '\n')
        result = self.run_uninstall()
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Refusing to remove a directory', result.stderr)
        self.assertTrue(directory.is_dir())

    def test_directory_symlink_preserves_its_target(self):
        directory = self.root / 'directory'
        directory.mkdir()
        content = directory / 'keep'
        content.write_text('preserve')
        link = self.root / 'directory link'
        link.symlink_to(directory, target_is_directory=True)
        (self.root / 'install_manifest.txt').write_text(str(link) + '\n')
        result = self.run_uninstall()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(link.is_symlink())
        self.assertEqual('preserve', content.read_text())

    def test_empty_manifest_preserves_other_files(self):
        retained = self.root / 'keep'
        retained.write_text('preserve')
        (self.root / 'install_manifest.txt').write_text('')
        result = self.run_uninstall()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('preserve', retained.read_text())

    def test_removal_failure_is_reported(self):
        installed = self.root / 'installed'
        installed.write_text('preserve on failure')
        (self.root / 'install_manifest.txt').write_text(str(installed) + '\n')
        command = '"' + shutil.which('cmake') + '" -E remove'
        script = self.script.read_text()
        self.assertIn(command, script)
        self.script.write_text(script.replace(command, '"' + shutil.which('false') + '" -E remove'))
        result = self.run_uninstall()
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Cannot remove installed file', result.stderr)
        self.assertEqual('preserve on failure', installed.read_text())


if __name__ == '__main__':
    unittest.main()
