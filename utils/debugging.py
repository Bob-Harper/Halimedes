import inspect

def log_caller():
    frame = inspect.currentframe()
    outer = inspect.getouterframes(frame, 2)
    current = outer[1]
    caller = outer[2] if len(outer) > 2 else None
    if caller:
        print(f"[TRACE] {current.function} called from {caller.function} @ {caller.filename}:{caller.lineno}")
    else:
        print(f"[TRACE] {current.function} called from UNKNOWN")


def trace_calls(func):
    def wrapper(*args, **kwargs):
        print("=" * 50)
        print(f"[DEBUG] __file__: {func.__code__.co_filename}")
        print(f"[DEBUG] __name__: {func.__module__}")
        log_caller()
        return func(*args, **kwargs)
    return wrapper


def trace_async_calls(func):
    async def wrapper(*args, **kwargs):
        print("=" * 50)
        print(f"[DEBUG] __file__: {func.__code__.co_filename}")
        print(f"[DEBUG] __name__: {func.__module__}")
        log_caller()
        return await func(*args, **kwargs)
    return wrapper


"""
Implementation example:
=============================
from utils.debugging import trace_calls, trace_async_calls

@trace_calls
def some_function(values):
    ...

@trace_async_calls
async def some_async_function(mood):
    ...

    
==================================================
** output will be like so:

[DEBUG] __file__: /home/hal/eyes/EyeExpressionManager.py
[DEBUG] __name__: eyes.EyeExpressionManager
[TRACE] set_expression called from set_mood @ /home/hal/dsl/channels.py:44

"""