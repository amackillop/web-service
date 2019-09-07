from dataclasses import dataclass, field
from typing import *
import uuid
import datetime as dt

T = TypeVar('T')

FuncType = Callable[..., Any]
Func = TypeVar('Func', bound=FuncType)

@dataclass(frozen=True)
class Pending: pass

@dataclass(frozen=True)
class InProgress: pass

@dataclass(frozen=True)
class Complete: pass

# Status = NewType('Status', str)
Status = Union[Pending, InProgress, Complete]

@dataclass(frozen=True)
class Uploaded:
    pending: List[str] = field(default_factory=list)
    completed: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)

@dataclass()
class Job:
    uploaded: Uploaded
    job_id: str
    created: str = field(default_factory=lambda: dt.datetime.utcnow().isoformat())
    finished: str = ''
    status: Status = Pending()
    