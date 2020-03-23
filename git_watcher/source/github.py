import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin

from .abstract import AbstractProvider, Throttler, Request
from ..objects import Contributor


class GitHub(AbstractProvider):
    base_url = 'https://api.github.com/'
    paginate_patt = re.compile(r'&page=(?P<n>\d+)>;\srel="(?P<name>\w+)"')

    throttler = Throttler(interval=0.3)

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
        self.contributors = _contributors

    def merge_contributors(self, new_list: List, main_set: Dict):
        res = main_set.copy()
        for v in new_list:
            if v.email in main_set:
                res[v.email].count += v.count
            else:
                res[v.email] = v
        return res

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

    def parse_contributors(self, data, storage):
        for commit in data:
            git_author = commit['commit']['author']
            hub_author = commit.get('author')
            if not hub_author:
                # this a commit from local repository without github account
                login = git_author.get('email')
            else:
                login = hub_author.get('login')

            c_date = datetime.strptime(git_author['date'], '%Y-%m-%dT%H:%M:%S%z')
            if self.config.since and c_date < self.config.since:
                continue
            if self.config.until and c_date > self.config.until:
                continue

            if login not in storage:
                storage[login] = Contributor(login=login,
                                             email=git_author['email'],
                                             count=1)
                yield storage[login]
            else:
                storage[login].count += 1
