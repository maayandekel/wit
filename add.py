import logging
import os
import shutil

import errors
import utils

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def get_directory_path(full_path: str) -> str:
    log.info("Getting the directory path")
    if os.path.isfile(full_path):
        return os.path.dirname(full_path)
    return full_path


def find_staging_area_path(directory_path: str, paths: utils.Paths) -> str:
    log.info("Finding the directory in the staging area")
    if paths.wit_dir == directory_path:
        return paths.staging
    relative_path = os.path.relpath(directory_path, paths.wit_dir)
    return os.path.join(paths.staging, relative_path)


def copy_file(source_path: str, destination_path: str) -> None:
    utils.create_path(os.path.dirname(destination_path))
    shutil.copy(source_path, destination_path)
    log.debug(f"Copying file {source_path} succeeded")


def copy_path(source_path: str, destination_path: str, wit_path: str) -> None:
    if os.path.isfile(source_path):
        log.debug(f"Copying the file {source_path}")
        copy_file(source_path, destination_path)
        log.info("Successfully finished copying into the staging area")
        return
    for item in os.listdir(source_path):
        source_item_path = os.path.join(source_path, item)
        destination_item_path = os.path.join(destination_path, item)
        if os.path.isdir(source_item_path): #and source_item_path != wit_path:
            log.debug(f"Copying all files in {source_item_path}")
            copy_path(source_item_path, destination_item_path, wit_path)
        if os.path.isfile(source_item_path):
            log.debug(f"Copying the file {source_item_path}")
            copy_file(source_item_path, destination_item_path)
    log.info("Successfully finished copying into the staging area")


def add(item_to_add: str) -> None:
    full_path_item = os.path.abspath(os.path.expanduser(item_to_add))
    directory_path = get_directory_path(full_path_item)
    try:
        paths = utils.get_paths(directory_path)
    except errors.WitDirectoryNotFoundError:
        log.error(
            "Unable to find a wit repository in any of the parent folders of the given item path, {directory_path}"
            )
        return
    destination_path = find_staging_area_path(directory_path, paths)
    log.info("Copying the source file(s) and folder(s) into the staging area")
    try:
        copy_path(full_path_item, destination_path, os.path.dirname(destination_path))
    except OSError as err:
        log.exception("Copying of at least one file failed.")
        raise err
