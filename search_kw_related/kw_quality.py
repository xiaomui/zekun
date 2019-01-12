#!/usr/bin/env python
# coding: utf-8

# @author: zhazekun

import pandas as pd
import re
fname = input("please input file: ")
A9_sheet = input('please input A9 sheet: ')
catalog_kw_sheet = input('please input catalog_kw_sheet:')
fname=fname.replace('"','')
if not A9_sheet:
    A9_sheet = 'A9_top_keyword'
if not catalog_kw_sheet:
    catalog_kw_sheet = 'catalog_keyword'
#sample kw list.xlsx,,catalog_keyword
A9_df = pd.read_excel(fname,sheet_name=A9_sheet)
catalog_kw_df = pd.read_excel(fname,sheet_name=catalog_kw_sheet)

print('Processing Data')

## drop na
A9_df = A9_df.dropna()
catalog_kw_df = catalog_kw_df.dropna()

stop_df = pd.read_csv('stop_list.txt',header=None)

stop_list = stop_df[0].values

A9_df.columns = ['Keywords']
catalog_kw_df.columns=['asin','Keywords']

def get_dict_stopw(kw_df):
    kw_dict ={}
    pattern= re.compile('[^\w]')
    for kws in kw_df.Keywords:
        kws = str(kws)
        kws = re.sub(pattern,r' ',kws)
        
        if kws:
            kws = kws.split(' ')
            for kw in kws:
                if kw:
                    if kw not in stop_list:
                        if kw in kw_dict:
                            kw_dict[kw] += 1
                        else:
                            kw_dict[kw] = 1

        
    return kw_dict

kw_dict_stopw = get_dict_stopw(A9_df)

catalog_dict_stopw = get_dict_stopw(catalog_kw_df)


kw_dict_df = pd.DataFrame(list(kw_dict_stopw.items()),columns=['kw','count'])
catalog_dict_df = pd.DataFrame(list(catalog_dict_stopw.items()),columns=['kw','count'])
#further step: stem words



# # Check coverage

print('Join two dicts')

joint_df = pd.merge(kw_dict_df,catalog_dict_df,on='kw')

joint_df.columns = ['kw','a9_count','catalog_count']

joint_df=joint_df.sort_values(['catalog_count'],ascending=[False])

writer = pd.ExcelWriter('kw_coverage.xlsx', engine = 'xlsxwriter')

joint_df.to_excel(writer,index=False,sheet_name='join')

print('Finding words in A9 but not in catalog keywords')
kws = catalog_dict_df.kw.values
disjoin = kw_dict_df[~kw_dict_df['kw'].isin(kws)]

disjoin.columns=['kw','A9_count']


disjoin = disjoin.sort_values(['A9_count'],ascending=[False])



disjoin.to_excel(writer,index=False,sheet_name='in_A9_not_in_catalog')
writer.save()
writer.close()
print('done')







