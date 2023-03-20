from pathlib import Path

import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry


@sleep_and_retry
@limits(calls=1, period=0.25)
def fetch_doc(session, doc_id):
    return session.post(
        "https://mqa-internet.doh.state.fl.us/MQASearchServices/Document",
        {"id": doc_id},
    ).content


def main():
    """Fetches documents related to the cases fetched by case_summaries.py"""

    df = pd.read_csv("case_summaries.csv")
    # Some cases don't have associated document IDs.
    df = df[df.doc_id.notna()]

    # Create parent directory if it doesn't already exist
    doc_dir = Path("docs")
    doc_dir.mkdir(exist_ok=True)

    session = requests.Session()
    for doc_id in df.doc_id:
        doc_path = doc_dir / f"{doc_id}.pdf"
        if doc_path.exists():
            print(f"{doc_path} already exists; skipping.")
            continue
        print(f"Fetching {doc_path}")
        doc_path.write_bytes(fetch_doc(session, doc_id))


main()
