from dataclasses import dataclass, field
from typing import Type, List, Union, NewType, Mapping, TypeVar, Callable, Iterable
import uuid
import datetime as dt

T = TypeVar('T')

class Pending: pass
class InProgress: pass
class Complete: pass
Status = Union[Pending, InProgress, Complete]

@dataclass(eq=True, frozen=True)
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
    status: Status = Type[Pending]
    

