import datetime
import logging
import os
import random
import shutil
import string

import utils
import errors

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def remove_commit_folder(paths: utils.Paths, commit_id: str) -> None:
    log.info(f"Removing commit folder {commit_id} due to previous error")
    commit_path = os.path.join(paths.images, commit_id)
    try:
        shutil.rmtree(commit_path)
    except OSError:
        log.error(f"Unable to remove the problematic commit folder, commit id {commit_id}")
        return
    log.info(f"Successfully removed the commit folder {commit_id}")


def create_commit_id() -> str:
    log.info("Creating new commit id")
    return "".join(random.choice(string.hexdigits) for _ in range(40))


def create_commit_folder(paths: utils.Paths) -> str:
    log.info("Creating new commit folder")
    commit_id = create_commit_id()
    log.info("New commit id created")
    commit_path = os.path.join(paths.images, commit_id)
    log.debug("Copying content into new commit folder")
    try:
        shutil.copytree(paths.staging, commit_path)
    except OSError:
        log.exception("Copying staging area content into new commit folder failed.")
        if os.path.isdir(commit_path):
            log.info("Removing new commit folder as copying failed")
            remove_commit_folder(paths, commit_id)
        return
    log.info("Copying staging area content into new commit folder successful")
    return commit_id


def create_commit_meta_data(paths: utils.Paths, commit_id: str, message: str) -> bool:
    log.info("Creating new commit meta data file")
    creation_time = datetime.datetime.now()
    formatted_creation_time = creation_time.strftime("%a %b %d %H:%M:%S %Y %z")
    try:
        parent = utils.get_reference_id(paths)
    except errors.ReferenceFileError:
        log.critical("Corrupted references file")
        remove_commit_folder(paths, commit_id)
        return False
    except errors.MissingBranchError:
        log.exception("Unable to retrieve the parent commit id as branch not found")
        remove_commit_folder(paths, commit_id)
        return False
    message = (
        f"parent={parent}\n" f"date={formatted_creation_time}\n" f"message={message}\n"
    )
    commit_file_path = os.path.join(paths.images, f"{commit_id}.txt")
    try:
        with open(commit_file_path, "w") as commit_file:
            commit_file.write(message)
    except OSError:
        log.exception("Unable to create commit metadata file")
        remove_commit_folder(paths, commit_id)
        return False
    return True


def get_active_branch(paths: utils.Paths) -> str | None:
    try:
        with open(paths.active, "r") as active_file:
            return active_file.read()
    except OSError:
        log.exception("Unable to retrieve the active branch.")


def check_current_commit_ids_match(paths: utils.Paths, branch_name: str) -> bool:
    log.info("Checking if the branch id matches the HEAD id")
    try:
        current_head_id = utils.get_reference_id(paths, "HEAD")
    except (errors.ReferenceFileError, errors.MissingBranchError):
        log.critical("Corrupted references file")
        return False
    try:
        current_branch_id = utils.get_reference_id(paths, branch_name)
    except errors.ReferenceFileError:
        log.critical("Corrupted references file")
        return False
    except errors.MissingBranchError:
        log.exception(f"Unable to retrieve the {branch_name} commit id as branch not found")
        return False
    if current_head_id != current_branch_id:
        log.error(
            "The current HEAD commit id does not match the active branch, {branch_name}, id."
        )
        return False
    log.info("The branch id matches the HEAD id")
    return True


def commit(commit_message: str) -> str | None:
    try:
        paths = utils.get_paths()
    except errors.WitDirectoryNotFoundError:
        log.error(
            "Unable to find a wit repository in any of the parent folders of the current working directory"
            )
        return
    commit_id = create_commit_folder(paths)
    if commit_id is None:
        return
    if not create_commit_meta_data(paths, commit_id, commit_message):
        return
    branch_name = get_active_branch(paths)
    if branch_name is None:
        remove_commit_folder(paths, commit_id)
        return
    if branch_name != "None":
        if not check_current_commit_ids_match(paths, branch_name):
            remove_commit_folder(paths, commit_id)
            return
    if not utils.update_references(paths, commit_id, branch_name):
        remove_commit_folder(paths, commit_id)
    return commit_id

