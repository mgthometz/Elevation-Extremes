#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 14:49:28 2018

@author: mattthometz
"""
import pandas as pd
from requests import get
from bs4 import BeautifulSoup

raw_html=get('https://en.wikipedia.org/wiki/List_of_elevation_extremes_by_country')
soup=BeautifulSoup(raw_html.text,'lxml')

html_table=soup.find_all('table')[0]

def parse_html_table(table):
    n_rows=0
    n_columns=0
    column_names=[]
    #Find row tags
    tr_tags=table.find_all('tr')
    #Find column tags
    th_tags=table.find_all('th')
    
    for th in th_tags:
        column_names.append(th.get_text().rstrip('\n'))
    #First row is column names
    n_rows=len(tr_tags)-1
    df=pd.DataFrame(columns=column_names,index=range(0,n_rows))
    row_pos=0
    for row in tr_tags:
        col_pos=0
        columns=row.find_all('td')
        for col in columns:
            df.iloc[row_pos,col_pos]=col.get_text().rstrip('\n').split('[')[0]
            col_pos+=1
        if len(columns)>0:  #First row is column names, no td tags
            row_pos+=1
    return df

elevations=parse_html_table(html_table)

#Split and clean up columns

to_split_cols=['Maximum elevation','Minimum elevation','Elevation span']

for idx in elevations.index:
    for col in to_split_cols:
        try:
            val=elevations.loc[idx,col]
            split=val.split('m')
        
            col_meters=split[0].rstrip().replace(',','')
            elevations.loc[idx,col+' (m)']=col_meters.rstrip()
            col_feet=split[1].replace(',','').split('ft')[0].rstrip()
            elevations.loc[idx,col+' (ft)']=col_feet
        except IndexError:
            if 'sea level' in val:
                elevations.loc[idx,col+' (m)']=0
                elevations.loc[idx,col+' (ft)']=0
            else:
                print(elevations.iloc[idx,:])
 
#Removing code for red text from beginning of negative minimum elevations               
for idx in elevations.index:
    try:
        split=elevations.loc[idx,'Minimum elevation (m)'].split('♠')
        elevations.loc[idx,'Minimum elevation (m)']=split[1].replace('−','-')
    except (IndexError, AttributeError):
        pass   

#Replacing fake negative sign with actual negative sign
for idx in elevations.index:
    try:
        change=elevations.loc[idx,'Minimum elevation (ft)'].replace('−','-')
        elevations.loc[idx,'Minimum elevation (ft)']=change
    except (IndexError, AttributeError):
        pass 
    
#Change to columns to float       
to_numerical_columns=['Maximum elevation (m)','Maximum elevation (ft)','Minimum elevation (m)','Minimum elevation (ft)','Elevation span (m)','Elevation span (ft)']

for idx in elevations.index:
    for col in to_numerical_columns: 
        num=elevations.loc[idx,col]
        try:
            elevations.loc[idx,col]=float(num)
        except:
            print(elevations.loc[idx,col])

#Remove leading white space from country column
elevations['Country or region']=elevations['Country or region'].map(lambda x: x.strip())

#Drop unecessary columns
elevations.drop(axis=1,inplace=True,columns=['Maximum elevation','Minimum elevation','Elevation span'])

#Export to Excel
elevations.to_excel('elevations.xls')