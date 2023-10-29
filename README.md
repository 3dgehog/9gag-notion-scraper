# 9GAG Notion Scraper

A small tool that takes a 9gag stream and translates it to a notion database

## Setup

Download chrome driver from: https://googlechromelabs.github.io/chrome-for-testing/

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