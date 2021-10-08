class Error(Exception):
    """Base exception class"""

    def __init__(self, msg, cause=None):
        super(Error, self).__init__(msg)
        self._cause = cause

    @property
    def cause(self):
        return self._cause


class APIError(Error):
    pass
