import flask
import os

import add
import branch
import checkout
import commit
import errors
import status
import utils

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'POST']) 
def index():
    commit_id, to_commit, unstaged, untracked = status.status()
    return flask.render_template(
        'index.html',
        commit_id=commit_id,
        to_commit=to_commit,
        unstaged=unstaged,
        untracked=untracked,
    )
    

@app.route('/add', methods=['GET', 'POST'])
def add_page():
    path = flask.request.form.get('file_path')
    added = add.add(path)
    if added:
        return flask.redirect("../")
    return flask.Response(status=400)


@app.route('/commit', methods=['GET', 'POST'])
def commit_page():
    message = flask.request.form.get('commit_message')
    commit_id = commit.commit(message)
    if commit_id:
        return flask.redirect("../")
    

@app.route('/branches', methods=['GET', 'POST']) 
def branch_page():
    paths = utils.get_paths(os.getcwd())
    active = utils.get_active_branch(paths)
    branches = utils.get_branches(paths)
    branches.remove(active)
    return flask.render_template(
        'branch.html',
        active_branch=active,
        inactive_branches=branches,
    )


@app.route('/newbranch', methods=['GET', 'POST'])
def new_branch():
    new_branch_name = flask.request.form.get('new_name')
    branch.branch(new_branch_name)
    return flask.redirect("../branches")


@app.route('/checkout', methods=['GET', 'POST']) 
def checkout_page():
    branch_name = flask.request.form.get('branch_name')
    try:
        commit_id = checkout.checkout(branch_name)
    except errors.StatusNotResolvedError:
        return flask.Response(status=400)
    paths = utils.get_paths(os.getcwd())
    commit_path = os.path.join(paths.images, commit_id)
    files = utils.get_directory_files(commit_path, paths.wit_dir)
    return flask.render_template(
        'checkout.html',
        branch=branch_name,
        branch_files=files,
    )


if __name__ == '__main__':
    app.run(host='localhost', port=5000)