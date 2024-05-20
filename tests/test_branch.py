import os 
from pathlib import Path
import pytest
import shutil
import tempfile

import src
import src.utils


TEMPDIR = Path(tempfile.gettempdir())


def create_file(filepath, content):
    with open(filepath, 'w') as file:
        file.write(content)


@pytest.fixture
def testable_repository():
    test_dir = TEMPDIR / 'test_branch'
    if os.path.isdir(test_dir):
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(test_dir)
    cwd = os.getcwd()
    src.init.init()
    sample_dir = os.path.join(cwd, 'sample')
    os.makedirs(sample_dir, exist_ok=True)
    first_file = os.path.join(sample_dir, 'file1.txt')
    create_file(first_file, 'test')
    src.add.add(first_file)
    src.commit.commit('first commit')
    src.branch.branch('test_branch')
    src.checkout.checkout('test_branch')
    second_file = os.path.join(sample_dir, 'file2.txt')
    create_file(second_file, 'test')
    src.add.add(second_file)
    src.commit.commit('second commit - first on branch')
    return test_dir, first_file, second_file


def test_branch(testable_repository):
    paths = src.utils.get_paths()
    with open(paths.references, 'r') as ref_file:
        references = ref_file.read().split()
    last_branch = references[-1].partition('=')[0]
    intended_last_branch = 'test_branch'

    assert intended_last_branch == last_branch

