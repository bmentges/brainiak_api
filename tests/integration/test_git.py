import unittest
#from brainiak.utils import git


# class GitTestCase(unittest.TestCase):
#
#     def setUp(self):
#         git.stash()
#         label = git.get_version_label()
#         commit = git.get_version_hash()
#         self.head = label if label != 'unstaged' else commit
#         # mocks
#         self.original_get_last_git_tag = git.get_last_git_tag
#         self.orginal_get_code_version = git.get_code_version
#         self.original_run = git.run
#         self.original_compute_next_git_tag = git.compute_next_git_tag
#
#     def tearDown(self):
#         git.checkout(self.head)
#         git.apply_stash()
#         # mocks
#         git.get_last_git_tag = self.original_get_last_git_tag
#         git.get_code_version = self.orginal_get_code_version
#         git.run = self.original_run
#         git.compute_next_git_tag = self.original_compute_next_git_tag
#
#     def test_git_version_is_tag(self):
#         checkout_tag = git.checkout("1.0.0")
#         computed = git.get_version_label()
#         expected = '1.0.0'
#         self.assertEquals(computed, expected)
#
#     def test_git_version_is_branch(self):
#         checkout_branch = git.checkout("master")
#         computed = git.get_version_label()
#         expected = 'master'
#         self.assertEquals(computed, expected)
#
#     def test_git_version_is_unstaged(self):
#         checkout_hash = git.checkout("8fc3444aa944a79777e30aa287a9a714e4c3871e")
#         computed = git.get_version_label()
#         expected = 'unstaged'
#         self.assertEquals(computed, expected)
#
#     def test_get_version(self):
#         checkout_branch = git.checkout("1.0.0")
#         computed = git.get_code_version()
#         expected = '1.0.0 | bfef0438c8bf04f698523896bc7f1f3d62aaa3ef'
#         self.assertEquals(computed, expected)
#
#     def test_is_available(self):
#         self.assertTrue(git.is_available())
#
#     def test_compute_next_git_tag_1_0_0_major(self):
#         git.get_last_git_tag = lambda: [1, 0, 0]
#         release_type = "major"
#         computed = git.compute_next_git_tag(release_type)
#         expected = "2.0.0"
#         self.assertEquals(computed, expected)
#
#     def test_compute_next_git_tag_1_0_0_minor(self):
#         git.get_last_git_tag = lambda: [1, 0, 0]
#         release_type = "minor"
#         computed = git.compute_next_git_tag(release_type)
#         expected = "1.1.0"
#         self.assertEquals(computed, expected)
#
#     def test_compute_next_git_tag_1_0_0_micro(self):
#         git.get_last_git_tag = lambda: [1, 0, 1]
#         release_type = "micro"
#         computed = git.compute_next_git_tag(release_type)
#         expected = "1.0.2"
#         self.assertEquals(computed, expected)
#
#     def test_compute_next_git_tag_2_3_1_micro(self):
#         git.get_last_git_tag = lambda: [2, 3, 1]
#         release_type = "micro"
#         computed = git.compute_next_git_tag(release_type)
#         expected = "2.3.2"
#         self.assertEquals(computed, expected)
#
#     def test_compute_next_git_tag_2_3_2_minor(self):
#         git.get_last_git_tag = lambda: [2, 3, 2]
#         release_type = "minor"
#         computed = git.compute_next_git_tag(release_type)
#         expected = "2.4.0"
#         self.assertEquals(computed, expected)
#
#     def test_compute_next_git_tag_2_3_3_major(self):
#         git.get_last_git_tag = lambda: [2, 3, 3]
#         release_type = "major"
#         computed = git.compute_next_git_tag(release_type)
#         expected = "3.0.0"
#         self.assertEquals(computed, expected)
#
#     def test_build_release_string(self):
#         git.get_code_version = lambda: "XUBIRU"
#         computed = git.build_release_string()
#         expected = "RELEASE = 'XUBIRU'"
#         self.assertEquals(computed, expected)
#
#     def test_get_last_git_tag_longer(self):
#         git.run = lambda cmd: "1.0.0-99-g9cb46b3"
#         computed = git.get_last_git_tag()
#         expected = [1, 0, 0]
#         self.assertEquals(computed, expected)
#
#     def test_get_last_git_tag_3_2_1(self):
#         git.run = lambda cmd: "3.2.1"
#         computed = git.get_last_git_tag()
#         expected = [3, 2, 1]
#         self.assertEquals(computed, expected)
#
#     def test_get_last_git_tag_multiple_digits(self):
#         git.run = lambda cmd: "10.200.3000"
#         computed = git.get_last_git_tag()
#         expected = [10, 200, 3000]
#         self.assertEquals(computed, expected)
#
#     def test_build_next_release_string(self):
#         git.compute_next_git_tag = lambda: "10.10.1"
#         computed = git.build_next_release_string()
#         expected = "RELEASE = '10.10.1'"
#         self.assertEquals(computed, expected)

if __name__ == '__main__':
    unittest.main()
