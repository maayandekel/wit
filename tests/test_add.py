import os
from pathlib import Path
import pytest
import shutil


from src import add


class TestAdd:
    PROJECTFILEDIR = Path(__file__).parent.resolve().parent.resolve()
    SOURCEPATH = PROJECTFILEDIR / 'samples' / 'test'

    def test_add(self, init_wit):
        self.tempdir = init_wit
        self.test_files = self.tempdir / 'test'
        shutil.copytree(TestAdd.SOURCEPATH, self.test_files, dirs_exist_ok=True)
        add.add(self.test_files)
        intended_files = os.listdir(self.test_files)
        staging_files = os.listdir(self.tempdir / '.wit' / 'staging_area' / 'test')

        assert intended_files == staging_files