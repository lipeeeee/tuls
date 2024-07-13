"""
  APNOR webcrawler constants
  Written by lipeeeee
"""

"""Schools"""
IPVC = "ipvc"
IPCA = "ipca"
UTAD = "utad"
IPP  = "ipp"
IPB  = "ipb"

"""String to School mappings"""
SCHOOL_MAPPING = {
    "Instituto Politécnico de Viana do Castelo": IPVC,
    "Instituto Politécnico d e Viana do Castelo": IPVC,
    "Instituto Politécnico de Viana  do C astelo": IPVC,
    "Universidade de Trás os Montes e Alto Douro": UTAD,
    "Universidade de Trás": UTAD,
    "UTAD": UTAD,
    "Instituto Politécnico do Cávado e do Ave": IPCA,
    "IPCA": IPCA,
    "Instituto Politécnico de Bragança": IPB,
    "Instituto Politécnico d e Bragança": IPB,
    "Instituto Politécnico do Porto": IPP,
    "Instituto Politécnico do Port o": IPP
}

"""Exams"""
MAT_PT_EXAM = "matpt"
BIO_PT_EXAM = "biopt"
ECO_PT_EXAM = "ecopt"
PSI_PT_EXAM = "psipt"
HST_PT_EXAM = "hstpt"
CERTIFICATE = "certificate"

"""String to Exam mapping"""
EXAM_MAPPING = {
    "PORTUGUÊS e MATEMÁTICA": MAT_PT_EXAM,
    "PORTUGUÊS  e MATEMÁTICA": MAT_PT_EXAM,
    "PORTUGUÊS e  MATEMÁTICA": MAT_PT_EXAM,
    "MATEMÁTICA e PORTUGUÊS": MAT_PT_EXAM,
    "MATEMÁTICS e PORTUGUÊS": MAT_PT_EXAM,
    "MATEMÁTICA  e PORTUGUÊS": MAT_PT_EXAM,
    "MATEMÁTICS  e PORTUGUÊS": MAT_PT_EXAM,
    "PORTUGUÊS e BIOLOGIA": BIO_PT_EXAM,
    "PORTUGUÊS  e BIOLOGIA": BIO_PT_EXAM,
    "BIOLOGIA e PORTUGUÊS": BIO_PT_EXAM,
    "BIOLOGIA  e PORTUGUÉS": BIO_PT_EXAM,
    "BIOLOGIA  e PORTUGUÊS": BIO_PT_EXAM,
    "ECONOMIA e PORTUGUÊS": ECO_PT_EXAM,
    "PORTUGUÊS e ECONOMIA": ECO_PT_EXAM,
    "ECONOMIA  e PORTUGUÊS": ECO_PT_EXAM,
    "PSICOLOGIA e PORTUGUÊS": PSI_PT_EXAM,
    "PORTUGUÊS e PSICOLOGIA": PSI_PT_EXAM,
    "PSICOLOGIA  e PORTUGUÊS": PSI_PT_EXAM,
    "HISTÓRIA DA CULTURA E": HST_PT_EXAM,
    "HISTÓRIA E CULTURA D": HST_PT_EXAM,
    "HISTÓRIA  DA CULTURA  E DAS": HST_PT_EXAM,
    "HCA  e PORTUGUÊS": HST_PT_EXAM,
    "HCA e PORTUGUÊS": HST_PT_EXAM,
    "HCA e  PORTUGUÊS": HST_PT_EXAM,
    "CERTIFICADO": CERTIFICATE
}

"""Metadata dict keys"""
DETECTED_SCHOOL = "DetectedSchool"
DETECTED_EXAM = "DetectedExam"
CREATION_DATE = "CreationDate"
MODIFICATION_DATE = "ModDate"
METADATA = "Metadata"
