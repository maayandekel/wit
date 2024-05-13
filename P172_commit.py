# Upload 172


import datetime
import os
import random
import shutil
import string
import sys


import P171_add as add


class ReferenceFileError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"The reference file found is improperly formatted. {self.message}"


def create_commit_id() -> str:
    return "".join(random.choice(string.hexdigits) for _ in range(40))


def create_commit_folder(wit_path: str) -> str:
    commit_id = create_commit_id()
    commit_path = os.path.join(wit_path, "images", commit_id)
    source_path = os.path.join(wit_path, "staging_area")
    shutil.copytree(source_path, commit_path)
    return commit_id


def create_commit_meta_data(
    wit_path: str, references_path: str, commit_id: str, message: str
) -> None:
    creation_time = datetime.datetime.now()
    formatted_creation_time = creation_time.strftime("%a %b %d %H:%M:%S %Y %z")
    parent = get_reference_id(references_path)
    message = (
        f"parent={parent}\n" f"date={formatted_creation_time}\n" f"message={message}\n"
    )
    commit_file_path = os.path.join(wit_path, "images", f"{commit_id}.txt")
    with open(commit_file_path, "w") as commit_file:
        commit_file.write(message)


def get_reference_id(references_path: str, id_type: str = "HEAD") -> str | None:
    if not os.path.isfile(references_path):
        return
    with open(references_path, "r") as references_file:
        references = references_file.read().split()
    if len(references) < 2:
        raise ReferenceFileError("The reference file must have at least 2 lines.")
    if "HEAD=" not in references[0]:
        raise ReferenceFileError(
            "The first line of the reference file must be of the format: HEAD=commit_id"
        )
    if "master=" not in references[1]:
        raise ReferenceFileError(
            "The second line of the reference file must be of the format: master=commit_id"
        )
    for reference in references:
        if id_type.upper() in reference.upper():
            return reference.split("=")[1]
    raise ValueError(
        f"The given branch name, {id_type}, does not exist in references.txt"
    )


def get_active_branch(wit_path: str) -> str:
    active_path = os.path.join(wit_path, "activated.txt")
    with open(active_path, "r") as active_file:
        active = active_file.read()
    return active


def create_new_references(
    references_path: str, head_commit_id: str, branch_name: str
) -> None:
    references = f"HEAD={head_commit_id}\n" f"{branch_name}={head_commit_id}\n"
    with open(references_path, "w") as references_file:
        references_file.write(references)


def update_reference_head(head_reference_line: str, commit_id: str) -> str:
    if "HEAD=" not in head_reference_line:
        raise ReferenceFileError(
            "The first line of the reference file must be of the format: HEAD=commit_id"
        )
    return f"HEAD={commit_id}"


def update_reference_branch(
    references: list[str], branch: str, commit_id: str
) -> list[str]:
    new_references = [update_reference_head(references[0], commit_id)]
    for reference in references[1:]:
        if branch in reference:
            new_references.append(f"{branch}={commit_id}")
        else:
            new_references.append(reference)
    return new_references


def check_current_commit_ids_match(references_path: str, branch_name: str) -> None:
    current_head_id = get_reference_id(references_path, "HEAD")
    current_branch_id = get_reference_id(references_path, branch_name)
    if current_head_id != current_branch_id:
        raise ValueError(
            "The current HEAD commit id does not match the active branch, {branch_name}, id."
        )


def update_references(
    references_path: str, head_commit_id: str, branch_name: str
) -> None:
    if not os.path.isfile(references_path):
        create_new_references(references_path, head_commit_id, branch_name)
        return
    with open(references_path, "r") as references_file:
        current_references = references_file.read().split()
    new_references = update_reference_branch(
        current_references, branch_name, head_commit_id
    )
    with open(references_path, "w") as references_file:
        references_file.write("\n".join(new_references))


def commit(commit_message: str) -> None:
    wit_path = add.get_wit_path(os.getcwd())
    references_path = os.path.join(wit_path, "references.txt")
    commit_id = create_commit_folder(wit_path)
    create_commit_meta_data(wit_path, references_path, commit_id, commit_message)
    branch_name = get_active_branch(os.path.dirname(references_path))
    if branch_name == "None":
        branch_name = "HEAD"
    check_current_commit_ids_match(references_path, branch_name)
    update_references(references_path, commit_id, branch_name)


if len(sys.argv) >= 2:
    if sys.argv[1] == "commit":
        commit(sys.argv[2])


# commit('testing_branch_changes')
