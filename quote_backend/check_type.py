# -*- coding: utf-8 -*-
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Sea Port data
EXCEL_PATH = r"D:\Planning_data\네오헬리우스MTO\기획자료\MDM\PORT\PORT CODE_DB2_ALIGNED.xls"

df = pd.read_excel(EXCEL_PATH, engine='xlrd')
print('Columns:', df.columns.tolist())
print()
print('Total rows:', len(df))
print()
print('First 20 rows:')
print(df.head(20))
print()
if 'Type' in df.columns:
    print('Type column unique values:')
    print(df['Type'].unique())
    print()
    print('Type value counts:')
    print(df['Type'].value_counts())

