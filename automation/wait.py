from asyncio import get_event_loop, sleep


async def wait_for_condition(condition, timeout=5, check_period=0.5):
    start = get_event_loop().time()
    while get_event_loop().time() - start < timeout:
        if condition():
            return
        await sleep(check_period)
    raise TimeoutError("Timeout waiting for condition")
