from itertools import islice
import re

from paths import KEYWORDS_TXT, COUNTRY_CODES_TXT
from domain_name_similarity_list import domain_name_similarity_list
from keywordFinder import calculateTotalOccurrences
from stringComparison import jaro_distance
from htmlParser import extractText
from log import message, Status


def linkify(string):
    if not string.startswith("http"):
        string = "http://" + string

    if string.count("/") < 3:
        string = string + "/"

    return string


def getFullDomains(url):
    url_split = url.split("/")[2:-1]
    domain = url_split[0]
    domains_list = domain.split(".")

    last = domains_list[-1]

    with open(COUNTRY_CODES_TXT, "r")as file:
        country_codes = file.read().split("\n")
    tld_idx = -1 if last not in country_codes else -2

    tld = domains_list[tld_idx]
    sub_domains = domains_list[:tld_idx]
    country_code = None if tld_idx == -1 else domains_list[-1]

    return tld, sub_domains, country_code


def getDomainName(url):
    tld, subdomains, country_code = getFullDomains(url)

    if len(subdomains) >= 1 and subdomains[0] == "www":
        subdomains = subdomains[1:]

    if country_code:
        raw_domain_name = ".".join(subdomains) + "." + tld + "." + country_code
    else:
        raw_domain_name = ".".join(subdomains) + "." + tld
    return raw_domain_name


def findDomainNameSimilarity(domains):
    results = set()

    for domain in domains:
        max_similarity = 0

        domain_without_tld = "".join(domain.split(".")[0:-1])
        for similar_domain in domain_name_similarity_list:
            similarity = jaro_distance(similar_domain, domain_without_tld)
            if similarity > max_similarity:
                max_similarity = similarity

        if max_similarity > 0.85:
            results.add(domain)

    return results


def filterDomains(domain_file_name, verbose):
    results = set()

    counter = 0
    batch = 1000
    with open(domain_file_name, encoding="utf-8") as file:
        while lines := list(islice(file, batch)):
            temp = findDomainNameSimilarity(lines)
            temp = {domain.strip() for domain in temp}
            results |= temp

            counter += 1
            message(str(batch * counter) + " many domains filtered", verbose, Status.LOG)

    with open("res.txt", "w", encoding="utf-8") as file:
        file.writelines("\n".join(results))

    return results


def pipeline(url, download_func, verbose, driver=None):
    if driver is None:
        html = download_func(url, verbose)
    else:
        html = download_func(url, driver, verbose)
    text = extractText(html)
    occurrence = calculateTotalOccurrences(text, KEYWORDS_TXT)
    domain_address = getDomainName(url)

    return {
        "url": url,
        "text": text,
        "domain": domain_address,
        "total_word_count": len(re.split("[ \n\t]", text)),
        "occurrence": occurrence,
    }