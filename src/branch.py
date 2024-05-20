import logging


import utils


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def branch_exists(branch, references):
    log.info("Checking if the branch name already exists in references info")
    for reference in references:
        current_branch = reference.partition('=')[0].lower()
        if branch == current_branch:
            return True


def branch(branch_name):
    log.info("Creating a new branch")
    paths = utils.get_paths()
    current_head_id = utils.get_reference_id(paths, 'HEAD')
    with open(paths.references, 'r') as references_file:
        current_references = references_file.read().split()
    if branch_exists(branch_name, current_references):
        log.error("The given branch name already, failed to create a new branch")
        return
    with open(paths.references, 'a') as references_file:
        references_file.write(f"{branch_name}={current_head_id}\n")
    log.info("Created a new branch successfully")
    

