"""
    'Tul' to scrape dges licenciaturas

    Can be used to scrape licenciaturas with certain access exams
    eg. (Matemática A and Português)

    Usage: python dges_lic_scraper output_file

    requirements:
    requests
    beautifulsoup4
"""

import sys
import json
import requests
from bs4 import BeautifulSoup

import dges_lic_constants as CONST

def main() -> int:
    """dges scraper entry point"""

    # Scrape degrees
    scraped_degrees = scrape_degrees("https://www.dges.gov.pt/guias/indcurso.asp?letra=E")

    # Apply filters
    access_exam_filter = []
    degree_name_filter = []
    filtered_degrees = apply_fitlers(scraped_degrees, access_exam_filter, degree_name_filter)

    # Show/Export info
    if len(sys.argv) > 1:
        out_file = open(sys.argv[1], "w")
        json.dump(filtered_degrees, out_file, indent=2, ensure_ascii=False)
        out_file.close()
        print(f"[RESULT] Dumped into {sys.argv[1]}")
    else:
        print(filtered_degrees)

    return 0

def scrape_degrees(url: str):
    """Scrape degrees from dges url"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    degrees = []
    current_degree = None

    # Find all degree divs (box10)
    degree_boxes = soup.find_all('div', class_=CONST.DEGREE_DIV_CLASS)

    for degree_box in degree_boxes:
        # Get degree code and name from 'lin-area-c1' and 'lin-area-c2'
        degree_code = degree_box.find('div', class_=CONST.DEGREE_CODE_DIV_CLASS).text.strip()
        degree_name = degree_box.find('div', class_=CONST.DEGREE_NAME_DIV_CLASS).text.strip()
        print(f"[DEGREE] Processing {degree_code} - {degree_name}")

        # Initialize a new degree entry
        current_degree = {
            CONST.DEGREE_CODE: degree_code,
            CONST.DEGREE_NAME: degree_name,
            CONST.UNIVERSITIES: []
        }
        
        # Get the next sibling which should be the list of universities
        sibling = degree_box.find_next_sibling()

        while sibling and CONST.UNIVERSITY_LINE_DIV_CLASS in sibling.get('class', []):
            # Uni info
            uni_code = sibling.find('div', class_=CONST.UNIVERSITY_CODE_DIV_CLASS).text.strip()
            uni_name = sibling.find('div', class_=CONST.UNIVERSITY_NAME_DIV_CLASS).text.strip()
            uni_link = compute_uni_link(degree_code, uni_code)
            uni_metadata = scrape_uni_metadata(uni_link)

            current_degree[CONST.UNIVERSITIES].append({
                CONST.UNI_CODE: uni_code,
                CONST.UNI_NAME: uni_name,
                CONST.UNI_LINK: uni_link,
                CONST.UNI_METADATA: uni_metadata
            })
            
            sibling = sibling.find_next_sibling()

        degrees.append(current_degree)

    return degrees

def scrape_uni_metadata(uni_link: str) -> dict:
    """Scrapes various type of 'metadata' from a university-degree specific dges page"""
    metadata = dict()
    response = requests.get(uni_link)
    soup = BeautifulSoup(response.content, 'html.parser')

    inside_div = soup.find('div', class_=CONST.UNIVERSITY_METADATA_DIV_CLASS)
    if inside_div:
        text = inside_div.get_text()

        # Extract the CNAEF code, which is in the format 'Área CNAEF: <code> <name>'
        cnaef_start = text.find(CONST.CNAEF_SEARCH_VALUE) + len(CONST.CNAEF_SEARCH_VALUE)
        if cnaef_start != -1:
            cnaef_end = text.find('Duração', cnaef_start)
            cnaef_code = text[cnaef_start:cnaef_end].strip()
            metadata[CONST.CNAEF_CODE] = cnaef_code

    return metadata

def compute_uni_link(degree_code: int, uni_code: int) -> str:
    """Computes dges university link"""
    return f"https://www.dges.gov.pt/guias/detcursopi.asp?codc={degree_code}&code={uni_code}"

def apply_fitlers(degrees: list, access_exams: list|None, degree_name: list|None):
    """Applies filters on a given degrees dict"""
    filtered = degrees
    if degrees is None or len(degrees) == 0:
        raise ValueError(f"apply_filters: degree dict is invalid ({degrees})")

    if not access_exams is None and len(access_exams) > 0:
        ...

    if not degree_name is None and len(degree_name) > 0:
        ...

    return filtered

if __name__ == "__main__":
    ret: int = main()
    assert isinstance(ret, int)
    sys.exit(ret)
