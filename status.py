# Upload 173


import collections
import filecmp
import os
import sys
from typing import Set


import P171_add as add
import P172_commit as commit


StatusTuple = tuple[str, list[str], list[str], list[str]]


class ReferenceFileError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"The reference file found is improperly formatted. {self.message}"


# This is the same class I submitted with problem #171 Add:
class WitDirectoryNotFoundError(Exception):
    def __init__(self, original_full_path: str):
        self.given_path = original_full_path

    def __str__(self) -> str:
        return f"No wit directory found in any directory in the full path: {self.given_path}"


# This function is almost the same one I submitted in problem #172 commit, added line before while:
def get_wit_path(path: str) -> str:
    current_wit_path = os.path.join(path, ".wit")
    while os.path.dirname(path) != path:
        current_wit_path = os.path.join(path, ".wit")
        if os.path.isdir(current_wit_path):
            return current_wit_path
        path = os.path.dirname(path)
    if os.path.isdir(current_wit_path):
        return current_wit_path
    raise WitDirectoryNotFoundError(path)


def status() -> StatusTuple:
    compare_results = collections.namedtuple(
        "compare_results", ["match", "mismatch", "error", "only_dir1", "only_dir2"]
    )
    current_commit_id, last_commit_path, staging_path, original_path = (
        prepare_status_paths()
    )
    staging_vs_commit = compare_results(
        *compare_directories(staging_path, last_commit_path),
    )
    original_vs_staging = compare_results(
        *compare_directories(original_path, staging_path),
    )
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


def prepare_status_paths() -> tuple[str, str, str, str]:
    wit_path = add.get_wit_path(os.getcwd())
    references_path = os.path.join(wit_path, "references.txt")
    current_commit_id = commit.get_reference_id(references_path)
    last_commit_path = os.path.join(wit_path, "images", current_commit_id)
    staging_path = os.path.join(wit_path, "staging_area")
    original_path = os.path.dirname(wit_path)
    return current_commit_id, last_commit_path, staging_path, original_path


def compare_directories(
    dir1: str, dir2: str
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
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
            match, mismatch, error, only_subdir1, only_subdir2 = comparison_results
            matches.extend(match)
            mismatches.extend(mismatch)
            errors.extend(error)
            only_dir1.extend(only_subdir1)
            only_dir2.extend(only_subdir2)
    return matches, mismatches, errors, only_dir1, only_dir2


def get_subdirs(
    dir1_walked: list[str | list[str]], dir1_path: str, dir2_path: str
) -> tuple[str, str, str]:
    subdir1 = os.path.abspath(dir1_walked[0])
    relative_path = os.path.relpath(subdir1, dir1_path)
    if relative_path != ".":
        subdir2 = os.path.join(dir2_path, relative_path)
    else:
        subdir2 = dir2_path
        relative_path = ""
    return subdir1, subdir2, relative_path


def get_files_from_directory(directory: str) -> Set:
    return {file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))}


def _filename_to_path(files: list[str], path: str) -> list[str]:
    for i, file in enumerate(files):
        files[i] = os.path.join(path, file)
    return files


def compare_directory_files(
    dir1: str, dir2: str, relative_path: str
) -> list[list[str]] | None:
    if not os.path.isdir(dir2):
        return
    dir1_files = get_files_from_directory(dir1)
    dir2_files = get_files_from_directory(dir2)
    common = dir1_files & dir2_files
    comparison_results = list(filecmp.cmpfiles(dir1, dir2, common, shallow=False))
    comparison_results.append(list(dir1_files - dir2_files))
    comparison_results.append(list(dir2_files - dir1_files))
    for comparison_type in comparison_results:
        comparison_type = _filename_to_path(comparison_type, relative_path)
    return comparison_results


def remove_from_staging(relative_file_path: str) -> None:
    wit_path = get_wit_path(os.getcwd())
    file_staging_path = os.path.join(wit_path, "staging_area", relative_file_path)
    os.remove(file_staging_path)


if len(sys.argv) >= 2:
    if sys.argv[1] == "status":
        current_status = status()
        print(status_message(*current_status))


# print(status())
