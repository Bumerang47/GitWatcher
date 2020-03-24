from datetime import datetime

import pytest

from git_watcher.objects import Contributor
from git_watcher.source import Request
from .conftest import UnstableRequester


@pytest.mark.asyncio
async def test_filter_contributors(_config, github, patch_request_contrib):
    await github.update_contributors()
    assert len(github.contributors) == 3

    github.config.since = datetime.fromisoformat('2020-02-02T01:00:00+00:00')
    github.config.until = datetime.fromisoformat('2020-02-02T02:00:00+00:00')

    await github.update_contributors()
    assert len(github.contributors) == 2


def test_slice_contributors(github):
    github.contributors = {str(i): Contributor(str(i), count=i)
                           for i in range(33)}
    assert len(github.contributors) == 33

    github.config.size_top_table = 7
    contribs = github.get_top_contributors()
    assert len(contribs) == 7
    assert contribs[0].count == 32
    assert contribs[-1].count == 26


@pytest.mark.asyncio
async def test_trottler_request(github, patch_session_request):
    patch_session_request.return_value = UnstableRequester(raise_fails=1,
                                                           return_value=['resp'])
    github.attempts_max_interval = 0.1
    github.attempts_count = 2
    r = Request('GET', '://somewhere')
    async with github.single_request(r) as resp:
        assert resp == ['resp']

    patch_session_request.return_value.raise_fails = 3
    with pytest.raises(RuntimeError):
        async with github.single_request(r):
            pass


def test_makeing_table():
    pass


def test_log_level_switching():
    pass


def test_pagination_requests():
    pass


def test_load_pull_requests_info():
    pass


def test_load_issues_info():
    pass
