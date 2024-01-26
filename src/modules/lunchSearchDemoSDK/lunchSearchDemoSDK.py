import regex as re
import json
from .lunchSearchDemoSDKprompts import *
import unique_sdk
from pprint import pprint
from datetime import datetime
import tiktoken
import unique_sdk
from dotenv import load_dotenv
import os

load_dotenv()
unique_sdk.api_key = os.getenv("API_KEY")
unique_sdk.app_id = os.getenv("APP_ID")
unique_sdk.api_base = os.getenv("API_BASE")

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
maxToken = 3000


def lunchSearchDemoSDK(event):
    userId = event["userId"]
    companyId = event["companyId"]
    chatId = event["payload"]["chatId"]

    userMessage = event["payload"]["userMessage"]["text"]
    assistantMessageId = event["payload"]["assistantMessage"]["id"]

    unique_sdk.Message.modify(
        user_id=userId,
        company_id=companyId,
        id=assistantMessageId,
        chatId=chatId,
        text="Lunch Menu Search...",
    )

    try:
        languageModel = event["payload"]["configurations"]["languageModel"]
    except:
        languageModel = "AZURE_GPT_35_TURBO_0613"

    ######## step 1: extract location/restaurant names ########
    unique_sdk.Message.modify(
        user_id=userId,
        company_id=companyId,
        id=assistantMessageId,
        chatId=chatId,
        text="Location and restaurant name extraction...",
    )

    sys_prompt_location = LUNCH_SEARCH_LOCATION_SYSTEM_PROMT
    usr_prompt_location = LUNCH_SEARCH_LOCATION_TRIGGER_PROMT
    msg = [
        {"role": "system", "content": sys_prompt_location},
        {
            "role": "user",
            "content": usr_prompt_location.replace("USERMESSAGE", userMessage),
        },
    ]

    # openAI api call
    response = unique_sdk.ChatCompletion.create(
        company_id=companyId, model=languageModel, messages=msg
    )
    response = response["choices"][0]["message"]["content"]

    # Extract json from response
    name = []
    location = []
    pattern = re.compile(r"\{(?:[^{}]|(?R))*\}")
    response_json = pattern.findall(response)[0]
    response_json = json.loads(response_json)
    response_json = dict((k.lower(), v) for k, v in response_json.items())
    try:
        name = response_json["name"]
        location = response_json["location"]
    except:
        name = ["Atipic", "Cafe 1805", "Cafeteria BHK", "Cafeteria OBH"]
        location = ["Geneva", "Luxembourg"]

    # Replace BHK/OBH with 'Cafeteria BHK'/'Cafeteria OBH'
    if "BHK" in name:
        name.remove("BHK")
        name.append("Cafeteria BHK")
    if "OBH" in name:
        name.remove("OBH")
        name.append("Cafeteria OBH")

    ######## step 2: extract relevant names ########
    unique_sdk.Message.modify(
        user_id=userId,
        company_id=companyId,
        id=assistantMessageId,
        chatId=chatId,
        text="Source extraction...",
    )

    name_joined = ""
    if len(name) > 0:  # if user message containes one/several name(s), use these names
        name = name
    elif (
        len(location) > 0
    ):  # if user message does NOT contained a name but one/several location(s), use all names from this/these location
        if "Geneva" in location:
            name.append("Atipic")
            name.append("Cafe 1805")
        if "Luxembourg" in location:
            name.append("Cafeteria BHK")
            name.append("Cafeteria OBH")

    else:  # if user message does NOT contain a name nor a location, use all names
        name = ["Atipic", "Cafe 1805", "Cafeteria BHK", "Cafeteria OBH"]
    name_joined = ", ".join(name)

    ######## step 3: Vector DB search ########
    message_update = userMessage + " - " + name_joined  # add names to search query
    pprint(f"Updated search query: {message_update}")

    # todo: API call for hybrid search
    search_result = unique_sdk.Search.create(
        user_id=userId,
        company_id=companyId,
        chatId=chatId,
        searchString=message_update,
        searchType="VECTOR",
    )

    ######## step 4: Pick a subset of the search results as context for the new prompt ########
    searchContext = pickSearchResultsForTokenWindow(search_result, maxToken)

    ######## step 5: join sources them together ########
    searchContext = mergeSources(searchContext)
    assembledSearchContext = "\n".join(
        [
            f"<source{index}>{result['text']}</source{index}>"
            for index, result in enumerate(searchContext)
        ]
    )

    ######## step 6: get current day ########
    current_datetime = datetime.now()
    current_weekday = current_datetime.strftime("%A")

    ######## step 7: names to as formatted bullet list ########
    # e.g.:
    # - Atipic
    # - Cafe 1805
    names_formatted = "\n".join(["- " + item for item in name])

    ######## step 8: create main prompt to get menu ########
    sys_prompt_menu = LUNCH_SEARCH_ANSWER_SYSTEM_PROMT
    usr_prompt_menu = LUNCH_SEARCH_ANSWER_TRIGGER_PROMT

    msg = [
        {"role": "system", "content": sys_prompt_menu.replace("LANGUAGE", "English")},
        {
            "role": "user",
            "content": usr_prompt_menu.replace("SOURCES", assembledSearchContext)
            .replace("USERMESSAGE", userMessage)
            .replace("LANGUAGE", "English")
            .replace("RESTAURANTLIST", names_formatted)
            .replace("DAYQUERY", current_weekday),
        },
    ]

    # openAI api call
    result = unique_sdk.ChatCompletion.create(
        company_id=companyId, model=languageModel, messages=msg
    )
    result = result["choices"][0]["message"]["content"]

    # update sources
    result = postprocessSources(result)

    unique_sdk.Message.modify(
        user_id=userId,
        company_id=companyId,
        id=assistantMessageId,
        chatId=chatId,
        text=result,
    )


def pickSearchResultsForTokenWindow(searchResults, tokenLimit):
    pickedSearchResults = []
    tokenCount = 0

    for searchResult in searchResults:
        try:
            searchTokenCount = len(encoding.encode(searchResult["text"]))
        except:
            searchTokenCount = 0
        if tokenCount + searchTokenCount > tokenLimit:
            break

        pickedSearchResults.append(searchResult)
        tokenCount += searchTokenCount

    return pickedSearchResults


def mergeSources(searchContext):
    sourceMap = {}
    for result in searchContext:
        sourceChunks = sourceMap.get(result["id"])
        if not sourceChunks:
            sourceMap[result["id"]] = [result]
        else:
            sourceChunks.append(result)

    mergedSources = []
    for sources in sourceMap.values():
        # sources.sort(key=lambda x: x["order"])
        for i, s in enumerate(sources):
            if i > 0:
                s["text"] = re.sub(
                    r"<\|document\|>(.*?)<\|\/document\|>", "", s["text"]
                )
                s["text"] = re.sub(r"<\|info\|>(.*?)<\|\/info\|>", "", s["text"])
        sources[0]["text"] = "\n".join(str(s["text"]) for s in sources)
        mergedSources.append(sources[0])

    return mergedSources


def postprocessSources(text):
    pattern = r"\[source(\d+)\]"
    replacement = lambda match: "<sup>{}</sup>".format(int(match.group(1)) + 1)
    return re.sub(pattern, replacement, text)
