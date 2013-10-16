import re
import subprocess


GET_BRANCH = 'git rev-parse --abbrev-ref HEAD'
GET_TAG = 'git describe --exact-match --tags HEAD'
GET_COMMIT = 'git rev-parse --verify HEAD'


def run(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.readline().split('\n')[0]


def is_available():
    log_line = run('git log -1')
    return 'commit' in log_line


def checkout(state):
    run(u"git checkout %s" % state)


def stash():
    run('git stash save "xubiru123"')


def apply_stash():
    run("git stash apply stash^{/xubiru123}")
    run("git stash clear")


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
    version = u"%s | %s" % (unicode(label), unicode(commit))
    return version


def get_last_git_tag():
    last_tag = run("git describe")
    version = [major, minor, micro] = re.search(r"(\d+)\.(\d+)\.(\d+)+", last_tag).groups()
    return [int(version_digit) for version_digit in version]


def compute_next_git_tag(release_type="micro"):
    digits = {"major": 0, "minor": 1, "micro": 2}
    release_digit = digits[release_type]
    version = get_last_git_tag()

    version[release_digit] += 1
    for smaller_digit in range(release_digit + 1, 3):
        version[smaller_digit] = 0

    return "%d.%d.%d" % tuple(version)


def build_release_string():
    return "RELEASE = '%s'" % get_code_version()


def build_next_release_string(release_type="micro"):
    return "RELEASE = '%s'" % compute_next_git_tag(release_type)
