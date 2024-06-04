import logging
import sys

import add
import branch
import checkout
import commit
import init
import status


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


COMMANDS = {
    'init': (0, init.init),
    'add': (1, add.add),
    'commit': (1, commit.commit),
    'status': (0, status.run_status),
    'checkout': (1, checkout.checkout),
    'branch': (1, branch.branch)

}
NUMBER_OF_ARGS = 0
FUNCTION = 1


def main(code_path: str, command: str, *args: str):
    if len(args) != COMMANDS[command][NUMBER_OF_ARGS]:
        log.error(f"{command} command takes {COMMANDS[command][NUMBER_OF_ARGS]} arguments, {len(args)} were given.")
        return
    COMMANDS[command][FUNCTION](*args)
    

if __name__ == '__main__':
    main(*sys.argv)
