# For hackathon on Mon. May 8th

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from pandarallel import pandarallel
pandarallel.initialize(progress_bar=True)


def comma_to_int(df, col_name):
    df[col_name] = df[col_name].apply(lambda x: x.replace(',', '') if type(x) == str else x) 
    df[col_name] = df[col_name].astype(float)
    df[col_name] = df[col_name].astype(int)
    return df

filepath = Path('nogit_data', 'list_of_post_contents.csv')
df = pd.read_csv(filepath)

# -- Basic cleaning
df = df.dropna(subset='time_downloaded') # drop (my hacky) comment rows 
df = df.drop_duplicates('post_id') # post_id is unique across entire forum
# -- Export
df.to_csv('nogit_data/list_of_post_contents_nona.csv', index=False)

# -- Convert relevant columns to datetime objects 
# df.join_date_data.parallel_apply(lambda x: pd.to_datetime(x, unit = 's')) # ignore this column, it conflicts with the human readable date for unkown reason
df.join_date_readable.parallel_apply(lambda x: pd.to_datetime(x))
# -- Export

# -- Turn columns with commas, into integers
df = pd.read_csv('nogit_data/list_of_post_contents_nona.csv')
for column in ['post_ordinal', 'author_num_posts', 'thread_page_num', 'thread_max_pages', 'num_quotes']:
    print(column)
    df = comma_to_int(df, column)



df = pd.read_csv('nogit_data/list_of_post_contents_nona_nocomma.csv')
# -- Drop some columns we don't need
df.drop(columns=['comment', 'join_date_data', 'posted_date_data'], inplace=True)
# -- Export
df.to_csv('nogit_data/list_of_post_contents_nona_nocomma_nodate.csv', index=False)
# -- Drop this columns too
df.drop(columns=['num_likers'], inplace=True)
# -- Export
df.to_csv('nogit_data/list_of_post_contents_nona_nocomma_nodate_nonumlikers.csv', index=False)

pd.read_csv('nogit_data/list_of_post_contents_nona_nocomma_nodate_nonumlikers.csv')


# check for duplicates
with pd.option_context('display.max_rows', 100, 'display.max_columns', 30):
    display(df[df.duplicated(subset=['post_ordinal', 'post_id', 'post_text'])])

# -- Following code helpful for debugging
# DtypeWarning: Columns (3) have mixed types. Specify dtype option on import or set low_memory=False.

for col in df.columns:
    unique_types = df[col].apply(type).unique()
    if len(unique_types) > 1: # if a column is mixed type
        print(col, unique_types)

# -- Remove mixed type (float) from post_text column
f['post_text'] = df['post_text'].fillna('')#, inplace=True)

# -- Export finally
readable = ['author', 'posted_date_readable', 'src_category_name', 'thread_page_url', 'post_ordinal', 'post_text']
df[readable].to_csv('nogit_data/post_data_only.csv', index=False)