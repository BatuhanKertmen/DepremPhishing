import pathlib
import os


# DIRECTORIES

WORKING_DIR = pathlib.Path().resolve()
LOGS_DIR = os.path.join(WORKING_DIR, "Logs")

# FILES

COUNTRY_CODES_TXT = os.path.join(WORKING_DIR, "country_codes.txt")
LOG_TXT = os.path.join(LOGS_DIR, "logs.txt")
WARNING_TXT = os.path.join(LOGS_DIR, "warnings.txt")
ERROR_TXT = os.path.join(LOGS_DIR, "errors.txt")
KEYWORDS_TXT = os.path.join(WORKING_DIR, "keywords.json")
DOMAIN_NAME_TXT = os.path.join(WORKING_DIR, "domain-names.txt")
