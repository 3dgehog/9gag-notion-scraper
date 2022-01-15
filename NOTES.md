Notes:
URL to figure out chrome version: chrome://version
96.0.4664.110 (Official Build) (arm64)

Currently don't work in headless mode

Selenium browser in docker ref:
https://stackoverflow.com/questions/53657215/running-selenium-with-headless-chrome-webdriver
https://github.com/SeleniumHQ/docker-selenium


RUN:
pipenv run app


Todo:
[x] Detect the spinner and whether I'm at the end rather than slow loading
[x] Add the image or video poster on notion 
[x] log html to file when an error occurs
[] retry system when notion page wasn't able to create or check
[] skip post if unable to find elements
[] Scroll to spinner area when unable to find a stream for 15 scrolls