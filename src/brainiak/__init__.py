from brainiak import version
from brainiak.utils import git

__doc__ = u"Brainiak Semantic Wrapper Server"

if git.is_available():
    __version__ = git.get_code_version()
else:
    __version__ = version.RELEASE
