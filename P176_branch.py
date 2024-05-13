import os
import sys

import P171_add as add
import P172_commit as commit


def branch(branch_name):
    wit_path = add.get_wit_path(os.getcwd())
    references_path = os.path.join(wit_path, 'references.txt')
    current_head_id = commit.get_reference_id(references_path, 'HEAD')
    with open(references_path, 'r') as references_file:
        current_references = references_file.read()
    if branch_name.lower() not in current_references.lower():
        with open(references_path, 'a') as references_file:
            references_file.write(f"{branch_name}={current_head_id}\n")
        return
    raise ValueError("This branch name already exists!")


if len(sys.argv) >= 3:
    if sys.argv[1] == "branch":
        branch(sys.argv[2])


# branch("testing_branch")