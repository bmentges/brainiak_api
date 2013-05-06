from brainiak.utils import git

__doc__ = u"Brainiak Semantic Wrapper Server"
__nversion__ = (1, 0, 0)
__api_version__ = ".".join(str(i) for i in __nversion__)
__version__ = "{0} | {1}".format(__api_version__, git.get_code_version())
