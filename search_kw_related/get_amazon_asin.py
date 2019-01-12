#!/usr/bin/env python3
# -*- coding: UTF-8  -*-
# @author:zhazekun
# @date: Jan.4th.2019
'''
This script is to
1. get first page asin list from amazon website
based on keywords and maketplace
2. for each asin, craw csi to get non index type

'''
import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from io import StringIO
import re


def get_asin_by_kws(url):
    page = requests.get(url)
    asin_soup = BeautifulSoup(page.text, 'html.parser')
    asin_list = []
    for i in asin_soup.find_all(class_='a-size-small a-link-normal a-text-normal'):
        asin = i['href'].replace('#customerReviews', '').split('/')[-1]
        asin_list.append(asin)
    return asin_list
# get craw product view
def get_attr_based_kws(rows,keywords):
    attr_set = set()
    kw_l = keywords.split('+')
    # print(kw_l)
    for row in rows:
        attr=row.find_all('td')[1].find_all(text=True)[0]
        desc = row.find_all('td')[2].find_all(text=True)[0]
        for kw in kw_l:

            if kw in desc:
                attr_set.add(attr)
    return attr_set
def craw_based_asin(asin,base_url,driver,keywords,marketplace_id):
    driver.get(base_url + "/view?view=simple_product_data_view&item_id="+asin+"&marketplace_id="+marketplace_id\
        +"&customer_id=&merchant_id=&sku=&fn_sku=&gcid=&fulfillment_channel_code=&listing_type=purchasable&submission_id=&order_id=&external_id=&search_string=&realm=USAmazon&stage=prod&domain_id=&keyword=&submit=Show")
    table_list=driver.find_element_by_id('productdata')
    table_list_text = table_list.get_attribute('innerHTML')
    soup = BeautifulSoup(table_list_text, 'html.parser')
    table_body = soup.find('tbody')
    rows = table_body.find_all('tr')
    attr_set = get_attr_based_kws(rows,keywords)
#     print(attr_set)
    return attr_set
def get_attr_type(marketplace_id,region_id):
    pattern = re.compile('\s+')
    file_name = marketplace_id+'_'+region_id+'.html'
    if os.path.exists(file_name):
        f = open(file_name,'r')

        idx_soup = BeautifulSoup(f, "html.parser")
        f.close()
    else:
        idx = requests.get(
            'http://remote-catalog-dumper.amazon.com:8088/exec/csd?environment=production&marketplace=&marketplace='+\
            marketplace_id+'&region='+region_id+'&data-type=pec&asin=foo&filter=&server=&port=&review-family=&.submit=submit')
        idx_soup = BeautifulSoup(idx.text, 'html.parser')
        with open(file_name, 'w') as f:
            f.write(idx.text)
    idx_data = idx_soup.find_all('p')[3].find_all('pre')[1].text
    idx_data = idx_data.split('\n')
    attr_dict = {}
    for i in range(3, len(idx_data)):
        attr_list = pattern.split(idx_data[i])
        if len(attr_list) > 2:
            attr_name = attr_list[2]
            atrr_type = attr_list[0]
            if attr_name not in attr_dict:
                attr_dict[attr_name] = atrr_type
    return idx_data,attr_dict
if __name__ == '__main__':
    keywords_list = []
    kw_file = input(r'Please input kw file:')


    if os.path.exists(kw_file):

        with open(kw_file,'r') as kw_list:
            for line in kw_list:
                keywords_list.append(line.replace('\n',''))
    else:
        print('Please input a kw file')


    country_code = input('country_code:').lower()
    '''
    market place id active from csi
    1 (www.amazon.com),3 (www.amazon.co.uk),6 (www.amazon.jp),7 (www.amazon.ca),3240 (www.amazon.cn),\
    31200 (cba.sandbox.amazon.com),31320 (checkout.stores.amazon.com),44571 (www.amazon.co.in),\
    111172 (www.amazon.com.au),330551 (urmp_1000-prod.amazon.co.uk),338851 (www.amazon.com.tr),\
    771770 (www.amazon.com.mx),877390 (terminated-1426008088www.edealswarehouse.com),877710 (woot.com),\
    926620 (www.quidsi.com),1326140 (terminated-1420623890getultimatenow.hostedbywebsto),1338980 (urmp-1-prod.amazon.com) 
    '''
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    base_url = "http://csi.amazon.com"
    driver = webdriver.Chrome('chromedriver.exe',options=chrome_options)

    us_url="www.amazon.com"
    uk_url="www.amazon.co.uk"
    de_url="www.amazon.de"
    fr_url="www.amazon.fr"
    it_url="www.amazon.it"
    es_url="www.amazon.es"
    eg_url="www.amazon.eg"
    in_url="www.amazon.in"
    jp_url="www.amazon.co.jp"
    ca_url="www.amazon.ca"
    cn_url="www.amazon.cn"
    br_url="www.amazon.com.br"
    mx_url="www.amazon.com.mx"
    au_url="www.amazon.com.au"
    ru_url="www.amazon.ru"
    nl_url="www.amazon.nl"
    ae_url="www.amazon.ae"
    sa_url="www.amazon.sa"
    tr_url="www.amazon.com.tr"
    sg_url="www.amazon.sg"
    region_map={'us':'1','uk':'2','jp':'3','ca':'1','cn':'3','in':'4','au':'3','tr':'2','mx':'1','de':'2','fr':'2','it':'2','es':'2','sg':'3'}
    marketplace_map = {'us':'1','uk':'3','jp':'6','ca':'7','cn':'3240','in':'44571','au':'111172','tr':'338851','mx':'771770','de':'4','fr':'5','it':'35691','es':'44551','sg':'104444012'}
    urls ={"us":us_url,"uk":uk_url,"de":de_url,\
           "fr":fr_url,"it":it_url,"es":es_url,\
           "eg":eg_url,"in":in_url,"jp":jp_url,\
           "ca":ca_url,"cn":cn_url,"br":br_url,\
           "mx":mx_url,"au":au_url,"ru":ru_url,"nl":nl_url,"ae":ae_url,"sa":sa_url,"tr":tr_url,"sg":sg_url}
    asin_list=[]
    marketplace_id = marketplace_map[country_code]
    region_id = region_map[country_code]
    print("Get attr from remote catalog dumper,and saved to",marketplace_id+"_"+region_id+'.html')
    idx_data, attr_dict = get_attr_type(marketplace_id,region_id)
    result_set=set()
    output = open('output.txt','w')
    for kw in keywords_list:

        result_set=set()

        non_index_attr = set()
        print('Get asin list from amazon website')
        kw =kw.strip()
        kw = kw.replace(' ','+')
        url = 'https://'+urls[country_code]+'/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords='+kw
        # print(url)
        try:
            asin_list = get_asin_by_kws(url)
        except:
            print("Can't get asin from url",kw,url)
            continue
        print('Asins were fetched,get attributes from csi ')
        if asin_list:
            for asin in asin_list:
                try:
                    result_set = result_set | craw_based_asin(asin, base_url, driver,kw,marketplace_id)
                #         print('result ',result_set)
                except:
                    continue

        if result_set:
            print(result_set)
            for attr in result_set:
                if attr == 'item_name' or attr == 'brand':
                    continue
                flag = False
                if attr in attr_dict:
                    flag = True
                    if attr_dict[attr] != 'index_type':
                        non_index_attr.add(attr)

                else:
                    for i in idx_data:
                        if attr in i:
                            # @TODO Discuss with xiaoli about the logic
                            if not i.startswith('index_type'):
                                non_index_attr.add(attr)
                            flag = True
                if flag == False:
                    print("Can't find type for attr:", attr)
        if non_index_attr:
            print('For keyword:',kw,',Non indexable attrs are: ',','.join(e for e in non_index_attr))
            output.write('For keyword:'+kw+',Non indexable attrs are: '+','.join(e for e in non_index_attr)+'\n')

        else:
            print('No Non indexable attrs for keyword:',kw)

    output.close()
    driver.quit()
