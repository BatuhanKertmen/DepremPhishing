from datetime import date
import os


from bs4 import BeautifulSoup
from io import BytesIO
import requests
import zipfile


from log import message, Status


def _scrapeTodaysDomainsFileLink(check_date, verbose):
    WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"
    whois_page = requests.get(WHO_IS_URL)
    soup = BeautifulSoup(whois_page.content, features="html.parser")
    domains_table_rows = soup.findAll('tr')

    today = date.today().strftime("%Y-%m-%d")
    if check_date:
        if domains_table_rows[1].contents[5].text != today:
            raise Exception("No domain file with the current date!")
    if int(domains_table_rows[1].contents[3].text) <= 0:
        raise Exception("0 domains in the file with the current date")

    message("Successfully downloaded newly registered domain zip file.", verbose, Status.SUCCESS)

    return domains_table_rows[1].contents[7].a['href']


def _downloadDomainList(link, file_location, verbose):
    try:
        get_zip = requests.get(link)
        zip_file = zipfile.ZipFile(BytesIO(get_zip.content))
        zip_file.extractall(file_location)
        message("Downloading newly registered domains is successful.", verbose, Status.SUCCESS)
        return os.path.join(file_location, zip_file.namelist()[0])

    except zipfile.BadZipfile:
        message("Were not able to extract from zip file.", verbose, Status.ERROR)
        raise Exception("Could not extract from zip file")


def scrapeWhoIsDs(file_location, verbose, check_date=True):
    zip_link = _scrapeTodaysDomainsFileLink(check_date, verbose)
    file_path = _downloadDomainList(zip_link, file_location, verbose)
    return file_path
