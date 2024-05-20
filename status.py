import filecmp
import logging
import os
from typing import NamedTuple, Set


import errors
import utils


StatusTuple = tuple[str, list[str], list[str], list[str]]


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class ComparedDirectories(NamedTuple):
    match: list[str]
    mismatch: list[str]
    error: list[str]
    only_dir1: list[str]
    only_dir2: list[str]


def status() -> StatusTuple:
    try:
        base_paths = utils.get_paths()
    except errors.WitDirectoryNotFoundError:
        log.error(
            "Unable to find a wit repository in any of the parent folders of the current working directory"
            )
        return
    current_commit_info = get_current_commit_info(base_paths)
    if current_commit_info is None:
        return
    current_commit_id, current_commit_path = current_commit_info
    staging_vs_commit = compare_directories(base_paths.staging, current_commit_path)
    original_vs_staging = compare_directories(base_paths.wit_dir, base_paths.staging)
    changes_to_commit = staging_vs_commit.mismatch + staging_vs_commit.only_dir1
    changes_not_to_commit = original_vs_staging.mismatch
    untracked = original_vs_staging.only_dir1
    return current_commit_id, changes_to_commit, changes_not_to_commit, untracked


def status_message(
    commit_id: str,
    changes_to_commit: list[str],
    changes_not_to_commit: list[str],
    untracked: list[str],
) -> str:
    return (
        f"Current commit id: {commit_id}\n"
        f"Changes to be commited: {changes_to_commit}\n"
        f"Changes not staged for commit: {changes_not_to_commit}\n"
        f"Untracked: {untracked}"
    )


def get_current_commit_info(base_paths: utils.Paths) -> tuple[str, str, str, str] | None:
    log.info("Getting current HEAD commit info")
    try:
        current_commit_id = utils.get_reference_id(base_paths)
    except (errors.ReferenceFileError, errors.MissingBranchError):
        log.critical("Corrupted references file")
        return None
    current_commit_path = os.path.join(base_paths.images, current_commit_id)
    log.info("Successfully got current HEAD commit info")
    return current_commit_id, current_commit_path


def compare_directories(
    dir1: str, dir2: str
) -> ComparedDirectories:
    log.info(f"Comparing directories '{dir1}' and '{dir2}'")
    all_directories = os.walk(dir1)
    matches = []
    mismatches = []
    errors = []
    only_dir1 = []
    only_dir2 = []
    for directory in all_directories:
        subdir1, subdir2, relative_path = get_subdirs(directory, dir1, dir2)
        comparison_results = compare_directory_files(subdir1, subdir2, relative_path)
        if comparison_results:
            matches.extend(comparison_results.match)
            mismatches.extend(comparison_results.mismatch)
            errors.extend(comparison_results.error)
            only_dir1.extend(comparison_results.only_dir1)
            only_dir2.extend(comparison_results.only_dir2)
    log.info(f"Compared directories '{dir1}' and '{dir2}' successfully")
    return ComparedDirectories(
        match=matches, 
        mismatch=mismatches, 
        error=errors, 
        only_dir1=only_dir1, 
        only_dir2=only_dir2,
        )


def get_subdirs(
    dir1_walked: list[str | list[str]], dir1_path: str, dir2_path: str
) -> tuple[str, str, str]:
    log.debug(f"Getting full subdirectory paths for {dir1_walked[0]} in {dir1_path} and {dir2_path}")
    subdir1 = os.path.abspath(dir1_walked[0])
    relative_path = os.path.relpath(subdir1, dir1_path)
    subdir2 = os.path.abspath(os.path.join(dir2_path, relative_path))
    log.debug("Successfully got full subdirectory paths")
    return subdir1, subdir2, relative_path


def compare_directory_files(
    dir1: str, dir2: str, relative_path: str
) -> ComparedDirectories | None:
    log.debug(f"Comparing files between {dir1} and {dir2}")
    if not os.path.isdir(dir1):
        log.warning(f"Parameter dir1, {dir1} is not a directory path")
        return
    dir1_files = get_files_from_directory(dir1)
    log.debug(f"Got all files from {dir1}")
    if not os.path.isdir(dir2):
        log.warning(f"Parameter dir2, {dir2} is not a directory path")
        dir1_file_paths = _filename_to_path(list(dir1_files), relative_path)
        return ComparedDirectories(
        match=[],
        mismatch=[],
        error=[],
        only_dir1=dir1_file_paths,
        only_dir2=[],
    )
    dir2_files = get_files_from_directory(dir2)
    log.debug(f"Got all files from {dir2}")
    common = dir1_files & dir2_files
    comparison_results = list(filecmp.cmpfiles(dir1, dir2, common, shallow=False))
    comparison_results.append(list(dir1_files - dir2_files))
    comparison_results.append(list(dir2_files - dir1_files))
    for i, comparison_type in enumerate(comparison_results):
        comparison_results[i] = _filename_to_path(comparison_type, relative_path)
    log.debug("Finished comparing files between {dir1} and {dir2}")
    return ComparedDirectories(
        match=comparison_results[0],
        mismatch=comparison_results[1],
        error=comparison_results[2],
        only_dir1=comparison_results[3],
        only_dir2=comparison_results[4],
    )


def get_files_from_directory(directory: str) -> Set:
    log.debug(f"Getting all files in the directory {directory}")
    return {file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))}


def _filename_to_path(files: list[str], path: str) -> list[str]:
    log.debug("Getting full paths for files")
    for i, file in enumerate(files):
        files[i] = os.path.abspath(os.path.join(path, file))
    return files


def remove_from_staging(relative_file_path: str) -> None:
    log.info("Removing file from staging area")
    try:
        paths = utils.get_paths()
    except errors.WitDirectoryNotFoundError:
        log.error(
            "Unable to find a wit repository in any of the parent folders of the current working directory"
            )
        return
    file_staging_path = os.path.join(paths.staging, relative_file_path)
    try:
        os.remove(file_staging_path)
    except OSError:
        log.exception("Failed to remove file from staging area")
        return
    log.info("Successfully removed file from staging area")

