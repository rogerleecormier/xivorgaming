from gw2api import GuildWars2Client
import time
import json
import yaml
import pandas as pd
from pandas.core.common import flatten
import pandas.io.formats.style
import os
import re

search_term = "specializations"
amount_per_chunk = 100
time_to_sleep = 0.5
gw2 = GuildWars2Client()
specializations = []

for i in gw2.specializations.get():
    specializations.append(i)


def get_chunks(size):
    chunked_list = [
        specializations[i : i + size]
        for i in range(0, len(specializations), size)
    ]
    return chunked_list


def get_json(lst):

    jsonString = json.dumps(lst, indent=2)

    for i in jsonString:
        data = json.loads(jsonString)
        for element in data:
            if element.get("icon") is not None:
                del element["icon"]
            if element.get("background") is not None:
                del element["background"]
            if element.get("profession_icon_big") is not None:
                del element["profession_icon_big"]
            if element.get("profession_icon") is not None:
                del element["profession_icon"]
    jsonProcessed = json.dumps(data, indent=2)
    jsonFile = open(search_term + ".json", "w")
    jsonFile.write(jsonProcessed)
    jsonFile.close()


def parse_json():
    with open(search_term + ".json") as output:
        data = json.load(output)
        for key in data:
            del key["icon"]
    return


def get_yaml(lst):
    yamlString = yaml.dump(lst, indent=2, sort_keys=False)
    yamlFile = open(search_term + ".yaml", "w")
    yamlFile.write(yamlString)
    yamlFile.close()


def get_df(lst):
    df = pd.DataFrame(data=lst)
    df.pop("icon")
    df.pop("background")
    df.pop("weapon_trait")
    df.pop("profession_icon_big")
    df.pop("profession_icon")
    df.columns = [
        "API ID",
        "Specialization",
        "Profession",
        "Elite?",
        "Minor Trait IDs",
        "Major Trait IDs",
    ]
    df.set_index("API ID")
    df["Trait IDs"] = df["Major Trait IDs"] + df["Minor Trait IDs"]
    flattened_col = pd.DataFrame(
        [
            (index, value)
            for (index, values) in df["Trait IDs"].iteritems()
            for value in values
        ],
        columns=["index", "Trait IDs"],
    ).set_index("index")
    df = df.drop("Trait IDs", axis=1).join(flattened_col)
    df = df.drop("Minor Trait IDs", axis=1)
    df = df.drop("Major Trait IDs", axis=1)
    return df


def get_html(lst):
    df = get_df(lst)
    htmlFile = df.to_html(
        search_term + ".html", table_id=search_term, index=False
    )


def get_df(lst):
    df = pd.DataFrame(data=lst)
    df.pop("icon")
    df.pop("background")
    df.pop("weapon_trait")
    df.pop("profession_icon_big")
    df.pop("profession_icon")
    df.columns = [
        "API ID",
        "Specialization",
        "Profession",
        "Elite?",
        "Minor Trait IDs",
        "Major Trait IDs",
    ]


def writeHTML(lst):
    PATH = "../material/overrides/"
    HNAME = PATH + search_term + ".html"
    df = pd.DataFrame(data=lst)
    df.pop("icon")
    df.pop("background")
    df.pop("weapon_trait")
    df.pop("profession_icon_big")
    df.pop("profession_icon")
    df.columns = [
        "API ID",
        "Specialization",
        "Profession",
        "Elite?",
        "Minor Trait IDs",
        "Major Trait IDs",
    ]
    df.set_index("API ID")
    df["Trait IDs"] = df["Major Trait IDs"] + df["Minor Trait IDs"]
    flattened_col = pd.DataFrame(
        [
            (index, value)
            for (index, values) in df["Trait IDs"].iteritems()
            for value in values
        ],
        columns=["index", "Trait IDs"],
    ).set_index("index")
    df = df.drop("Trait IDs", axis=1).join(flattened_col)
    df = df.drop("Minor Trait IDs", axis=1)
    df = df.drop("Major Trait IDs", axis=1)
    
    result = """
        {% extends "overrides/main.html" %}
        {% block content %}
        <section>
        <div>
            <div>
                <div>
                    <h1>Specializations</h1>
        """
    if type(df) == pd.io.formats.style.Styler:
        result += df.render()
    else:
        result += df.to_html(
            table_id=search_term, escape=False, border=0, index=False
        )
        result += """
                </div>
            </div>
        </div>
        </section>
        <script src="https://cdn.jsdelivr.net/npm/simple-datatables@latest"></script>
        <script>
        const table = new simpleDatatables.DataTable("#specializations")
        </script>
        {% endblock %}
        """
    with open(HNAME, "w") as f:
        f.write(result)


# Get api search item in chunks to avoid throttling
objChunks = get_chunks(size=amount_per_chunk)
lstSearchItems = []
for chunk in objChunks:
    i = 0
    # print(chunk) #debug
    for i in chunk:
        trait = gw2.specializations.get(id=i)
        lstSearchItems.append(trait)
        chunk_n = 0
    chkTotal = len(objChunks)
for chkRem in range(len(objChunks), -1, -1):
    print(
        str(i)
        + " items processed in "
        + str(chkTotal)
        + " total chunks with "
        + str(chkRem)
        + " remaining to process."
    )
    time.sleep(time_to_sleep)

# get_json(lstSearchItems)
# get_yaml(lstSearchItems)
# get_html(lstSearchItems)
writeHTML(lstSearchItems)
