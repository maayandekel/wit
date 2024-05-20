import logging
import os

import utils


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def create_activated(active_path: str) -> bool:
    try:
        with open(active_path, 'w') as active_file:
            active_file.write('master')
    except OSError:
        log.exception("init: Can't create activated file")
        return False
    return True


def init():
    log.info("Creating the base directories")
    creation_path = os.getcwd()
    paths = utils.get_paths(path=creation_path, wit_exist=False)
    initial_paths = (paths.wit, paths.images, paths.staging)
    for folder in initial_paths:
        log.debug(f"Creating {folder}")
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError:
            log.exception(f"init: Can't create the folder {folder}")
            return False
    if not create_activated(paths.active):
        return False
    log.info("Base directories created successfully")
    return True