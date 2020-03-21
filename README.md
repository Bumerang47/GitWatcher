# GitWatcher
Watch bulletin about git repository

### Install
```bash
pip install -e .

python -m git_watcher <URL>  
```

Before run on Pycharm turn on "*Emulate terminal in output console*"  

### Description
```bash
usage: GitWatcher [-h] [--branch BRANCH] [--since SINCE] [--until UNTIL] url

positional arguments:
  url              Repository URL

optional arguments:
  -h, --help       show this help message and exit
  --branch BRANCH  Branch name for analyze commits
  --since SINCE    Get result after this date. This is a timestamp or ISO format
  --until UNTIL    Get result before this date. This is a timestamp or ISO format

```

Example URL: `https://github.com/:owner/:repo/`
