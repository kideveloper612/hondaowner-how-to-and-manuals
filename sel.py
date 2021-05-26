import csv
import time
import pandas as pd
import argparse
import spotipy
import requests
from datetime import datetime
from lxml import html
from spotipy.oauth2 import SpotifyClientCredentials

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.maximize_window()
    # driver.execute_script("window.open()")
    return driver


def read_file():
    with open(file='Honda_How_To.csv', encoding='utf-8', mode='r') as csv_file:
        rows = list(csv.reader(csv_file))
    return rows


def wait_for(driver, condition):
    delay = 10  # seconds
    try:
        return WebDriverWait(driver, delay).until(EC.presence_of_element_located(condition))
    except TimeoutException:
        pass


def write(lines, file_name):
    with open(file=file_name, encoding='utf-8', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)


def send_request(url):
    res = requests.get(url=url)
    return BeautifulSoup(res.text, 'html5lib')


def main():
    lines = read_file()
    driver = get_driver()
    for line in lines:
        try:
            video_url = line[6]
            driver.get(video_url)
            time.sleep(5)
            driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
            video_link = driver.find_element_by_tag_name('video').get_attribute('src')
            # thumb_link = driver.find_element_by_css_selector('.mwEmbedPlayer img').get_attribute('src')
            thumb_link = driver.find_element_by_css_selector('.ytp-cued-thumbnail-overlay-image').get_attribute('style')
            line = [line[0], line[1], line[2], line[3], line[4], line[5], video_link, thumb_link]
            print(line)
            write(lines=[line], file_name='A.csv')
        except Exception as e:
            print(e)
            continue

    if driver:
        driver.quit()


def get_description():
    lines = read_file()
    for line in lines:
        titile_des = []
        url = line[6]
        soup = send_request(url=url)
        bread_soup = soup.find(attrs={'class': 'feature-bread-crumbs'})
        print(bread_soup, url)
        if bread_soup:
            spans = bread_soup.find_all('span')
            for span in spans:
                span.decompose()
            navs = bread_soup.find_all('a')
            print(navs)
            for nav in navs:
                titile_des.append(nav.text.strip())
                nav.decompose()
            titile_des.append(bread_soup.text.strip())
            print(titile_des)
            exit()
            if len(titile_des) >= 2:
                title = titile_des[-2]
                description = titile_des[-1]
            elif len(titile_des) == 1:
                title = titile_des[0]
                description = ''
            else:
                title = ''
                description = ''
            new_line = [line[0], line[1], line[2], '', title, description, url]
            print(new_line)
            write(lines=[line], file_name='Save.csv')


def get_description_sel():
    lines = read_file()
    driver = get_driver()
    for line in lines:
        title_des = []
        url = line[6]
        driver.get(url=url)
        ele = driver.find_element_by_class_name('feature-bread-crumbs')
        if ele:
            navs = ele.find_elements_by_tag_name('a')
            for nav in navs:
                title_des.append(nav.text.replace('<', '').strip())
                js = "var aa=document.getElementsByClassName('feature-bread-crumbs')[0]; var anchors = aa.getElementsByTagName('a'); for (let i=0; i < anchors.length; i++) {anchors[i].parentNode.removeChild(anchors[i]);}"
                driver.execute_script(js)
            title_des.append(ele.text.replace('<', '').strip())
            print(title_des)
            if len(title_des) >= 2:
                title = title_des[-2]
                description = title_des[-1]
            elif len(title_des) == 1:
                title = title_des[0]
                description = ''
            else:
                title = ''
                description = ''
            new_line = [line[0], line[1], line[2], '', title, description, url]
            print(new_line)
            write(lines=[new_line], file_name='Save.csv')
    driver.quit()


if __name__ == '__main__':
    main()
