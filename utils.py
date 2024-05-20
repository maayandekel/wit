import logging
import os
from typing import NamedTuple

import errors

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class Paths(NamedTuple):
    cwd: str
    wit: str
    wit_dir: str
    images: str
    staging: str
    active: str
    references: str


def get_wit_path(path: str) -> str:
    log.info(f"Finding wit directory in a parent path of {path}")
    current_wit_path = os.path.join(path, ".wit")
    while os.path.dirname(path) != path:
        current_wit_path = os.path.join(path, ".wit")
        if os.path.isdir(current_wit_path):
            log.info(f"Wit directory found in {path}")
            return current_wit_path
        path = os.path.dirname(path)
    if os.path.isdir(current_wit_path):
        log.info(f"Wit directory found in {path}")
        return current_wit_path
    raise errors.WitDirectoryNotFoundError(path)


def get_paths(path: str | None = None, wit_exist: bool = True) -> Paths:
    log.info("Getting basic wit paths")
    cwd = os.getcwd()
    if path is None:
        path = cwd
    if wit_exist:
        wit_path = get_wit_path(path)
    else:
        wit_path = os.path.join(cwd, '.wit')
    wit_dir = os.path.dirname(wit_path)
    images = os.path.join(wit_path, 'images')
    staging = os.path.join(wit_path, 'staging_area')
    active = os.path.join(wit_path, 'activated.txt')
    references = os.path.join(wit_path, 'references.txt')
    log.info("Finished getting basic wit paths")
    return Paths(
        cwd = cwd,
        wit = wit_path,
        wit_dir = wit_dir,
        images = images,
        staging = staging,
        active = active,
        references = references,
    )


def get_reference_id(paths: Paths, id_type: str = "HEAD") -> str | None:
    if not os.path.isfile(paths.references):
        return
    with open(paths.references, "r") as references_file:
        references = references_file.read().split()
    if len(references) < 2:
        raise errors.ReferenceFileError("The reference file must have at least 2 lines - HEAD and master.")
    if "HEAD=" not in references[0]:
        raise errors.ReferenceFileError(
            "The first line of the reference file must be of the format: HEAD=commit_id"
        )
    if "master=" not in references[1]:
        raise errors.ReferenceFileError(
            "The second line of the reference file must be of the format: master=commit_id"
        )
    for reference in references:
        if id_type.upper() in reference.upper():
            return reference.split("=")[1]
    raise errors.MissingBranchError(
        f"The given branch name, {id_type}, does not exist in references.txt"
    )


def create_path(destination_path: str) -> None:
    os.makedirs(destination_path, exist_ok=True)


def _update_reference_head(head_reference_line: str, commit_id: str) -> str | bool:
    log.debug("Updating the HEAD info in the data for references.txt")
    if "HEAD=" not in head_reference_line:
        log.error(
            "The first line of the reference file must be of the format: HEAD=commit_id, "
            "unable to update HEAD info"
        )
        return False
    return f"HEAD={commit_id}"


def _update_reference_branch(
    references: list[str], branch: str, commit_id: str
) -> list[str] | bool:
    log.debug("Updating the branch info in the data for references.txt")
    if len(references) < 2:
        log.error(
            "References.txt content must have at least 2 rows - HEAD and master, unable to update branch info"
        )
        return False
    new_references = [_update_reference_head(references[0], commit_id)]
    if not new_references:
        return False
    branch_found = False
    for reference in references[1:]:
        if branch in reference:
            new_references.append(f"{branch}={commit_id}")
            branch_found = True
        else:
            new_references.append(reference)
    if not branch_found:
        log.error(
            f"Branch {branch} not found in references content provided. Unable to update branch info."
        )
        return False
    return new_references


def create_new_references(
    references_path: str, head_commit_id: str, branch_name: str
) -> bool:
    log.info("Creating new references file")
    references = (
            f"HEAD={head_commit_id}\n"
            f"master={head_commit_id}\n"
        )
    if branch_name.lower() != 'master':
        log.warning(f"The first commit should be made to the master branch and not {branch_name}")
        references += f"{branch_name}={head_commit_id}\n"
    try:
        with open(references_path, "w") as references_file:
            references_file.write(references)
    except OSError:
        log.critical("Unable to create references file")
        return False
    log.info("New references file created successfully")
    return True


def update_references(
    paths: Paths, head_commit_id: str, branch_name: str
) -> bool:
    log.info("Updating the references file")
    if not os.path.isfile(paths.references):
        log.debug("No existing references file found, creating new references.txt")
        if not create_new_references(paths.references, head_commit_id, branch_name):
            return False
        return True
    log.debug("Reading references.txt")
    try:
        with open(paths.references, "r") as references_file:
            current_references = references_file.read().split()
    except OSError:
        log.exception("Updating failed - unable to read references.txt")
        return False
    new_references = _update_reference_branch(
        current_references, branch_name, head_commit_id
    )
    if new_references is False:
        return False
    log.debug("Writing to references.txt")
    new_reference_text = "\n".join(new_references) + '\n'
    try:
        with open(paths.references, "w") as references_file:
            references_file.write(new_reference_text)
    except OSError:
        log.exception("Updating failed - unable to write to references.txt.")
        return False
    log.info("Updated references.txt successfully")
    return True