from collections import namedtuple
import logging
# Types to wrap future results in.
Success = namedtuple('Success', ['args', 'result'])
Fail = namedtuple('Failure', ['args', 'reason'])    


def submit_to_executor(executor, func, args):
    """Abtracting the pattern of submitting tasks to an executor

    Args
    ----
    executor : futures.Executor
        A threadpool or processpool executor
    func : <function>
        Some function to submit to the pool
    TODO: Make this more generic

    """
    to_do = {}
    for args in args:
        if isinstance(args, tuple):
            future = executor.submit(func, *args)
        else:
            future = executor.submit(func, args)
        to_do[future] = args
    return to_do

def get_future_result(future, to_do):
    """Wraps and returns a future result."""
    try:
        future_result = future.result()
    except Exception as exc:
        result = Fail(to_do[future], str(exc))
    else:
        result = Success(to_do[future], future_result)
    return result

