from gw2api import GuildWars2Client
import time
import json
import yaml
import pandas as pd
from pandas.core.common import flatten
import pandas.io.formats.style

html_location = "../material/overrides/"
search_term = "traits"
amount_per_chunk = 1000
time_between_chunks = 1
time_to_sleep = 60
gw2 = GuildWars2Client()
traits = []

print("Pulling data from the GW2 API...")
for i in gw2.traits.get():
    traits.append(i)

print("Calculating total data pieces...")
cntTraits = len(traits)


def get_chunks(size):
    chunked_list = [traits[i : i + size] for i in range(0, cntTraits, size)]
    return chunked_list


def get_json(lst):
    print("Writing JSON file...")
    with open("traits.json", "w") as outfile:
        for item in lst:
            print(json.dumps(item), file=outfile)


def get_yaml(lst):
    yamlString = yaml.dump(lst, indent=2, sort_keys=False)
    yamlFile = open(search_term + ".yaml", "w")
    yamlFile.write(yamlString)
    yamlFile.close()


def get_html(lst):
    html_name = html_location + search_term + ".html"
    df = pd.DataFrame(data=lst)
    df.drop(
        [
            "tier",
            "order",
            "description",
            "facts",
            "icon",
            "skills",
            "traited_facts",
        ],
        axis=1,
        inplace=True,
    )
    df.columns = [
        "API ID",
        "Trait",
        "Slot",
        "Specialization",
    ]
    df.set_index("API ID")
    result = """
        {% extends "overrides/main.html" %}
        {% block content %}
        <section>
        <div>
            <div>
                <div>
                    <h1>Traits</h1>
        """

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
    const table = new simpleDatatables.DataTable("#traits")
    </script>
    {% endblock %} 
    """
    with open(html_name, "w") as f:
        f.write(result)


# Get api search item in chunks to avoid throttling
objChunks = get_chunks(size=amount_per_chunk)
lstSearchItems = []
missedItems = []
for chunk in objChunks:
    i = 0
    # print(chunk) #debug
    for i in chunk:
        trait = gw2.traits.get(id=i)
        if trait == {"text": "too many requests"}:
            print("API rate limit hit - sleeping for 60s...")
            missedItems.append(i)
            time.sleep(time_to_sleep)
        else:
            lstSearchItems.append(trait)
        chunk_n = 0
    # print(missedItems) #debug
    for i in missedItems:
        trait = gw2.traits.get(id=i)
        lstSearchItems.append(trait)

# get_json(lstSearchItems)
# get_yaml(lstSearchItems)
get_html(lstSearchItems)
print("Process complete")
