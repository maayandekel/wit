import logging
import sys

import init
import add
import commit
import status
import checkout
import branch


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def main(code_path: str, command: str, *args: str):
    if command == 'init':
        if len(args) != 0:
            log.error(f"init command does not take any arguments, {len(args)} were given.")
            return
        init.init()
    if command == 'add':
        if len(args) != 1:
            log.error(f"add command takes exactly 1 argument, {len(args)} were given.")
            return
        add.add(*args)
    if command == 'commit':
        if len(args) != 1:
            log.error(f"commit command takes exactly 1 argument, {len(args)} were given.")
            return
        commit.commit(*args)
    if command == 'status':
        if len(args) != 0:
            log.error(f"status command does not take any arguments, {len(args)} were given.")
        current_status = status.status()
        print(status.status_message(*current_status))
    if command == 'checkout':
        if len(args) != 1:
            log.error(f"checkout command takes exactly 1 argument, {len(args)} were given.")
            return
        checkout.checkout(*args)
    if command == 'branch':
        if len(args) != 1:
            log.error(f"branch command takes exactly 1 argument, {len(args)} were given.")
            return
        branch.branch(*args)



if __name__ == '__main__':
    main(*sys.argv)
