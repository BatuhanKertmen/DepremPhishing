from bs4 import BeautifulSoup
import requests


from log import message, Status


def getHtmlWithRequests(url, verbose=False):
    try:
        request = requests.get(url)

        if request.status_code > 399 and verbose:
            message(str(url) + " could not be reached.", verbose, Status.ERROR)
        elif request.status_code < 300 and verbose:
            message(str(url) + " html successfully downloaded.", verbose, Status.ERROR)

        return request.content

    except Exception:
        message(str(url) + " could not be reached.", verbose, Status.ERROR)
        return ""


def getHtmlWithSelenium(url, driver, verbose=False):
    try:
        driver.get(url)
        driver.implicitly_wait(10)

        message(str(url) + " html successfully downloaded.", verbose, Status.SUCCESS)

        return driver.page_source
    except Exception:
        message(str(url) + " could not be reached.", verbose, Status.ERROR)
        return ""


def extractText(html):
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text.lower()
