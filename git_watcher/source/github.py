from .abstract import AbstractProvider, Throttler


class GitHub(AbstractProvider):
    base_url = 'https://api.github.com/'
    throttler = Throttler(interval=0.3)

    @property
    def path_commits(self):
        return f'/repos/{self.owner}/{self.repo}/commits'

    def parse_contributors(self, data):
        _data = {}

        for commit in data:
            committer = commit['commit']['committer']
            date = committer['date']
            email = committer['email']

            if self.config.since and date > self.config.since:
                continue
            if self.config.until and date < self.config.until:
                continue

            if email not in _data:
                _data[email] = self.new_contributor(committer)
                yield _data[email]
            else:
                _data[email].count += 1
