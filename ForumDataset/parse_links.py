import pandas as pd
from urlextract import URLExtract
from urllib.parse import urlparse

extractor = URLExtract()
extractor.add_enclosure("(", ")")
extractor.add_enclosure("[", "]")


def parse_domain(url):
    # According to
    # https://docs.python.org/3.11/library/urllib.parse.html#urllib.parse.urlparse
    #
    # "Following the syntax specifications in RFC 1808, urlparse recognizes a
    # netloc only if it is properly introduced by ‘//’. Otherwise the input is
    # presumed to be a relative URL and thus to start with a path component."
    #
    # Parse invalid relative URLs as a absolute URL by prepending // if needed.
    if "//" not in url:
        url = "//" + url
    return urlparse(url).netloc


def parse_domains(text):
    return list(set(parse_domain(url) for url in extractor.gen_urls(text)))


def main():
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser()
    parser.add_argument("input_file", type=Path)

    args = parser.parse_args()
    df = pd.read_csv(args.input_file, nrows=10_00)

    domains = df.post_text.dropna().apply(parse_domains)
    print(domains[domains.apply(bool)])


if __name__ == "__main__":
    main()
