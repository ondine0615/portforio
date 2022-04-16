import pandas as pd
import glob
import os

files_2=os.path.join("/home/ondine0615/airflow/twitch_csv2/*.csv")
files_list_2=glob.glob(files_2)

df_3=pd.concat(map(pd.read_csv, files_list_2),ignore_index=True,sort=False)
df_3=df_3.fillna('0')
df_3=df_3.astype(int)
df_3=df_3.drop("Unnamed: 0",axis=1)

df_sum=df_3.sum().sort_index()
df_sum.to_csv("/home/ondine0615/workplace/chat-log/csv/df_sum.csv",header=False)