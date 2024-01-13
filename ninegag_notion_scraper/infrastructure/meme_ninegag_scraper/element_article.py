import os
import logging
from typing import List
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement


logger = logging.getLogger('app.9gag')


class Base:
    @staticmethod
    def get_item_id_from_url(url: str) -> str:
        item_id = os.path.basename(url)
        return item_id

    @staticmethod
    def get_tags_from_article(article: WebElement) -> List[str | None]:
        try:
            tags_element = article.find_elements(
                By.CSS_SELECTOR,
                'article > div.post-tags > a'
            )
            tags = [
                x.get_attribute('innerHTML')
                for x in tags_element
            ]
        except NoSuchElementException as error:
            logger.warning('Unable to find post_section in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        return tags

    @staticmethod
    def get_cover_photo_from_article(article: WebElement) -> str:
        cover_photo = None

        try:
            cover_photo = article.find_element(
                By.CSS_SELECTOR, '.post-container * > picture > img'
            ).get_attribute('src')
        except NoSuchElementException:
            pass

        try:
            cover_photo = article.find_element(
                By.CSS_SELECTOR, '.post-container * > video'
            ).get_attribute('poster')
        except NoSuchElementException:
            pass

        if not cover_photo:
            logger.warning("Unable to find cover photo\n %s",
                           article.get_attribute('outerHTML')
                           )
            raise NoSuchElementException("Unable to find cover photo")

        return cover_photo

    @staticmethod
    def get_title_from_article(article: WebElement) -> str:
        raise NotImplementedError

    @staticmethod
    def get_file_url_from_article(article: WebElement) -> str:
        try:
            post_view_element = article.find_element(
                By.CLASS_NAME, 'post-view')
        except NoSuchElementException as error:
            logger.warning('Unable to find post_view in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        video_url = None
        image_url = None

        try:
            video_url = post_view_element.find_element(
                By.XPATH,
                "video/source[@type='video/mp4']").get_attribute('src')
        except NoSuchElementException:
            pass

        try:
            image_url = post_view_element.find_element(
                By.XPATH,
                "picture/img").get_attribute('src')
        except NoSuchElementException:
            pass

        if not video_url and not image_url:
            logger.warning('Unable to find image or video in post view')
            raise NoSuchElementException
        if video_url and image_url:
            logger.warning('Found both an image and a video... not possible')
            raise ValueError

        if video_url:
            return video_url
        else:
            assert image_url
            return image_url


class StreamArticle(Base):
    @staticmethod
    def get_url_from_article(article: WebElement) -> str:
        try:
            url = article.find_element(
                By.CSS_SELECTOR,
                'article > header > a').get_attribute('href')
        except NoSuchElementException as error:
            logger.warning('Unable to find title in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        assert url
        return url

    @staticmethod
    def get_title_from_article(article: WebElement) -> str:
        try:
            title = article.find_element(
                By.CSS_SELECTOR,
                'article > header > a').text
        except NoSuchElementException as error:
            logger.warning('Unable to find title in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        return title


class SinglePageArticle(Base):
    @staticmethod
    def get_title_from_article(article: WebElement) -> str:
        try:
            title = article.find_element(
                By.CSS_SELECTOR,
                'article > header > h1').text
        except NoSuchElementException as error:
            logger.warning('Unable to find title in article %s',
                           article.get_attribute('outerHTML')
                           )
            raise error

        return title
