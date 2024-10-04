"""
    'Tul' to scrape dges licenciaturas

    Can be used to scrape licenciaturas with certain access exams
    eg. [Matemática A, Português] or certain degree names [Engenharia, Ciencia]

    Change HARD_*_FILTER globals to switch between `and` and `or` operations for filters
    True = `and`, False = `or`

    Usage: python dges_lic_scraper output_file

    requirements:
    requests
    beautifulsoup4
"""

import re
import sys
import json
import requests
from bs4 import BeautifulSoup

import dges_lic_constants as CONST

HARD_NAME_FILTER = False
HARD_ACCESS_EXAM_FILTER = True

def main() -> int:
    """dges scraper entry point"""

    # Scrape all degrees
    dges_letters =  ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "V", "Z"]
    scraped_degrees = list()
    for letter in dges_letters:
        print(f"#" * 120)
        print(f"[SCRAPING] SCRAPING DEGREES FROM LETTER {letter}")
        print(f"#" * 120)
        letter_degree = scrape_degrees(f"https://www.dges.gov.pt/guias/indcurso.asp?letra={letter}")
        scraped_degrees.extend(letter_degree)

    # Apply filters
    access_exam_filter = [CONST.MAT_A_EXAM, CONST.PT_EXAM]
    degree_name_filter = ["Matemática", "Computação", "Engenharia", "Inteligência Artificial"]
    cnaef_filter = []
    uni_codes_filter = [CONST.ISEP_UNI_CODE, CONST.FEUP_UNI_CODE, CONST.FCUP_UNI_CODE, CONST.UM_UNI_CODE, CONST.IPCA_EST_UNI_CODE, CONST.UC_UNI_CODE]
    print(f"#" * 120)
    print(f"[FILTER] Applying filters:")
    print(f"exams={access_exam_filter}")
    print(f"names={degree_name_filter}")
    print(f"cnaef_filter={cnaef_filter}")
    print(f"uni_codes={uni_codes_filter}")
    filtered_degrees = apply_fitlers(scraped_degrees, access_exam_filter, degree_name_filter, cnaef_filter, uni_codes_filter)

    # Show/Export info
    if len(sys.argv) > 1:
        out_file = open(sys.argv[1], "w")
        info_dict = {
            "Degrees": degree_name_filter,
            "Access Exams": access_exam_filter,
            "CNAEF's": cnaef_filter,
            "University codes": uni_codes_filter
        }
        filtered_degrees.insert(0, info_dict)
        json.dump(filtered_degrees, out_file, indent=2, ensure_ascii=False)
        out_file.close()
        print(f"#" * 120)
        print(f"[RESULT] Dumped into {sys.argv[1]}")
        print(f"#" * 120)
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
        cnaef_start = text.find('Área CNAEF:') + len('Área CNAEF:')
        if cnaef_start != -1:
            cnaef_end = text.find('Duração', cnaef_start)
            cnaef_code = text[cnaef_start:cnaef_end].strip()
            metadata[CONST.CNAEF_CODE] = cnaef_code

        # Extract the access exams section, which starts with "Provas de Ingresso"
        access_exams_start = text.find("Provas de Ingresso")
        access_exams_end = text.find("Classificações")
        if access_exams_start != -1:
            # Regex exams
            access_exams_text = text[access_exams_start:access_exams_end]
            access_exams_pattern = r"\d{2}\s+[A-Za-zÀ-ÿ e]+"
            exams = re.findall(access_exams_pattern, access_exams_text)

            # Process exams(extra string and duplicate exams)
            to_delete = list()
            for i in range(len(exams)):
                exams[i] = exams[i].replace("Candidatura de ", "")
                exams[i] = exams[i].replace("ou", "")
                if exams[i] == "24 e ":
                    to_delete.append(i)
            for delete_indexes in to_delete:
                del exams[delete_indexes]
            exams = set(exams)

            metadata[CONST.ACCESS_EXAMS] = list(exams)

    return metadata

def compute_uni_link(degree_code: int, uni_code: int) -> str:
    """Computes dges university link"""
    return f"https://www.dges.gov.pt/guias/detcursopi.asp?codc={degree_code}&code={uni_code}"

def apply_fitlers(degrees: list, access_exams: list|None, degree_name: list|None, cnaefs: list|None, uni_codes:list|None) -> list:
    """
    Applies filters on a given degrees dict
    This is such bad code... but don't spend time refactoring
    """
    filtered = list() 
    total = 0
    count_append = 0
    if degrees is None or len(degrees) == 0:
        raise ValueError(f"apply_filters: degree dict is invalid ({degrees})")

    # go through all degrees and apply filters
    for degree in degrees:
        universities_to_append = list()
        for university in degree[CONST.UNIVERSITIES]:
            total += 1
            # Access exam filter
            if access_exams is not None and len(access_exams) > 0:
                if HARD_ACCESS_EXAM_FILTER:
                    continue_flag = False
                    for exam in access_exams:
                        if exam not in university[CONST.UNI_METADATA][CONST.ACCESS_EXAMS]:
                            continue_flag = True
                            break
                    if continue_flag:
                        continue
                else:
                    continue_flag = True
                    for exam in access_exams:
                        if exam in university[CONST.UNI_METADATA][CONST.ACCESS_EXAMS]:
                            continue_flag = False 
                            break
                    if continue_flag:
                        continue

            # CNAEF filter
            if cnaefs is not None and len(cnaefs) > 0:
                if university[CONST.UNI_METADATA][CONST.CNAEF_CODE] not in cnaefs:
                    continue

            # Uni codes
            if uni_codes is not None and len(uni_codes) > 0:
                if university[CONST.UNI_CODE] not in uni_codes:
                    continue

            # If we havent continued by now it means its all good
            universities_to_append.append(university)

        if len(universities_to_append) > 0:
            degree[CONST.UNIVERSITIES] = universities_to_append

            # Name filter
            if degree_name is not None and len(degree_name) > 0:
                if HARD_NAME_FILTER:
                    continue_flag = False
                    for name in degree_name:
                        if name.upper() not in degree[CONST.DEGREE_NAME].upper():
                            continue_flag = True
                            break
                    if continue_flag:
                        continue
                else:
                    continue_flag = True 
                    for name in degree_name:
                        if name.upper() in degree[CONST.DEGREE_NAME].upper():
                            continue_flag = False 
                            break
                    if continue_flag:
                        continue

            count_append += len(degree[CONST.UNIVERSITIES])
            filtered.append(degree)

    print(f"[FILTER] Filtered universities... old={total}; new={count_append}")
    print(f"[FILTER] Filtered degrees... old={len(degrees)}; new={len(filtered)}")
    return filtered

if __name__ == "__main__":
    ret: int = main()
    assert isinstance(ret, int)
    sys.exit(ret)
