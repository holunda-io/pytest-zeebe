from typing import ClassVar as _ClassVar, Optional as _Optional

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class StartEngineRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StartEngineResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StopEngineRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StopEngineResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResetEngineRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResetEngineResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IncreaseTimeRequest(_message.Message):
    __slots__ = ("milliseconds",)
    MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    milliseconds: int
    def __init__(self, milliseconds: _Optional[int] = ...) -> None: ...

class IncreaseTimeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WaitForIdleStateRequest(_message.Message):
    __slots__ = ("timeout",)
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    timeout: int
    def __init__(self, timeout: _Optional[int] = ...) -> None: ...

class WaitForIdleStateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WaitForBusyStateRequest(_message.Message):
    __slots__ = ("timeout",)
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    timeout: int
    def __init__(self, timeout: _Optional[int] = ...) -> None: ...

class WaitForBusyStateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRecordsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RecordResponse(_message.Message):
    __slots__ = ("recordJson",)
    RECORDJSON_FIELD_NUMBER: _ClassVar[int]
    recordJson: str
    def __init__(self, recordJson: _Optional[str] = ...) -> None: ...
