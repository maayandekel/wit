import os
from pathlib import Path
import pytest
import shutil


from src import commit, utils


class TestCommit:

    def test_commit(self, init_wit):
        commit.commit('testing_commit')
        paths = utils.get_paths(init_wit)
        commit_id = utils.get_reference_id(paths)
        intended_files = [directory_result[1:] for directory_result in os.walk(paths.staging)]
        commit_files = [directory_result[1:] for directory_result in os.walk(os.path.join(paths.images, commit_id))]

        assert intended_files == commit_files

    def test_remove_commit_folder(self, init_wit):
        paths = utils.get_paths()
        if os.path.isfile(paths.references):
            os.remove(paths.references)
        assert not os.path.isfile(paths.references)
        commit_id = commit.create_commit_folder(paths)
        assert os.path.isdir(os.path.join(paths.images, commit_id))
        commit.remove_commit_folder(paths, commit_id)
        assert not os.path.isdir(os.path.join(paths.images, commit_id))



