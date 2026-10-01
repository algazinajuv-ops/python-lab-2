class StreamStatsError(Exception):
    pass


class InvalidEventError(StreamStatsError):
    pass


class InvalidTimestampError(StreamStatsError):
    pass


class UnsupportedFormatError(StreamStatsError):
    pass