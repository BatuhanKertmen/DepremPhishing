import json


def calculateOccurrence(text, keywords):
    total = 0

    for keyword in keywords:
        if keyword in text:
            print(keyword)
            total += 1

    return total


def calculateTotalOccurrences(text, keywords_file_name):
    with open(keywords_file_name, "r", encoding="utf-8") as file:
        keywords = json.load(file)

    return {
        "level_1": calculateOccurrence(text, set(keywords["level_1"])),
        "level_2": calculateOccurrence(text, set(keywords["level_2"])),
        "level_3": calculateOccurrence(text, set(keywords["level_3"])),
    }



