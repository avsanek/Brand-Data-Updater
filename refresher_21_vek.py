import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_excel('manufacturer.xlsx')  # Loading data from Excel into DataFrame
column_name = df['name']  # take the brand column


def time_out(response, index):  # if we get any status other than 200, we take a break
    print(response.status_code, response, 'time_out', index + 1)
    time.sleep(61)


for index, value in enumerate(column_name):  # we use enumerate to make it easier to access the necessary columns
    while True:                                 # to update information in the future
        url_api_items = f'https://search.21vek.by/api/v2.0/search/suggest?q={value}&mode=desktop&v=1.0.0'  # it's a drop-down list of items
        response = requests.get(url_api_items)
        if response.status_code == 200:
            need_item = response.json()
            if need_item['data'][5]['items']:  # check whether is any item on the list
                need_item_with_info = f"https://www.21vek.by/{need_item['data'][5]['items'][0]['url']}"  # take url of tirst item
                response = requests.get(need_item_with_info)
                if response.status_code == 200:
                    response_html = response.text
                    soup = BeautifulSoup(response_html, 'lxml')  #  we use BeautifulSoup to make it easier to find the "manufacturer and importer" we need
                    title_item = soup.find('title').text.split()  #  We get the name of the brand item
                    if value.lower() == title_item[0].lower():  # usually the brand goes the very first word and we compare it with the brand from our file
                        need_info = soup.find('ul', class_='cr-info-spec columns__nowrap')
                        need_info = need_info.find_all('li')  # here we get all the information we need about "manufacturer and importer"
                        df.loc[index, 'izgotov'] = need_info[1].text  # updating manufacturer information
                        df.loc[index, 'import'] = need_info[2].text  # updating importer information
                    else:
                        df.loc[index, 'izgotov'] = 'Не нашёл'  # if the brand from our file does not match the brand on the site, then we write that we did not find it
                else:
                    time_out(response, index)  # if we get any status other than 200, we take a break
                    continue
            else:
                df.loc[index, 'izgotov'] = 'Не нашёл'  #  if there is no such brand on the site, then we write that we have not found it
            if not (index + 1) % 100:  # due to the fact that there may be many unexpected errors, I decided to update the file every 100 changes
                print(index + 1)
                df.to_excel('manufacturer.xlsx', index=False)
            break  # move on to another brand :)
        else:
            time_out(response, index)  # if we get any status other than 200, we take a break

df.to_excel('manufacturer.xlsx', index=False)  # When we've gone through all the brands, save the changes
