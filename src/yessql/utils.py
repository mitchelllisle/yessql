class PendingConnectionError(ValueError):
    """Error for when you attempt to use connection before calling setup_connection"""


class PendingConnection:
    """Pending Connection Class
    This class is used to differentiate between having made an actual connection to the database
    vs only having instantiated the class. This is important so that we can catch any confusing
    errors and instead return more helpful messages explaining that a connection has not been made
    yet.
    """

    def __enter__(self):
        raise PendingConnectionError(
            'You are trying to use a PendingConnection object. '
            'Did you forget to run setup_connection()?'
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        pass

    def commit(self):
        pass
