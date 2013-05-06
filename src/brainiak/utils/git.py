import subprocess


GET_BRANCH = 'git rev-parse --abbrev-ref HEAD'
GET_TAG = 'git describe --exact-match --tags HEAD'
GET_COMMIT = 'git  rev-parse --verify HEAD'


def run(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.readline().split('\n')[0]


def checkout(state):
    run("git checkout %s" % state)


def stash():
    run('git stash save "xubiru123"')


def apply_stash():
    run("git stash apply stash^{/xubiru123}")


def get_version_label():
    """
    Return current branch or tag, if any, otherwise return <DEFAULT_VERSION>
    """

    tag = run(GET_TAG)
    branch = run(GET_BRANCH)
    label = tag or branch
    if label == 'HEAD':
        label = 'unstaged'
    return label


def get_version_hash():
    return run(GET_COMMIT)


def get_code_version():
    label = get_version_label()
    commit = get_version_hash()
    version = "%s | %s" % (label, commit)
    return version
