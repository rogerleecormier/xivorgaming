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
time_between_chunks = 1
time_to_sleep = 60
gw2 = GuildWars2Client()
specializations = []

print("Pulling data from the GW2 API...")
for i in gw2.specializations.get():
    specializations.append(i)

print("Calculating total data pieces...")
cntSpecs = len(specializations)


def get_chunks(size):
    chunked_list = [
        specializations[i : i + size] for i in range(0, cntSpecs, size)
    ]
    return chunked_list


def get_json(lst):
    print("Writing JSON file...")
    with open("specializations.json", "w") as outfile:
        for item in lst:
            print(json.dumps(item), file=outfile)


def get_yaml(lst):
    yamlString = yaml.dump(lst, indent=2, sort_keys=False)
    yamlFile = open(search_term + ".yaml", "w")
    yamlFile.write(yamlString)
    yamlFile.close()


def get_html(lst):
    PATH = "../material/overrides/"
    HTML_NAME = PATH + search_term + ".html"
    df = pd.DataFrame(data=lst)
    df.drop(
        [
            "icon",
            "background",
            "weapon_trait",
            "profession_icon_big",
            "profession_icon",
        ],
        axis=1,
        inplace=True,
    )
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
    df.drop(["Minor Trait IDs", "Major Trait IDs"], axis=1, inplace=True)

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
    with open(HTML_NAME, "w") as f:
        f.write(result)


# Get api search item in chunks to avoid throttling
objChunks = get_chunks(size=amount_per_chunk)
lstSearchItems = []
missedItems = []
for chunk in objChunks:
    i = 0
    # print(chunk) #debug
    for i in chunk:
        spec = gw2.specializations.get(id=i)
        if spec == {"text": "too many requests"}:
            print("API rate limit hit - sleeping for 60s...")
            missedItems.append(i)
            time.sleep(time_to_sleep)
        else:
            lstSearchItems.append(spec)
        chunk_n = 0
        # print(missedItems) #debug
    for i in missedItems:
        spec = gw2.specializations.get(id=i)
        lstSearchItems.append(spec)
    chkTotal = len(objChunks)
for chkRem in range(len(objChunks), -1, -1):
    print(
        str(cntSpecs)
        + " items processed in "
        + str(chkTotal)
        + " total chunks with "
        + str(chkRem)
        + " remaining to process."
    )
    # time.sleep(time_to_sleep)

# get_json(lstSearchItems)
# get_yaml(lstSearchItems)
get_html(lstSearchItems)
print("Process complete")
