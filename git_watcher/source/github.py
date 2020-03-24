from collections import Counter
from datetime import datetime, timezone as tz
from typing import Callable, Optional
from urllib.parse import urljoin

from .abstract import AbstractProvider, Request
from ..objects import Contributor


class GitHub(AbstractProvider):
    pr_edge_days = 30
    issue_edge_days = 14
    base_url = 'https://api.github.com/'
    paginate_re = r'&page=(?P<n>\d+)>;\srel="(?P<name>\w+)"'

    async def update_contributors(self):
        url = urljoin(self.base_url, f'/repos/{self.owner}/{self.repo}/commits')
        params = {
            'since': self.since and self.since.isoformat(),
            'until': self.until and self.until.isoformat(),
            'sha': self.branch,
            'per_page': 100,
        }
        params = {k: v for k, v in params.items() if v}

        _contributors = {}
        async for resp in self.request('GET', url, params=params):
            list(self.parse_contributors(resp, _contributors))

        self.contributors.clear()
        self.contributors.update(_contributors)

    async def update_pulls_info(self):
        url = urljoin(self.base_url, f'/repos/{self.owner}/{self.repo}/pulls')
        params = {'base': self.branch, 'state': 'all', 'per_page': 100}
        info = Counter()

        async for resp in self.request('GET', url, params=params):
            counter = self.count_state_results(resp,
                                               edge_days=self.pr_edge_days,
                                               k_filter=lambda pr: pr['draft'])
            info.update(counter)
        self.pulls_info.clear()
        self.pulls_info.update({'name': 'Pulls', **info})

    async def update_issues_info(self):
        url = urljoin(self.base_url, f'/repos/{self.owner}/{self.repo}/issues')
        params = {'since': self.since and self.since.isoformat(),
                  'state': 'all', 'per_page': 100}
        params = {k: v for k, v in params.items() if v}

        info = Counter()

        async for resp in self.request('GET', url, params=params):
            def _filter(iss):
                # GitHub's REST API v3 considers every pull request an issue
                return 'pull_request' in iss

            counter = self.count_state_results(resp, edge_days=self.issue_edge_days,
                                               k_filter=_filter)
            info.update(counter)
        self.issues_info.clear()
        self.issues_info.update({'name': 'Issues', **info})

    def count_state_results(self, data, edge_days=None, k_filter: Callable = None) -> Counter:
        """ Count sate open, closed and the open old items from Issues or Pull Request
        :return: Counter(closed=<a>, opened=<b>, old_opened=<c>)
        """

        counter: Counter = Counter(closed=0, opened=0, old_opened=0)
        now = datetime.now(tz=tz.utc)
        for item in data:

            if k_filter and k_filter(item):
                continue

            created_at = self.valid_dates(item, key_date='created_at')
            if not created_at:
                continue

            if item['state'] == 'open':
                counter.update(opened=1)

                if (now - created_at).days > edge_days:
                    counter.update(old_opened=1)
            elif item['state'] == 'closed':
                counter.update(closed=1)
        return counter

    def parse_contributors(self, data, storage):
        for commit in data:
            git_author = commit['commit']['author']
            hub_author = commit.get('author')
            if not hub_author:
                # this a commit from local repository without github account
                login = git_author.get('email')
            else:
                login = hub_author.get('login')

            if not self.valid_dates(git_author, key_date='date'):
                continue

            if login not in storage:
                storage[login] = Contributor(login=login,
                                             email=git_author['email'],
                                             count=1)
                yield storage[login]
            else:
                storage[login].count += 1

    def generate_requests(self, *a, **kw):
        request = Request(*a, **kw)
        yield request

        while 'next' in request.paginate:
            next = request.paginate['next']
            kwargs = request.kwargs.copy()
            params = kwargs.pop('params', {})
            params['page'] = next
            request = Request(request.method, request.url, *request.args,
                              params=params, **kwargs)
            yield request

    async def request(self, *args, **kwargs):
        for request in self.generate_requests(*args, **kwargs):
            async with self.single_request(request) as resp:
                links = resp.headers.get('Link', '')
                pages = {name: page for page, name in self.paginate_patt.findall(links)}
                request.paginate = pages
                yield await resp.json()

    def valid_dates(self, item, key_date='date') -> Optional[datetime]:
        """Check date period from config and return date from key if valid or None"""

        date = datetime.strptime(item[key_date], '%Y-%m-%dT%H:%M:%S%z')
        if self.config.since and date < self.config.since:
            return None
        if self.config.until and date > self.config.until:
            return None
        return date
