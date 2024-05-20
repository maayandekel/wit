import os
from pathlib import Path
import pytest
import tempfile

from src import init


TEMPDIR = Path(tempfile.gettempdir())

class TestInit:
    def setup_method(self):
        self.test_dir = TEMPDIR / 'test_init'
        self.test_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(self.test_dir)

    def test_file_creation(self):
        init.init()
        post_init_files = os.listdir(self.test_dir)

        assert '.wit' in post_init_files

        test_wit_dir = self.test_dir / '.wit'
        wit_files = set(os.listdir(test_wit_dir))
        intended_wit_files = {'images', 'staging_area', 'activated.txt'}

        assert wit_files == intended_wit_files
    