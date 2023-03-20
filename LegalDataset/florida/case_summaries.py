import re
from enum import Enum

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from ratelimit import limits, sleep_and_retry


# Profession IDs used for filtering in the search UI. Derived from
# https://mqa-internet.doh.state.fl.us/MQASearchServices/EnforcementActionsPractitioner/FilterProfessionList
# , which is fetched by Javascript on the search page for generating the filter
# options. See professions.json for an offline copy.
class Profession(Enum):
    MassageTherapist = 1401
    MassageEstablishment = 1402


def all_cases():
    for profession in list(Profession):
        yield from cases_for_profession(profession)


def cases_for_profession(profession):
    """Fetch case summaries filtered to the given profession."""
    session = requests.Session()
    initial_url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/EnforcementActionsPractitioner"
    params = {"SearchDto.Profession": profession.value}

    response = session.post(initial_url, params)
    page_num = 1
    while True:
        print(f"Profession: {profession.name}, page number: {page_num}")
        page = BeautifulSoup(response.text, features="lxml")
        yield from parse_cases(page)
        next_page_link = page.select('a[rel="next"]')
        if not next_page_link:
            return
        response = session.get(
            "https://mqa-internet.doh.state.fl.us" + next_page_link[0]["href"]
        )
        page_num += 1


# Hack; we're rate limiting our parsing of requests rather than the requests
# themselves, which has equivalent timing characteristics for this code.
@sleep_and_retry
@limits(calls=1, period=0.25)
def parse_cases(page):
    for row in page.select("tbody:first-of-type tr"):
        cols = row.find_all("td")
        name, license, profession, city, state, county, case, action, date = cols
        doc_id = None
        # If there's a child 'a' tag, then there's an associated document.
        if case.a and (
            match := re.match(r"ViewDocument\('(.+)'\);", case.a["onclick"])
        ):
            doc_id = match.group(1)

        stripped = lambda tag: tag.get_text(strip=True)

        yield dict(
            # The search results list names in 'Last name, first name' format.
            # If the name is that of a business rather than a person, there ends
            # up being an extra comma at the end of the name.
            name=stripped(name).removesuffix(","),
            license=stripped(license),
            profession=stripped(profession),
            city=stripped(city),
            county=stripped(county),
            case=stripped(case),
            action=stripped(action),
            date=stripped(date),
            doc_id=doc_id,
        )


def main():
    df = DataFrame.from_records(all_cases())
    df.to_csv("case_summaries.csv")


main()
