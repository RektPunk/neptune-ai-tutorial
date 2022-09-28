from enum import Enum


class NeptuneMode(str, Enum):
    OFFLINE = "offline"
    DEBUG = "debug"
    ASYNC = "async"
    SYNC = "sync"
    READ_ONLY = "read-only"

    def __repr__(self):
        return f"{self.value}"
