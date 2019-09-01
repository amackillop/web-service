from dataclasses import dataclass, field
from typing import Type, List, Tuple, Union, TypeVar, NewType, Callable, Iterable, Iterator, Any
import uuid
import datetime as dt

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
    complete: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)

@dataclass()
class Job:
    uploaded: Uploaded
    job_id: str
    created: str = dt.datetime.utcnow().isoformat()
    finished: bool = False
    status: Status = Pending()
    