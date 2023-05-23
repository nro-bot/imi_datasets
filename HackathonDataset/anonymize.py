import pandas as pd
from pandas import DataFrame, Series

def export_for_reading(infile='nogit_data/list_of_post_contents.csv'): 
    raw = pd.read_csv(infile)
    readable = ['time_downloaded', 'posted_date_readable', 'src_category_name','thread_page_url', 'author', 'author_url', 'post_text' ]
    df[readable].to_csv('nogit_data/post_data_only.csv', index=False)
    #posts = pd.read_csv('nogit_data/hackathon_ripgrep_post_contents.csv')
    N = 100
    df.sample(n=N, seed=42).to_csv(f'nogit_data/{N}_sample_posts.csv')

def extract_sample():
    print('hi') 


def clean(df):
    # -- Clean of usernames
    # -- Clean of names
    # -- Clean addresses from reviews
    # -- Clean of 

    import re
    import base64
    from pandas.util import hash_pandas_object

    print(df.columns)
    all_authors = pd.Series(df.author.unique())

    # # Regex to match author references in text. Author names can contain regex characters, so they must be escaped.
    # author_re = re.compile('|'.join(re.escape(a) for a in all_authors))

    author_ids = {a: base64.b64encode(a.to_bytes(8, 'big')) for a in hash_pandas_object(all_authors)}
    print(author_ids)


def main():
    import argparse
    import ast

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input filename for raw forum posts CSV file.', type=argparse.FileType('r'), default='posts_raw.csv')
    parser.add_argument('-n', '--num_rows', help='Number of rows to read from input file.', type=int)

    args = parser.parse_args()
    raw = pd.read_csv(args.input, nrows=args.num_rows)

    clean(raw)

main()
