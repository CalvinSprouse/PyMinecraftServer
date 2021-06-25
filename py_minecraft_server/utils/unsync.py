import asyncio


def unsync_function(func, *args, **kwargs):
    """Runs an async function in a standard blocking way and returns output"""
    return asyncio.run(func(*args, **kwargs))
