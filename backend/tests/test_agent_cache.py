"""Tests for the bounded agent cache.

Each cached agent holds a live MCP subprocess (~95 MB), so the cache must stay
capped. These exercise the bookkeeping without spawning real subprocesses.
"""

import asyncio

import pytest

import app.agent.graph as graph


class FakeStack:
    def __init__(self):
        self.closed = False

    async def aclose(self):
        self.closed = True


@pytest.fixture
def clean_cache():
    """Isolate the module-level caches between tests."""
    graph._agent_cache.clear()
    graph._agent_stacks.clear()
    graph._agent_locks.clear()
    graph._agent_last_used.clear()

    yield

    graph._agent_cache.clear()
    graph._agent_stacks.clear()
    graph._agent_locks.clear()
    graph._agent_last_used.clear()


def _add(uid, stacks, last_used=None):
    stack = FakeStack()
    stacks[uid] = stack

    graph._agent_cache[uid] = f"agent-{uid}"
    graph._agent_stacks[uid] = stack
    graph._agent_locks[uid] = asyncio.Lock()
    # Higher value means more recently used.
    graph._agent_last_used[uid] = uid if last_used is None else last_used


async def test_busy_users_are_not_evicted(clean_cache):
    """Closing a subprocess mid-request would break that request."""
    stacks = {}
    for uid in (1, 2, 3):
        _add(uid, stacks)

    # User 1 is the least recently used but is mid-request.
    graph._agent_last_used[1] = 0
    graph._agent_last_used[2] = 1
    graph._agent_last_used[3] = 2

    await graph._agent_locks[1].acquire()

    try:
        await graph._evict_least_recent()
    finally:
        graph._agent_locks[1].release()

    assert stacks[1].closed is False
    assert 1 in graph._agent_cache
    assert stacks[2].closed
    assert 2 not in graph._agent_cache


async def test_no_eviction_when_everyone_is_busy(clean_cache):
    """Exceeding the cap briefly beats breaking an in-flight request."""
    stacks = {}
    for uid in (1, 2):
        _add(uid, stacks)

    for uid in (1, 2):
        await graph._agent_locks[uid].acquire()

    try:
        await graph._evict_least_recent()
    finally:
        for uid in (1, 2):
            graph._agent_locks[uid].release()

    assert all(stack.closed is False for stack in stacks.values())
    assert set(graph._agent_cache) == {1, 2}


async def test_eviction_closes_the_victim_and_drops_its_bookkeeping(
    clean_cache,
):
    stacks = {}
    for uid in range(1, 5):
        _add(uid, stacks)

    victim = min(graph._agent_last_used, key=graph._agent_last_used.get)

    await graph._evict_least_recent()

    assert stacks[victim].closed
    assert victim not in graph._agent_cache
    assert victim not in graph._agent_stacks
    assert victim not in graph._agent_locks
    assert victim not in graph._agent_last_used


async def test_cache_never_exceeds_the_cap(clean_cache):
    """The loop in get_or_create_agent evicts before adding, not after."""
    stacks = {}
    created = []

    for uid in range(1, 12):
        while len(graph._agent_cache) >= graph._MAX_CACHED_AGENTS:
            await graph._evict_least_recent()

        _add(uid, stacks)
        created.append(uid)

        assert len(graph._agent_cache) <= graph._MAX_CACHED_AGENTS

    assert len(graph._agent_cache) == graph._MAX_CACHED_AGENTS


async def test_eviction_prefers_least_recently_used(clean_cache):
    stacks = {}
    for uid in (1, 2, 3):
        _add(uid, stacks)

    # User 1 was added first but touched most recently.
    graph._agent_last_used[1] = 999

    await graph._evict_least_recent()

    assert stacks[2].closed
    assert stacks[3].closed is False
    assert stacks[1].closed is False
    assert set(graph._agent_cache) == {1, 3}


async def test_shutdown_closes_everything(clean_cache):
    stacks = {}
    for uid in range(1, 4):
        _add(uid, stacks)

    await graph.close_mcp_agents()

    assert all(stack.closed for stack in stacks.values())
    assert not graph._agent_cache
    assert not graph._agent_stacks
    assert not graph._agent_locks
    assert not graph._agent_last_used