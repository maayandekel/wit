import os
from pathlib import Path
import shutil
import tempfile

import src
import src.status
import src.utils


TEMPDIR = Path(tempfile.gettempdir())


class TestStatus:
    def setup_method(self):
        self.test_dir = TEMPDIR / 'test_status'
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)
        os.chdir(self.test_dir)
        cwd = os.getcwd()
        src.init.init()
        self.sample_dir = os.path.join(cwd, 'sample')
        os.makedirs(self.sample_dir)
        self.unchanged_file = os.path.join(self.sample_dir, 'file0.txt')
        with open(self.unchanged_file, 'w') as file:
            file.write('test')
        self.changed_file = os.path.join(self.sample_dir, 'file1.txt')
        with open(self.changed_file, 'w') as file:
            file.write('test')
        src.add.add(self.unchanged_file)
        src.add.add(self.changed_file)
        src.commit.commit('first commit')
        with open(self.changed_file, 'w') as file:
            file.write('changed')
        self.new_file = os.path.join(self.sample_dir, 'file2.txt')
        with open(self.new_file, 'w') as file:
            file.write('test')
        src.add.add(self.new_file)
        self.untracked_file = os.path.join(self.sample_dir, 'file3.txt')
        with open(self.untracked_file, 'w') as file:
            file.write('test')
        paths = src.utils.get_paths()
        self.current_id = src.utils.get_reference_id(paths)

    def test_status(self):
        intended_to_commit = [self.new_file]
        intended_not_staged = [self.changed_file]
        intended_untracked = [self.untracked_file]
        intended_status_message = (
            f"Current commit id: {self.current_id}\n"
            f"Changes to be commited: {intended_to_commit}\n"
            f"Changes not staged for commit: {intended_not_staged}\n"
            f"Untracked: {intended_untracked}"
        )
        current_status = src.status.status()
        status_message = src.status.status_message(*current_status)

        assert intended_status_message == status_message