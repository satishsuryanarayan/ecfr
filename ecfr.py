import re
import xml.etree.ElementTree as ET
from typing import List, Set, Dict, Any
from xml.etree.ElementTree import Element

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy: Retry = Retry(
    total=5,
    backoff_factor=1
)

adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
agencies_url: str = "https://www.ecfr.gov/api/admin/v1/agencies.json"
titles_url: str = "https://www.ecfr.gov/api/versioner/v1/titles.json"


def add(cfr_reference: Dict[str, Any], subset: str, subset_dict: Dict[str, Set[str]]) -> None:
    if subset in cfr_reference:
        if subset not in subset_dict:
            subset_dict[subset] = set()
        subset_dict[subset].add(cfr_reference[subset])


def combine(cfr_reference: Dict[str, Any], combined_cfr_references: dict[int, dict[str, Set[str]]]) -> None:
    title: int = cfr_reference["title"]
    if title not in combined_cfr_references:
        combined_cfr_references[title] = dict()

    subset_list: List[str] = ["subtitle", "chapter", "subchapter", "part", "subpart", "section", "appendix"]
    for subset in subset_list:
        if subset in cfr_reference:
            add(cfr_reference, subset, combined_cfr_references[title])


def tags(space: str, element: Element, file: Any):
    if element.text and element.text.strip():
        print(space + "  " + element.text.strip(), file=file)
    for child in element:
        tags(space + "  ", child, file=file)


def run() -> None:
    with requests.session() as session:
        session.mount("https://", adapter)
        session.headers.update({"Accept": "application/json"})

        # Get list of agencies
        response = session.get(agencies_url)
        data: Dict[str, List[Dict[str, Any]]] = response.json()
        agency_list = data["agencies"]

        # Get list of titles
        response = session.get(titles_url)
        data: Dict[str, List[Dict[str, Any]]] = response.json()
        title_list: List[Dict[str, Any]] = data["titles"]

        # Index titles by title number
        title_index: Dict[int, Dict[str, Any]] = dict()
        for title in title_list:
            title_number: int = title["number"]
            title_index[title_number] = title

        """
            Loop through each agency and get the CFR document 
            for it and it's children using cfr_references section
        """
        agency_combined_cfr_references: Dict[str, Dict[int, Dict[str, Set[str]]]] = dict()
        for agency in agency_list:
            combined_cfr_references: Dict[int, Dict[str, Set[str]]] = dict()

            agency_cfr_references = agency["cfr_references"]
            for cfr_reference in agency_cfr_references:
                combine(cfr_reference, combined_cfr_references)

            for child in agency["children"]:
                child_cfr_references = child["cfr_references"]
                for cfr_reference in child_cfr_references:
                    combine(cfr_reference, combined_cfr_references)

            agency_combined_cfr_references[agency["name"]] = combined_cfr_references

    # Get XML documents by agency
    pattern = re.compile("[\\W_]+")
    # client: MongoClient = MongoClient("mongodb://localhost:27017/")
    with requests.session() as session:
        session.mount("https://", adapter)
        session.headers.update({"Accept": "application/xml"})
        # db = client["ecfr"]
        for agency in agency_combined_cfr_references:
            agency_collection = pattern.sub('', agency)
            with open("./docs/" + agency_collection + ".txt", "w") as file:
                combined_cfr_references = agency_combined_cfr_references[agency]
                for title in combined_cfr_references:
                    up_to_date_as_of: str = title_index[title]["up_to_date_as_of"]
                    documents_base_url: str = f"https://www.ecfr.gov/api/versioner/v1/full/{up_to_date_as_of}/title-{title}.xml"
                    subset_dict: Dict[str, Set[str]] = combined_cfr_references[title]
                    for subset_type in subset_dict:
                        for identifier in subset_dict[subset_type]:
                            documents_query: str = f"?{subset_type}={identifier}"
                            documents_url: str = documents_base_url + documents_query
                            print(documents_url)
                            response = session.get(documents_url)
                            root: Element = ET.fromstring(response.content)
                            tags("", root, file=file)


if __name__ == "__main__":
    run()
