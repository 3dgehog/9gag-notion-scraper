# 9GAG Notion Scraper

A small tool that takes a 9gag stream and translates it to a notion database

## Setup

**Required ENV**

A  Notion API Token
```
NOTION_TOKEN=
```

A Notion Database id (which needs to be setup ahead of time)
```
NOTION_DATABASE=
```

The 9GAG URL to want to scrape
```
9GAG_URL=https://9gag.com/u/username/likes
```

**Optional ENV**

Login credentials if you need to login first
```
USERNAME=
PASSWORD=
```

If you want to start scraping a specific stream (Default = 0)
```
START_STREAM = 0
```

**Docker**

The following ENV is required if you do not want the container to run only once (Default = 0). This is the time in seconds between each runs
```
RUN_INTERVAL_SECONDS = 0
```

You need to point the remote selenium server for this script to work, using this Env (Default = 0)
```
WEBDRIVER_URL = <url>
```
