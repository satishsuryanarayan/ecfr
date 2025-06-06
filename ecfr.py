import re
import xml.etree.ElementTree as ElementTree
from typing import List, Dict, Any

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


def agency_and_children_cfr_references(agency: Dict[str, Any]) -> List[Dict[str, Any]]:
    combined_cfr_references: List[Dict[str, Any]] = []
    for cfr_reference in agency["cfr_references"]:
        combined_cfr_references.append(cfr_reference)

    for child in agency["children"]:
        for cfr_reference in child["cfr_references"]:
            combined_cfr_references.append(cfr_reference)

    return combined_cfr_references


def cfr_references_by_agency() -> None:
    with requests.session() as session:
        session.mount("https://", adapter)
        session.headers.update({"Accept": "application/json"})

        # Get list of agencies
        response = session.get(agencies_url)
        data: Dict[str, List[Dict[str, Any]]] = response.json()
        agency_list: List[Dict[str, Any]] = data["agencies"]

        # Get list of titles
        response = session.get(titles_url)
        data: Dict[str, List[Dict[str, Any]]] = response.json()
        title_list: List[Dict[str, Any]] = data["titles"]

        # Index titles by title number
        title_index: Dict[int, Dict[str, Any]] = dict()
        for title_dict in title_list:
            title_number: int = title_dict["number"]
            title_index[title_number] = title_dict

    # Extract relevant portions of CFR references for each agency
    with requests.session() as session:
        session.mount("https://", adapter)
        session.headers.update({"Accept": "application/xml"})
        pattern = re.compile('[\\W_]+')
        for agency in agency_list:
            print(agency["name"])
            file_name_for_agency: str = "./docs/" + pattern.sub("", agency["name"]) + ".txt"
            with open(file_name_for_agency, "w") as agency_file:
                combined_cfr_references = agency_and_children_cfr_references(agency)
                for cfr_reference in combined_cfr_references:
                    title: int = cfr_reference["title"]
                    del cfr_reference["title"]
                    up_to_date_as_of: str = title_index[title]["up_to_date_as_of"]
                    xml_url = f"https://www.ecfr.gov/api/versioner/v1/full/{up_to_date_as_of}/title-{title}.xml?"
                    xml_url += "&".join(f"{key}={value}" for key, value in cfr_reference.items())
                    print(xml_url)
                    response = session.get(xml_url)
                    root: ElementTree.Element = ElementTree.fromstring(response.content)
                    for elem in root.iter():
                        if elem.text:
                            print(elem.text, file=agency_file, end="")
                    print(file=agency_file)


if __name__ == "__main__":
    cfr_references_by_agency()
