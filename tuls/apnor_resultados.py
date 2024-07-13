"""
  APNOR webcrawler
"""
from apnor_cosntants import *

import sys
import json
import requests
from datetime import datetime
from PyPDF2 import PdfReader
from io import BytesIO

# Valid api headers
headers = {
    'Cookie': 'JSESSIONID=0BBABC5E5707D8DFBC92BCCEB2BADD3E',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def extract_pdf_info(response: requests.Response):
    """Extracts pdf info from a valid Response from an url"""
    assert response.status_code != 401
    
    # Read content
    pdf_file = BytesIO(response.content)
    pdf_reader = PdfReader(pdf_file)
    info = pdf_reader.metadata
    if info is None:
        return None

    # Extract content
    found_school = None
    found_exam = None
    first_page = None
    for page in pdf_reader.pages:
        text = page.extract_text()
        if not first_page:
            first_page = text 

        # School search
        for school in SCHOOL_MAPPING:
            if school in text:
                found_school = SCHOOL_MAPPING[school]
                break

        # Exam search
        for exam in EXAM_MAPPING:
            if exam in text:
                found_exam = EXAM_MAPPING[exam]
                break

    if not found_exam or not found_school:
        if first_page == "" or first_page == " ":
            print("Page seems to be an image")
        else:
            print(first_page)

    # Send results
    return {
        DETECTED_SCHOOL: found_school,
        DETECTED_EXAM: found_exam,
        CREATION_DATE: parse_pdf_date(info.get('/CreationDate')),
        MODIFICATION_DATE: parse_pdf_date(info.get('/ModDate')),
        METADATA: info
    }

def parse_pdf_date(pdf_date):
    if pdf_date is None:
        return None

    if pdf_date.startswith('D:'):
        pdf_date = pdf_date[2:]
    
    # Extract date components
    year = int(pdf_date[0:4])
    month = int(pdf_date[4:6])
    day = int(pdf_date[6:8])
    hour = int(pdf_date[8:10])
    minute = int(pdf_date[10:12])
    second = int(pdf_date[12:14])

    # Create datetime object
    creation_datetime = datetime(year, month, day, hour, minute, second)
    return creation_datetime.strftime("%Y-%m-%d")

def check_valid_numbers(start: int, end: int, year_filter=None, exam_filter=None) -> dict:
    """Checks for valid numbers in apnor API"""
    valid_numbers = dict()
    for number in range(start, end):
        url = f"https://www.apnor.pt/api/resultado/candidato/pauta/{number}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pdf_info = extract_pdf_info(response)
            if pdf_info is not None:
                # Process pdf info
                doc_age = pdf_info[CREATION_DATE] if pdf_info[CREATION_DATE] is not None else pdf_info[MODIFICATION_DATE]
                doc_year = doc_age[:4]
                print(f"[{number}] {pdf_info[DETECTED_SCHOOL]} - {pdf_info[DETECTED_EXAM]} in {doc_year}")

                # Check for year filter
                if (year_filter is None or int(doc_year) == year_filter) and (exam_filter is None or pdf_info[DETECTED_EXAM] == exam_filter):
                    valid_numbers[number] = pdf_info
            else:
                print(f"[{number}] Is valid with no availabe pdf info")

        if number % 500 == 0:
            print(f"[{number}] Printing current state")
    return valid_numbers

if __name__ == "__main__":
    valid_numbers = check_valid_numbers(start=9000, end=11000, year_filter=2024, exam_filter=MAT_PT_EXAM)

    # Show/Export info
    if len(sys.argv) > 1:
        out_file = open(sys.argv[1], "w")
        json.dump(valid_numbers, out_file, indent=4)
        out_file.close()
        print(f"[RESULT] Dumped into {sys.argv[1]}")
    else:
        print(valid_numbers)
