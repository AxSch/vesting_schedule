import asyncio

import pytest


@pytest.fixture(scope="function")
def event_loop_policy():
    policy = asyncio.get_event_loop_policy()
    yield policy


@pytest.hookimpl(trylast=True)
def pytest_fixture_setup(fixturedef, request):
    if fixturedef.argname == "event_loop":
        old_finish = fixturedef.finish

        def finish():
            loop = request.node.funcargs.get("event_loop")
            if loop is not None and not loop.is_closed():
                for task in asyncio.all_tasks(loop):
                    task.cancel()

                loop.run_until_complete(asyncio.sleep(0.1))

            old_finish()

        fixturedef.finish = finish
