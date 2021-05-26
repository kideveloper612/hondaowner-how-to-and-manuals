import requests
import re
import csv
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.maximize_window()
    # driver.execute_script("window.open()")
    return driver


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


def send_request(url, params={}):
    headers = {
        'user-agent': 'Mozilla/5.0'
    }
    res = requests.get(url=url, headers=headers, params=params)
    return json.loads(res.content)


def parse_url(url):
    headers = {
        'user-agent': 'Mozilla/5.0'
    }
    res = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(res.content, features='html5lib')
    return soup


def main():
    total = []
    driver = get_driver()

    for year in range(2021, 2022):
        pre_param = {
            'year': year
        }
        models = send_request(url=model_url, params=pre_param)
        for model in models:
            model_name = model['name']
            model_value = model['value']

            model_request = 'https://owners.honda.com/vehicles/information/{}/{}'.format(year, model_value)
            model_soup = parse_url(model_request)

            items = model_soup.select(".all-guides .lnk-feature-name")
            for item in items:
                title = item.text.strip()
                item_link = 'https://owners.honda.com' + item['href']

                item_soup = parse_url(item_link)
                sub_items = item_soup.select(".feature-item")
                for sub_item in sub_items:
                    description = re.sub(' +', ' ', sub_item.text.strip())
                    if 'video' in sub_item.findChild().use['xlink:href'] or 'youtube' in sub_item.findChild().use['xlink:href']:
                        anchor_url = 'https://owners.honda.com' + sub_item.a['href']
                        driver.get(anchor_url)
                        time.sleep(5)
                        video_link = driver.find_element_by_tag_name('iframe').get_attribute('src')
                        driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
                        thumb_link = driver.find_element_by_css_selector(
                            '.ytp-cued-thumbnail-overlay-image').get_attribute('style').replace\
                            ("background-image: url(\"", "").replace(");\"", "")
                        line = [year, 'Honda', model_name, title, description, video_link, thumb_link]
                        if line not in total:
                            total.append(line)
                            print("video ", line)
                            write(lines=[line], file_name='Honda_How_To.csv')
                    elif 'pdf' in sub_item.findChild().use['xlink:href']:
                        anchor_url = 'https://owners.honda.com' + sub_item.a['href']

                        anchor_soup = parse_url(anchor_url)
                        pdf_url = 'https://owners.honda.com' + anchor_soup.select(".pdf-info a")[0]['href'].replace(
                            '/utility/download?path=', ''
                        )
                        line = [year, 'Honda', model_name, title, description, pdf_url]
                        if line not in total:
                            total.append(line)
                            print("pdf ", line)
                            write(lines=[line], file_name='Honda_Manuals.csv')


if __name__ == '__main__':
    model_url = 'https://owners.honda.com/data/GetModelsByYear'
    feature_url = 'https://owners.honda.com/data/GetVehicleFeaturesByYearAndModel'
    main()
