"""
used by config.py
which needs a dictionary-like item for storing repositories
that only accepts items that are concrete instances
of the abstract repository.py classes
"""

import abc

import inflection

try:
    from knowledge_service import repositories
except ModuleNotFoundError:
    import repositories
except ImportError:
    import repositories


class RepoSet:
    def __init__(self):
        self._data = {}
        # use snake_case version of repository.ClassName for keys
        # inflection is a library that can convert strings to snake_case
        allowable_keys = {
            inflection.underscore(cls.__name__)
            for cls in vars(repositories).values()
            if isinstance(cls, type)
            and issubclass(cls, abc.ABC)
            and cls is not abc.ABC
        }
        for key in allowable_keys:
            self._data[key] = None

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if key not in self._data:
            keylist = list(self._data.keys())
            msg = f"Invalid key '{key}'. Must be one of {keylist}"
            raise KeyError(msg)
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)
