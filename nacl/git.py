#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
nacl-git module

This is an abstraction for some raw stuff with the git command
itself and also the main module for the nacl-git command.
"""

import os.path
import os
from subprocess import Popen, PIPE
from pprint import pprint
from nacl.helper import color, merge_two_dicts
from nacl.fileutils import get_dir_list_from_filesystem
from nacl.base import get_users_nacl_conf
from nacl.base import get_salt_root_dirs
import nacl.gitapi
from nacl.decorator import log, ListLine
from nacl.exceptions import GitCallError


def get_all_possible_git_dirs():
    """
    There are two ways in getting git repo locations

    There are two ways to locate salt related git repos:
    1. Via the salt config when looking into file_root and pillar_root and
    2. via get_dir_list_from_filesystem

    We have to go both paths and then unify the results
    """
    salt_root_dir = get_salt_root_dirs()
    all_git_dirs_found = [x[:-5] for x in get_dir_list_from_filesystem()]
    possible_git_dirs = set(salt_root_dir + all_git_dirs_found)
    checked_git_dirs = [x for x in possible_git_dirs if is_git_repo(x)]
    return sorted(checked_git_dirs)


@log
def list_salt_git_repositories():
    """
    Printout all salt related git repos and their state

    Using a list of local git repositories to check whether
    they have uncommitted changes or not and list them in a pretty way.
    """

    check_dirs = get_all_possible_git_dirs()

    if not check_dirs:
        return [('WARNING', 'No git repository provided!', 3)]

    # Some Header
    # Fix this: Use a decorator for printing out stuff instead
    print("%-50s %-15s %-15s %-15s %s" % ("Directory", "Active Branch", "Status", "Local Master", "All Branches"))
    print("=" * 120)

    for git_dir in check_dirs:
        os.chdir(git_dir)
        pretty_status()


def merge_all_repositories():
    """
    Check every salt related git repo and merge if needed

    Merge all repositories at once when origin/master is ahead
    and the repository is clean.
    We will merge into local master!
    merge_git_repo is tested as well as get_all_possible_git_dirs.
    So no further tests intended.
    """
    git_repo_list = get_all_possible_git_dirs()
    for git_repo in git_repo_list:
            merge_git_repo(git_repo)


def merge_single_repository():
    """" Merge a single remote repo into the local branch. """
    merge_git_repo()


@log
def merge_git_repo(git_repo_name=None):
    """
    Merge a single git repository with origin/master

    Merge origin/master into local master branch.
    If another branch is active, we will switch to master and back again
    after the merge is done.
    """

    __ret = []

    if git_repo_name:
        os.chdir(git_repo_name)

    branch = get_current_branch()
    dir_name = os.getcwd()

    __ret.append(("INFO", "Checking: {0}".format(dir_name)))

    # First check if there are any uncommitted changes.
    # In this case skip merging!
    if not branch_is_clean():
        __ret.append(('INFO', 'Uncommitted changes, skipping...'))
        return __ret
    else:
        pass

    # We only merge into the local master branch
    if branch != 'master':
        __ret.append(('INFO', 'Checkout master'))
        checkout_branch('master')

    if need_pull_push(return__returncode=True) == 1:
        __ret.append(("INFO", "Need merge! "))
        __ret.append(("INFO", "Try to merge Branch: master in {0}".format(dir_name)))
    else:
        # Switch back to previous branch
        if branch != 'master':
            __ret.append(('INFO', 'Nothing to do in master... Switch back'))
            checkout_branch(branch)
        return __ret

    try:
        git(['fetch'])
        __ret.append(("INFO", "Start merge..."))
        git(['merge', '--ff-only', 'origin/master'])
        __ret.append(('INFO', 'Merge complete!'))
    except GitCallError as e:
        __ret.append(('INFO', 'Merge failed: {0}'.format(e.message)))

    # Switch back to prvevious branch
    if branch != 'master':
        __ret.append(('INFO', 'Switch back'))
        checkout_branch(branch)

    return __ret


@log
def remote_diff():
    """ Shows the diffs between the local and the origin/master"""

    __ret = []

    if not branch_is_clean():
        __ret.append(('INFO', 'Uncommitted changes.'))

    git(['fetch'])
    output = git(['diff', 'master', 'origin/master'])

    if output:
        __ret.append(('BOLD', output))
    else:
        __ret.append(('INFO', 'No diffs found'))

    return __ret


@log
def checkout_branch(branch=None):
    """ Checkout specified branch or master as default """

    print_is_git_repo()

    __ret = []

    if branch is None:
        git(['checkout', 'master'])
        __ret.append(('INFO', 'Branch: {0}'.format(get_current_branch())))
    elif branch == get_current_branch():
        __ret.append(('INFO', 'Already in {0}'.format(get_current_branch())))
    else:
        try:
            git(['checkout', branch])
            __ret.append(('INFO', 'Switch to branch: {0}'.format(get_current_branch())))
        except GitCallError as exc:
            __ret.append(('FAIL', 'Unable to checkout {0} : {1}'.format(branch, exc)))

    return __ret


def is_git_repo(dir_name=None):
    """ Return whether it is a git repo or not """
    if dir_name:
        os.chdir(dir_name)

    try:
        git(['status', '-s'])
        return True
    except GitCallError:
        return False


@log
def print_is_git_repo():
    """ Print and exit if is no repository """
    if not is_git_repo():
        return [('WARNING', 'No git repository found!', 1)]


def get_all_branches():
    """ Return a list with all branches """
    return git(['for-each-ref',
                '--format="%(refname:short)"',
                'refs/heads/']).replace('"', '').split()


def branch_exist(branch=None):
    """ Check whether a branch already exists """
    exiting_branches = get_all_branches()
    for existing_branch in exiting_branches:
        if existing_branch == branch:
            return True
    return False


@log
def change_or_create_branch(branch=None):
    """ Either creates (and switches into) a branch or just list branches """

    __ret = []

    print_is_git_repo()

    if branch is None:
        __ret.append(('INFO', git(['branch']).rstrip()))
    elif branch is not None and branch_exist(branch) is False:
        __ret.append(('INFO', 'Creating branch: {0}'.format(branch)))
        git(['branch', '--track', branch, 'origin/master'])
        git(['checkout', branch])
        __ret.append(('INFO', 'Switch into: {0}'.format(get_current_branch())))
    else:
        __ret.append(('INFO', "Branch exists. Change into {0}".format(branch)))
        git(['checkout', branch])

    return __ret


@log
def remote_prune():
    """
    Housekeeping of staled refs

    Removes staled remote refs (like old feature branches at the
    remote, that have been merged and deleted)
    """
    __ret = []
    try:
        output = git(['remote', 'prune', 'origin'])

    except GitCallError as e:
        __ret.append(('FAIL', 'Prune failed: {0}'.format(e)))
        return __ret

    if not output:
        output = 'Nothing to prune'
    __ret.append(('INFO', output))

    return __ret


def get_local_url_list():
    """ Get a list off all local repositories remote url's """

    url_list = []
    for repo in get_dir_list_from_filesystem():
        os.chdir(repo[:-4])
        url_list.append(git(['config', '--get', 'remote.origin.url']).rstrip())

    return url_list


def compare_remote():
    """
    Try to find differences between local and remote repositories

    Compare the existence of remote and local git repositories and show
    missing local repositories.
    """
    local_repo_urls = get_local_url_list()
    remote_url_dict = nacl.gitapi.get_remote_url_dict()

    print(color("FAIL", "WARNING: This list might be inaccurate!\n It will list remote git repositories, that are not in one of our salt environments!\n That might be ok!\n"))

    for url, desc in remote_url_dict.iteritems():
        if url not in local_repo_urls:
                url = color("GREEN", url)
                desc = color("WARNING", desc)
                print("%-59s" % (url))
                print("%-59s\n" % (desc))


def get_user_name():
    """
    Return the name of the git user

    This reads out the git config and returns the user.name parameter.
    """
    return git(['config', '--get', 'user.name']).rstrip()


def get_user_email():
    """
    Return the email adress of the git user

    This reads out the git config and returns the user.email parameter.
    """
    return git(['config', '--get', 'user.email']).rstrip()


def set_user_name(user_name=None):
    """ Set a git user.name """
    if not user_name:
        raise ValueError('user_name must be set!')

    git(['config', '--global', 'user.name', user_name])


def set_user_email(user_email=None):
    """ Set a git user.email """
    if not user_email:
        raise ValueError('user_email must be set!')

    git(['config', '--global', 'user.email', user_email])


def git(args, env={}):
    """
    The main git command wrapper

    Expects a list of args (e.g. ['diff']) and returns the git command output.
    Parameter env is used to append environment vars to ENV like a
    proxy setting.
    """

    user_config = get_users_nacl_conf()

    # We have to merge the os.environment and env, because we need HOME!
    env = merge_two_dicts(env, os.environ)

    # Any Proxy?
    try:
        proxy = user_config['proxy']
    except KeyError:
        proxy = False

    if proxy:
        env = merge_two_dicts(env, {'https_proxy': user_config['proxy']})

    p = Popen(['git'] + args, stdout=PIPE, stderr=PIPE, env=env)
    output, err = p.communicate()
    rc = p.wait()

    if err and rc != 0:
        raise GitCallError(err)

    # We are doing this because there might be umlauts in output that can not
    # be decoded to unicode (don't know why) and throwing errors like:
    # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 5: ordinal not in range(128)
    # Decoding it like below makes the decorator convert the str successfully
    # to unicode.
    # Ugly hack, but I just don't get it right by now.
    # TODO: Unterstand str and unicode better
    return output.decode("utf-8")


def branch_is_clean():
    """ Check whether a branch is clean """
    uncommited = git(['diff', '--name-only', 'HEAD'])
    if not uncommited:
        return True

    return False


def get_last_commit_sha():
    """ Return the current commit SHA"""
    return git(['rev-parse', 'HEAD'])


def is_commit_on_remote(sha=None, branch='master'):
    """ Check if sha is already in the remote branch"""
    if sha:
        try:
            remote_sha = git(['merge-base', sha.rstrip(), 'origin/' + branch])
            return bool(sha.rstrip() == remote_sha.rstrip())
        except:
            return False
    else:
        raise ValueError("sha must be provided")


def need_pull_push(return__returncode=False,
                   local_branch='master',
                   remote_branch='master'):
    """ Check whether we need to push or pull """

    git(['remote', 'update'])

    local = git(['rev-parse', local_branch])
    remote = git(['rev-parse', 'origin/' + remote_branch])
    base = git(['merge-base', local_branch, 'origin/' + remote_branch])

    if local == remote:
        answer = "Up-to-date"
        code = 0
    elif local == base:
        answer = "Need to pull"
        code = 1
    elif remote == base:
        answer = "Need to push"
        code = 2
    else:
        answer = "Diverged"
        code = 3

    if return__returncode is True:
        return code

    return answer


def get_current_branch():
    """ Returns the current active branch """

    return git(['rev-parse', '--abbrev-ref', 'HEAD']).rstrip()


def is_merged(branch):
    """ Check whether a local branch is already merged into origin/master """

    git(['remote', 'update'])
    local = git(['rev-parse', '@']).rstrip()
    remote = git(['merge-base', local, 'origin/master']).rstrip()

    if local == remote:
        return True
    return False


def print_merge_status(branch):
    """ Print out the merge status of branch """
    if is_merged(branch):
        return "(merged)"
    return "(unmerged)"


@ListLine
def pretty_status():
    """ Prints out some information about a repository """
    __ret = {}
    __ret['branch'] = get_current_branch()
    __ret['status'] = git(['status', '-s']).rstrip()
    __ret['pull_push'] = need_pull_push()
    __ret['merge_status'] = ''
    __ret['all_branches'] = ', '.join(get_all_branches())

    if branch_is_clean():
        __ret['status'] = 'Clean'
    else:
        __ret['status'] = __ret['status'][0:10]

    if __ret['branch'] != 'master':
        __ret['merge_status'] = print_merge_status(__ret['branch'])

    __ret['dir_name'] = os.getcwd()

    return __ret
