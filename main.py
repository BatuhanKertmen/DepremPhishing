from dotenv
import argparse


from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver


from htmlParser import getHtmlWithSelenium, getHtmlWithRequests
from utilityFunctions import pipeline, linkify, filterDomains
from keywordFinder import calculateOccurrence
from download_domains import scrapeWhoIsDs
from news_keywords import news_keywords
from virusTotalApiKeys import apikeys
from virusTotal import virusTotal
from log import message, Status


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--scraper", help="Selenium or requests. Default selenium.")
parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity.")
parser.add_argument("-u", "--url", help="URL to check.")
parser.add_argument("-w", "--who-is", action="store_true", help="Check who is newly registered domains.")
parser.add_argument("-uL", "--url-list", help="File location that contains URLs to check.")

args = parser.parse_args()

if args.who_is and (args.url is not None or args.url_list is not None):
    parser.error("When checking who is database any other url can not be given")

if args.url_list is None and args.url is None and args.who_is is None:
    parser.error("Either --url (-u) or --url-list (-uL) or --who-is (-w) must be provided.")

if args.url_list is not None and args.url is not None:
    parser.error("Both --url (-u) and --url-list (-uL) can not be provided at the same time.")

if args.scraper is not None and (args.scraper.lower() != "selenium" and args.scraper.lower() != "requests"):
    parser.error("Specified scraper is unknown.")

isSelenium = False if args.scraper is not None and args.scraper.lower() == "requests" else True
verbose = args.verbose

message("Given arguments are correct. Starting.", verbose, Status.LOG)

results = list()
api_idx = 0
if isSelenium:
    message("Initializing selenium driver.", verbose, Status.LOG)

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), desired_capabilities=caps)
    driver.set_page_load_timeout(30)

    message("Selenium driver succesfully initialized.", verbose, Status.SUCCESS)

    if args.who_is:
        message("Filtering domains.", verbose, Status.LOG)
        domain_file_name = scrapeWhoIsDs("domain-names.txt", verbose)
        domains = filterDomains(domain_file_name, verbose)
        message("Domains Successfully filtered.", verbose, Status.SUCCESS)

        for domain in domains:
            url = linkify(domain)
            result = pipeline(url, getHtmlWithSelenium, verbose, driver=driver)
            results.append(result)
            api_idx = (api_idx + 1) % len(apikeys)

    elif (url := args.url) is not None:
        url = linkify(url)
        result = pipeline(url, getHtmlWithSelenium, verbose, driver=driver)
        results.append(result)

    elif (file_name := args.url_list) is not None:
        with open(file_name, encoding="utf-8") as file:
            url_list = file.read().split("\n")

        for url in url_list:
            url = linkify(url)
            result = pipeline(url, getHtmlWithSelenium, verbose, driver=driver)
            results.append(result)
            api_idx = (api_idx + 1) % len(apikeys)

    message("First analyze completed. Driver closing.", verbose, Status.SUCCESS)
    driver.quit()

else:
    if args.who_is:
        message("Filtering domains.", verbose, Status.LOG)
        domain_file_name = scrapeWhoIsDs("domain-names.txt", verbose)
        domains = filterDomains(domain_file_name, verbose)
        message("Domains Successfully filtered.", verbose, Status.SUCCESS)

        for domain in domains:
            url = linkify(domain)
            result = pipeline(url, getHtmlWithRequests, verbose)
            results.append(result)
            api_idx = (api_idx + 1) % len(apikeys)

    elif (url := args.url) is not None:
        url = linkify(url)
        result = pipeline(url, getHtmlWithRequests, verbose)
        results.append(result)

    elif (file_name := args.url_list) is not None:
        with open(file_name, encoding="utf-8") as file:
            url_list = file.read().split("\n")

        for url in url_list:
            url = linkify(url)
            result = pipeline(url, getHtmlWithRequests, verbose)
            results.append(result)
            api_idx = (api_idx + 1) % len(apikeys)

    message("First analyze completed.", verbose, Status.SUCCESS)


message("Filtering results according to the keywords.", verbose, Status.LOG)
filtered_results = [result for result in results
                    if (result["occurrence"]["level_3"] >= 5
                    and result["occurrence"]["level_2"] >= 1)
                    or
                    (result["occurrence"]["level_3"] >= 3
                    and result["occurrence"]["level_2"] >= 1
                    and result["occurrence"]["level_1"] >= 1
                    )]
message("Results sucessfully filtered.", verbose, Status.SUCCESS)


message("Removing news sites from results", verbose, Status.LOG)
filtered_results = [filtered_result for filtered_result in filtered_results
                    if calculateOccurrence(filtered_result["text"], news_keywords) < 7]
message("News sites removed.", verbose, Status.SUCCESS)

message("Getting VirusTotal answers.", verbose, Status.LOG)


counter = 0
for filtered_result in filtered_results:
    is_malicious = virusTotal(filtered_result["url"], apikeys[counter])
    filtered_result["virus_total"] = is_malicious

    counter = (counter + 1) % len(apikeys)

print([result["domain"] + " " + str(result["virus_total"]) for result in filtered_results])



