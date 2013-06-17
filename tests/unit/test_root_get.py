from brainiak.root.get import list_all_contexts
from brainiak.utils.cache import memoize


def test_usage_of_memoize():
    assert list_all_contexts.func_globals['memoize'] == memoize
