class WhisperException(Exception):
    """Base class for whisper exceptions."""


class InvalidConfiguration(WhisperException):
    """Invalid configuration."""


class InvalidAggregationMethod(WhisperException):
    """Invalid aggregation method."""


class InvalidTimeInterval(WhisperException):
    """Invalid time interval."""


class TimestampNotCovered(WhisperException):
    """Timestamp not covered by any archives in this database."""


class CorruptWhisperFile(WhisperException):
    def __init__(self, error, path):
        super(CorruptWhisperFile, self).__init__(self, error)
        self.error = error
        self.path = path

    def __repr__(self):
        return "<CorruptWhisperFile[%s] %s>" % (self.path, self.error)

    def __str__(self):
        return "%s (%s)" % (self.error, self.path)
