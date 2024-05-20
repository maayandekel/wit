import os
from pathlib import Path
import tempfile

import src
import src.utils

class TestUtils:
    COMMIT_ID = 'xxx'
    TEMPDIR = Path(tempfile.gettempdir())

    def setup_method(self):
        self.test_dir = TestUtils.TEMPDIR / 'test_utils'
        self.test_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(self.test_dir)
        src.init.init()

    def test_get_paths_with_wit(self, init_wit):
        cwd = os.getcwd()
        intended_paths = src.utils.Paths(
            cwd = cwd,
            wit = os.path.join(cwd, '.wit'),
            wit_dir = cwd,
            images = os.path.join(cwd, '.wit', 'images'),
            staging = os.path.join(cwd, '.wit', 'staging_area'),
            active = os.path.join(cwd, '.wit', 'activated.txt'),
            references = os.path.join(cwd, '.wit', 'references.txt'),
        )
        utils_paths = src.utils.get_paths()

        assert intended_paths == utils_paths

    def test_update_with_create(self, init_wit):
        paths = src.utils.get_paths()
        if os.path.isfile(paths.references):
            os.remove(paths.references)
        assert not os.path.isfile(paths.references)
        src.utils.update_references(paths, TestUtils.COMMIT_ID, 'new_branch')

        intended_content = (
            f'HEAD={TestUtils.COMMIT_ID}\nmaster={TestUtils.COMMIT_ID}\nnew_branch={TestUtils.COMMIT_ID}\n'
        )
        with open(paths.references, 'r') as references:
            references_content = references.read()

        assert intended_content == references_content

    def test_get_reference_id(self, init_wit):
        paths = src.utils.get_paths()
        reference_id = src.utils.get_reference_id(paths, 'master')
        assert TestUtils.COMMIT_ID == reference_id

    