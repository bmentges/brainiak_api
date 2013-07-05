from brainiak import version as _version
from brainiak.utils.git import get_code_version, is_available

__doc__ = u"Brainiak Semantic Wrapper Server"


def get_version():
    return get_code_version() if is_available() else _version.RELEASE

__version__ = get_version()
