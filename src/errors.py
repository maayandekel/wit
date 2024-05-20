

class WitError(Exception):
    def __init__(self):
        pass


class WitDirectoryNotFoundError(WitError):
    def __init__(self, original_full_path: str):
        self.given_path = original_full_path

    def __str__(self) -> str:
        return f"No wit directory found in any directory in the full path: {self.given_path}"
    

class ReferenceFileError(WitError):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"The reference file found is improperly formatted. {self.message}"
    

class MissingBranchError(WitError):
    def __init__(self, branch: str):
        self.branch = branch

    def __str__(self) -> str:
        return f"The given branch name, {self.branch}, does not exist."


class StatusNotResolvedError(WitError):
    STATUS_ISSUE = {1: "changes to be commited", 2: "changes not staged for commit"}

    def __init__(self, status_type):
        self.status_problem = StatusNotResolvedError.STATUS_ISSUE[status_type]

    def __str__(self) -> str:
        return f"The current status is unresolved. There are {self.status_problem}"