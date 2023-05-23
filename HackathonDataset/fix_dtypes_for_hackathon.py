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


def clean_column_types():
    filepath = Path('nogit_data', 'list_of_post_contents.csv')
    df = pd.read_csv(filepath)

    # -- Drop N/As and duplicates and unused columns
    df = df.dropna(subset='time_downloaded') # drop (my hacky) comment rows 
    df = df.drop_duplicates('post_id') # post_id is unique across entire forum
    df.to_csv('nogit_data/list_of_post_contents_nona.csv', index=False)

    df.drop(columns=['comment', 'join_date_data', 'posted_date_data'], inplace=True)
    df.drop(columns=['num_likers'], inplace=True)

    # -- Turns strings into datetime type
    # use join_date_readable, not join_date_data; the two columns don't quite match up 
    # df.join_date_data.parallel_apply(lambda x: pd.to_datetime(x, unit = 's'))
    df.join_date_readable.parallel_apply(lambda x: pd.to_datetime(x))

    # -- Turn strings into integers
    df = pd.read_csv('nogit_data/list_of_post_contents_nona.csv')
    for column in ['post_ordinal', 'author_num_posts', 'thread_page_num', 'thread_max_pages', 'num_quotes']:
        print(column)
        df = comma_to_int(df, column)

    # -- Remove mixed type from post_text by replacing NaNs with strings 
    f['post_text'] = df['post_text'].fillna('')#, inplace=True)

    def debug_types():
        # -- Check column types 
        with pd.option_context('display.max_rows', 100, 'display.max_columns', 30):
            display(df[df.duplicated(subset=['post_ordinal', 'post_id', 'post_text'])])
        # DtypeWarning: Columns (3) have mixed types. Specify dtype option on import or set low_memory=False.
        for col in df.columns:
            unique_types = df[col].apply(type).unique()
            if len(unique_types) > 1: # if a column is mixed type
                print(col, unique_types)

    # -- Export finally
    readable = ['author', 'posted_date_readable', 'src_category_name', 'thread_page_url', 'post_ordinal', 'post_text']
    df[readable].to_csv('nogit_data/post_data_only.csv', index=False)
    df.to_csv('nogit_data/dtype_fixed_posts_df.pkl')

clean_column_types()