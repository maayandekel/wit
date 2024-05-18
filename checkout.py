import os
import shutil
import sys


import P171_add as add
import P172_commit as commit
import P173_status as status


class StatusNotResolvedError(Exception):
    STATUS_ISSUE = {1: "changes to be commited", 2: "changes not staged for commit"}

    def __init__(self, status_type):
        self.status_problem = StatusNotResolvedError.STATUS_ISSUE[status_type]

    def __str__(self) -> str:
        return f"The current status is unresolved. There are {self.status_problem}"


def replace_file(source_path: str, destination_path: str) -> None:
    add.create_path(os.path.dirname(destination_path))
    if os.path.isfile(destination_path):
        os.remove(destination_path)
    shutil.copy(source_path, destination_path)


def export_items(
    source_path: str,
    destination_path: str,
    untracked_items: list[str],
    source_items: list[str],
) -> None:
    for item in source_items:
        source_item_path = os.path.join(source_path, item)
        destination_item_path = os.path.join(destination_path, item)
        if os.path.isdir(source_item_path) and source_item_path not in untracked_items:
            replace_path(source_item_path, destination_item_path, untracked_items)
        if os.path.isfile(source_item_path) and source_item_path not in untracked_items:
            replace_file(source_item_path, destination_item_path)


def clear_destination(
    source_path: str,
    destination_path: str,
    untracked_items: list[str],
    source_items: list[str],
    destination_items: list[str],
) -> None:
    for item in destination_items:
        destination_item_path = os.path.join(destination_path, item)
        if item not in source_items and destination_item_path not in untracked_items:
            if os.path.isfile(destination_item_path):
                os.remove(destination_item_path)
            if (
                os.path.isdir(destination_item_path)
                and os.listdir(destination_item_path) == []
            ):
                os.rmdir(destination_item_path)


def replace_path(
    source_path: str, destination_path: str, untracked_items: list[str] | None = None
) -> None:
    if untracked_items is None:
        untracked_items = []
    source_items = os.listdir(source_path)
    export_items(source_path, destination_path, untracked_items, source_items)
    destination_items = os.listdir(destination_path)
    clear_destination(
        source_path, destination_path, untracked_items, source_items, destination_items
    )


def get_commit_ids(references_path: str, commit_name: str) -> tuple[str, str]:
    if len(commit_name) == 40:
        return commit_name
    return commit.get_reference_id(references_path, commit_name)


def get_checkout_paths_and_ids(commit_name: str) -> tuple[str, str, str, str, str, str]:
    wit_path = add.get_wit_path(os.getcwd())
    main_path = os.path.dirname(wit_path)
    references_path = os.path.join(wit_path, "references.txt")
    commit_id = get_commit_ids(references_path, commit_name)
    source_image_path = os.path.join(wit_path, "images", commit_id)
    staging_path = os.path.join(wit_path, "staging_area")
    active_path = os.path.join(wit_path, "activated.txt")
    return (
        main_path,
        source_image_path,
        staging_path,
        references_path,
        commit_id,
        active_path,
    )


def get_checkout_status(main_path: str) -> list[str]:
    status_results = status.status()
    if len(status_results[1]) != 0:
        raise StatusNotResolvedError(1)
    if len(status_results[2]) != 0:
        raise StatusNotResolvedError(2)
    return [os.path.join(main_path, item) for item in status_results[3]]


def update_active_branch(active_path: str, branch_name: str) -> None:
    with open(active_path, "w") as active_file:
        active_file.write(branch_name)


def checkout(commit_name: str) -> None:
    (
        main_path,
        source_image_path,
        staging_path,
        references_path,
        commit_id,
        active_path,
    ) = get_checkout_paths_and_ids(commit_name)
    untracked_items = get_checkout_status(main_path)
    replace_path(source_image_path, main_path, untracked_items)
    replace_path(source_image_path, staging_path)
    if len(commit_name) == 40:
        commit_name = 'None'
    commit.update_references(references_path, commit_id, commit_name)
    update_active_branch(active_path, commit_name)


if len(sys.argv) >= 3:
    if sys.argv[1] == "check_out":
        checkout(sys.argv[2])


# checkout('master')
