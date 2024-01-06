# Notes

URL to figure out chrome version: chrome://version
96.0.4664.110 (Official Build) (arm64)

Get the chromedriver here:
https://chromedriver.chromium.org/downloads

Currently don't work in headless mode

Selenium browser in docker ref:
https://stackoverflow.com/questions/53657215/running-selenium-with-headless-chrome-webdriver
https://github.com/SeleniumHQ/docker-selenium


## RUN
pipenv run app


## TODO

- [x] Detect the spinner and whether I'm at the end rather than slow loading
- [x] Add the image or video poster on notion 
- [x] log html to file when an error occurs
- [x] retry system when notion page wasn't able to create or check
- [x] skip post if unable to find elements
- [x] ~~Scroll to spinner area when unable to find a stream for 15 scrolls~~ All scrolls now scrolls to loader element
- [x] Remember session (prevents logining in over and over)
- [x] headless
- [x] Save meme to a folder
- [x] Check notion database uses correct properties
- [x] Give notion the ability to update an existing meme
- [x] Skip if already exists
- [ ] Stop when found meme that exists
- [ ] Add a peronal WebDAV link to notion page
- [ ] Detected when logged out again (like page can be accessed without logging in)