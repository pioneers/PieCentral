class EmergencyStopException(SystemExit):
    """
    A special exception used to indicate an emergency stop (e-stop).

    The exit code 255 is used to communicate from child processes to the
    supervisor that an e-stop has occurred.
    """
    EXIT_CODE = 0xFF

    def __init__(self):
        super().__init__(self.EXIT_CODE)


class RuntimeBaseException(Exception):
    """
    Base for Runtime-specific exceptions.

    ``RuntimeBaseException`` accepts arbitrary data that can be examined in
    post-mortems or written into structured logs.

    Example:

        >>> err = RuntimeBaseException('Error', dev_ids=[2, 3])
        >>> err
        RuntimeBaseException('Error', dev_ids=[2, 3])

    """
    def __init__(self, message, **context):
        super().__init__(message)
        self.context = context

    def __repr__(self):
        cls_name, (msg, *_) = self.__class__.__name__, self.args
        if self.context:
            kwargs = ', '.join(f'{name}={repr(value)}' for name, value in self.context.items())
            return f'{cls_name}({repr(msg)}, {kwargs})'
        return f'{cls_name}({repr(msg)})'


class RuntimeExecutionError(RuntimeBaseException):
    """ An exception that occurred while attempting to execute student code. """
