import requests
import os
import csv
import json
from bs4 import BeautifulSoup


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
    for year in range(2020, 2022):
        pre_param = {
            'year': year
        }
        models = send_request(url=model_url, params=pre_param)
        for model in models:
            model_name = model['name']
            model_value = model['value']
            params = {
                'year': year,
                'modelName': model_name,
                'modelVal': model_value
            }
            features_res = send_request(url=feature_url, params=params)['Features']
            for feature_res in features_res:
                if feature_res['Type'] == 'youtube' or feature_res['Type'] == 'video':
                    title = feature_res['Title']
                    description = feature_res['Text']
                    ind_url = 'https://owners.honda.com' + feature_res['Url']
                    soup = parse_url(url=ind_url)
                    feature_items = soup.find_all(attrs={'class': 'feature-item'})
                    for feature_item in feature_items:
                        if feature_item.findChild().name == 'svg':
                            if 'video' in feature_item.findChild().use['xlink:href'] or 'youtube' in feature_item.findChild().use['xlink:href']:
                                anchor_url = 'https://owners.honda.com' + feature_item.a['href']
                                line = [year, 'Honda', model_name, '', title, description, anchor_url]
                                if line not in total:
                                    total.append(line)
                                    print(line)
                                    write(lines=[line], file_name='Honda_How_To.csv')
                        else:
                            anchor_url = 'https://owners.honda.com' + feature_item.a['href']
                            anchor_soup = parse_url(anchor_url)
                            feature_items = anchor_soup.find_all(attrs={'class': 'feature-item'})
                            for item in feature_items:
                                if 'video' in item.findChild().use['xlink:href'] or 'youtube' in \
                                        item.findChild().use['xlink:href']:
                                    an_url = 'https://owners.honda.com' + item.a['href']
                                    line = [year, 'Honda', model_name, '', title, description, an_url]
                                    if line not in total:
                                        total.append(line)
                                        print(line)
                                        write(lines=[line], file_name='Honda_How_To.csv')


if __name__ == '__main__':
    model_url = 'https://owners.honda.com/data/GetModelsByYear'
    feature_url = 'https://owners.honda.com/data/GetVehicleFeaturesByYearAndModel'
    main()
