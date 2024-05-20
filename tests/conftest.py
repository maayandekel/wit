import os
from pathlib import Path
import pytest
import shutil
import tempfile

import src
import src.add
import src.branch
import src.checkout
import src.commit


TEMPDIR = Path(tempfile.gettempdir())


@pytest.fixture
def init_wit():
    test_dir = TEMPDIR / 'test_dir'
    test_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(test_dir)
    src.init.init()
    return test_dir
