import unittest
from brainiak.utils.git import *


class GitTestCase(unittest.TestCase):

    def setUp(self):
        stash()
        label = get_version_label()
        commit = get_version_hash()
        self.head = label if label != 'unstaged' else commit

    def tearDown(self):
        checkout(self.head)
        apply_stash()

    def test_git_version_is_tag(self):
        checkout_tag = checkout("1.0.0")
        computed = get_version_label()
        expected = '1.0.0'
        self.assertEquals(computed, expected)

    def test_git_version_is_branch(self):
        checkout_branch = checkout("master")
        computed = get_version_label()
        expected = 'master'
        self.assertEquals(computed, expected)

    def test_git_version_is_unstaged(self):
        checkout_hash = checkout("8fc3444aa944a79777e30aa287a9a714e4c3871e")
        computed = get_version_label()
        expected = 'unstaged'
        self.assertEquals(computed, expected)

    def test_get_version(self):
        checkout_branch = checkout("1.0.0")
        computed = get_code_version()
        expected = '1.0.0 | bfef0438c8bf04f698523896bc7f1f3d62aaa3ef'
        self.assertEquals(computed, expected)


if __name__ == '__main__':
    unittest.main()
