# GitWatcher
The simple utility of a dashboard in the console for information from git repository.  
I use only native python libraries (beside aiohttp for requests) yet.  
The decision by requirements from [test task](https://drive.google.com/file/d/1iDiNPnQgr1GkIDNNi-75wfLYx0M939eB/view).  
  
Demonstration of display:  
![](https://image.prntscr.com/image/KadjCbq2Q_Sj2bz-Xw0JrQ.gif)  
  
### Install
```bash
pip install -e .
```
or
```bash
pip install git+https://github.com/Bumerang47/GitWatcher
```
### Run
```bash
python -m git_watcher <URL>  
```

Before run on Pycharm turn on "*Emulate terminal in output console*"  

### Description
```bash
usage: git_wathcer [-h] [--branch BRANCH] [--since SINCE] [--until UNTIL] [--no-debug] [--auth AUTH] [--update-interval UPDATE_INTERVAL] [--size-top-table SIZE_TOP_TABLE] URL

Simple dashboard of git repository

positional arguments:
  URL                   Repository URL

optional arguments:
  -h, --help            show this help message and exit
  --branch BRANCH       branch name for analyze commits [master].
  --since SINCE         get result after this date. This is a timestamp or ISO format [None]
  --until UNTIL         get result before this date. This is a timestamp or ISO format [None]
  --no-debug            disable debug and output to stdout [True].
  --auth AUTH           authenticate for pass or just get more rate limit. Example: `<login>:<pass>` or `<clent_id>:<clent_secret>`
  --update-interval UPDATE_INTERVAL
                        period in second between repeat upload data [600].
  --size-top-table SIZE_TOP_TABLE
                        size table of top contributors [30].
```

Example URL: `https://github.com/:owner/:repo/`
