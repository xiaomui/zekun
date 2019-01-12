#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
# @author:zhazekun
# @date: 28/12/2018
Purpose: craw result files based on source and target countries from ags dashboard
http://int-xxr.serv.rbspek.com/agsdashboard/console.html and export data to user defined
local path.
'''

from tkinter import *
import requests
import pandas as pd
import os
from tkinter import messagebox
import datetime
'''
Main function
'''


def check_and_run_dashboard():
    # check file exists
    source = e1.get().lower()
    target = e2.get().lower()
    output = e3.get().lower()

    #run check file button
    print('Checking files')

    check_file = requests.post('http://int-xxr.serv.rbspek.com/agsdashboard/checkDefectiveAsinFile.spring', \
                               data={'sourceCountry':source, 'targetCountry': target})

    check_file_text = check_file.text


    messagebox.showinfo(title='Check file', message=check_file.text)
    if 'result_null.txt' in check_file_text and 'result_.txt' in check_file_text \
            and 'result_N.txt' in check_file_text and 'result_Y.txt' in check_file_text:
        print(check_file_text)
    else:
        raise Exception('Wrong check file exception'+check_file_text)
    #run run
    print('Start run button')
    r = requests.post("http://int-xxr.serv.rbspek.com/agsdashboard/mapDefectiveAsin.spring", \
                      data={'sourceCountry': source, 'targetCountry': target})

    if r.text == '["success"]':
        messagebox.showinfo(title='Run result', message='Succeed')

        result_null = requests.get('http://int-xxr.serv.rbspek.com/agsdashboard/downloadFile.spring?fileName=result_null.txt&sourceCountry='+ \
                                   source+'&targetCountry='+target)
        result_N = requests.get('http://int-xxr.serv.rbspek.com/agsdashboard/downloadFile.spring?fileName=result_N.txt&sourceCountry='+ \
                                source+'&targetCountry='+target)
        result = requests.get('http://int-xxr.serv.rbspek.com/agsdashboard/downloadFile.spring?fileName=result_.txt&sourceCountry='+ \
                              source+'&targetCountry='+target)
        result_Y = requests.get('http://int-xxr.serv.rbspek.com/agsdashboard/downloadFile.spring?fileName=result_Y.txt&sourceCountry='+ \
                                source+'&targetCountry='+target)
        result_null_df = pd.read_csv(pd.compat.StringIO(result_null.text), \
                                     sep=r'\s*\|\s*|\t', engine='python')
        result_N_df = pd.read_csv(pd.compat.StringIO(result_N.text), \
                                  sep=r'\s*\|\s*|\t', engine='python')
        result_df = pd.read_csv(pd.compat.StringIO(result.text), \
                                sep=r'\s*\|\s*|\t', engine='python')
        result_Y_df = pd.read_csv(pd.compat.StringIO(result_Y.text), \
                                  sep=r'\s*\|\s*|\t', engine='python')

        print('Done read all files, output to folder',output)
        current_date = datetime.datetime.now().date().strftime('%y%m%d')
        out_path = os.path.join(output,current_date+source.upper()+'.xlsx')
        writer = pd.ExcelWriter(out_path, engine = 'xlsxwriter')
        result_Y_df.to_excel(writer,index=False,sheet_name='Y')
        result_N_df.to_excel(writer,index=False,sheet_name='N')
        result_null_df.to_excel(writer,index=False,sheet_name='NULL')
        result_df.to_excel(writer,index=False,sheet_name='RESULT')
        writer.save()
        print('Done check & run dashboard.')

        messagebox.showinfo(title='Final', message='Done, File is in '+out_path)
        window.destroy()
    else:
        raise Exception('Error run in Dashboard')
        window.destroy()
        root = Tk()
        msg = Message(root, text = 'Error run in Dashboard')
        msg.pack()
        mainloop()
#     return[result_Y_df,result_N_df,result_null_df,result_df]\

'''

GUI part
'''
if __name__ == '__main__':

    window  = Tk()
    window.geometry('350x150')

    window.title('Craw AGS Dashboard')
    Label(window, text="Source").grid(row=0)
    Label(window, text="Target").grid(row=1)
    Label(window, text="Output full path").grid(row=2)
    e1 = Entry(window)
    e2 = Entry(window)
    e3 = Entry(window,width = 30)
    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2,column=1)

    # res = Message(window,text='check result:').grid(row=4)
    Button(window, text='Submit', command=check_and_run_dashboard).grid(row=5, column=1)

    window.mainloop()
