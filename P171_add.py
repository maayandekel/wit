# Upload 171


import os
import shutil


class WitDirectoryNotFoundError(Exception):
    def __init__(self, original_full_path: str):
        self.given_path = original_full_path

    def __str__(self) -> str:
        return f"No wit directory found in any directory in the full path: {self.given_path}"


def get_directory_path(full_path: str) -> str:
    if os.path.isfile(full_path):
        return os.path.dirname(full_path)
    return full_path


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


def find_staging_area_path(original_full_path: str) -> str:
    directory_path = get_directory_path(original_full_path)
    wit_path = get_wit_path(directory_path)
    wit_dir_path = os.path.dirname(wit_path)
    if wit_dir_path == directory_path:
        return os.path.join(wit_path, "staging_area")
    relative_path = os.path.relpath(directory_path, wit_dir_path)
    return os.path.join(wit_path, "staging_area", relative_path)


def copy_file(source_path: str, destination_path: str) -> None:
    create_path(os.path.dirname(destination_path))
    shutil.copy(source_path, destination_path)


def copy_path(source_path: str, destination_path: str, wit_path: str) -> None:
    if os.path.isfile(source_path):
        copy_file(source_path, destination_path)
        return
    for item in os.listdir(source_path):
        source_item_path = os.path.join(source_path, item)
        destination_item_path = os.path.join(destination_path, item)
        if os.path.isdir(source_item_path) and source_item_path != wit_path:
            copy_path(source_item_path, destination_item_path, wit_path)
        if os.path.isfile(source_item_path):
            copy_file(source_item_path, destination_item_path)


def create_path(destination_path: str) -> None:
    os.makedirs(destination_path, exist_ok=True)


def add(item_to_add: str) -> None:
    full_path_item = os.path.abspath(os.path.expanduser(item_to_add))
    wit_path = find_staging_area_path(full_path_item)
    copy_path(full_path_item, wit_path, os.path.dirname(wit_path))

# add(r'C:\Python Course\week10\Problem sets\test')