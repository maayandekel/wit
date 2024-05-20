import logging
import os
import shutil

import errors
import utils
import status


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def replace_file(source_path: str, destination_path: str) -> None:
    log.debug("Copying file {source_path} from source path into destination path, replacing if needed")
    utils.create_path(os.path.dirname(destination_path))
    if os.path.isfile(destination_path):
        os.remove(destination_path)
    shutil.copy(source_path, destination_path)
    log.debug("File copy successful")


def export_files(
    source_path: str,
    destination_path: str,
    untracked_files: list[str],
    source_files: list[str],
) -> None:
    log.debug(f"Moving files and replacing folders from {source_path} to {destination_path}")
    for file in source_files:
        source_file_path = os.path.join(source_path, file)
        destination_file_path = os.path.join(destination_path, file)
        if os.path.isdir(source_file_path) and destination_file_path not in untracked_files:
            replace_path(source_file_path, destination_file_path, untracked_files)
        if os.path.isfile(source_file_path) and destination_file_path not in untracked_files:
            replace_file(source_file_path, destination_file_path)


def clear_destination(
    destination_path: str,
    untracked_items: list[str],
    source_items: list[str],
    destination_items: list[str],
) -> None:
    log.debug("Clearing destination path of tracked items that aren't in the source items")
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
    log.info(
        f"Replacing the content of the destination path {destination_path} "
        f"with the content of the source path {source_path}, "
        "ignoring untracked items"
    )
    if untracked_items is None:
        untracked_items = []
    source_files = os.listdir(source_path)
    export_files(source_path, destination_path, untracked_items, source_files)
    destination_items = os.listdir(destination_path)
    clear_destination(
        destination_path, untracked_items, source_files, destination_items
    )


def get_commit_ids(paths: utils.Paths, commit_name: str) -> tuple[str, str] | None:
    log.debug("Getting commit id from branch name or id")
    if len(commit_name) == 40:
        return commit_name
    try:
        return utils.get_reference_id(paths, commit_name)
    except errors.ReferenceFileError:
        log.critical("Corrupted references file")
        return 
    except errors.MissingBranchError:
        log.exception("Unable to retrieve the branch commit id as branch not found")
        return 


def get_checkout_commit_info(paths: utils.Paths, commit_name: str) -> tuple[str, str] | None:
    log.info("Getting commit id and path")
    commit_id = get_commit_ids(paths, commit_name)
    if commit_id is None:
        log.error("Failed to get commit id and path")
        return
    source_image_path = os.path.join(paths.images, commit_id)
    log.info("Got commit id and path")
    return source_image_path, commit_id


def get_checkout_status(main_path: str) -> list[str]:
    log.info("Getting the current repository untracked items")
    UNCOMITTED_CHANGES = 1
    UNSTAGED_CHANGES = 2
    UNTRACKED = 3
    status_results = status.status()
    if len(status_results[UNCOMITTED_CHANGES]) != 0:
        raise errors.StatusNotResolvedError(UNCOMITTED_CHANGES)
    if len(status_results[UNSTAGED_CHANGES]) != 0:
        raise errors.StatusNotResolvedError(UNSTAGED_CHANGES)
    return status_results[UNTRACKED]


def update_active_branch(active_path: str, branch_name: str) -> None:
    log.info(f"Updating the active branch to {branch_name}")
    with open(active_path, "w") as active_file:
        active_file.write(branch_name)
    log.info("Finished updating the active branch")


def checkout(commit_name: str) -> None:
    try:
        paths = utils.get_paths()
    except errors.WitDirectoryNotFoundError:
        log.error(
            "Unable to find a wit repository in any of the parent folders of the given item path, {directory_path}"
            )
        return
    commit_info = get_checkout_commit_info(paths, commit_name)
    if commit_info is None:
        return
    source_image_path, commit_id = commit_info
    try:
        untracked_items = get_checkout_status(paths.wit_dir)
    except errors.StatusNotResolvedError:
        log.exception("Unresolved status - cannot perform checkout")
        return
    log.info("Untracked items retrieval successful")
    replace_path(source_image_path, paths.wit_dir, untracked_items)
    replace_path(source_image_path, paths.staging)
    if len(commit_name) == 40:
        commit_name = 'None'
    if not utils.update_references(paths, commit_id, commit_name):
        log.critical("Unable to update references.txt after performing checkout")
        return
    update_active_branch(paths.active, commit_name)

