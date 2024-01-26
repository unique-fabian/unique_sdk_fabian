LUNCH_SEARCH_LOCATION_SYSTEM_PROMT = """Your task is to check if the query includes names of restaurants and locations.

There are the following restaurants with the location in JSON format:

{{'name': 'food truck', 'location': 'Geneva'},
{'name': 'Cafe 1805', 'location': 'Geneva'},
{'name': 'Atipic', 'location': 'Geneva'},
{'name': 'Gabelle', 'location': 'Geneva'},
{'name': 'BHK', 'location': 'Luxembourg'},
{'name': 'OBH', 'location': 'Luxembourg'},
{'name': 'soup station', 'location': 'London'},
{'name': 'theatre', 'location': 'London'},
{'name': 'bistro', 'location': 'London'}}

Step 1: Extract all names of restaurants from the query that you can find also on the JSON.

Step 2: Extract all locations from the query. Add for each found name the location to the output.

Step 3: Extract the day from the query. If now day is mentioned, return "NONE".

Output a JSON object structured like:
{"name": list of restaurant names,
"location": list of locations must be in [Geneva, Luxembourg],
"day": list of weekdays must be in ["NONE",  "Monday",  "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}"""

LUNCH_SEARCH_LOCATION_TRIGGER_PROMT = """Today is TODAY.

Query:
\`\`\`
USERMESSAGE
\`\`\`

Output in JSON format:"""

LUNCH_SEARCH_ANSWER_SYSTEM_PROMT = """Your task is to return the menu options for the restaurants and location mentioned in the prompt.

Below are sources of the weekly menu for different cafeterias. Each source is delimited with XML tags. There are no additional sources outside of the ones provided.

There are some menu options available every day. These are available Monday to Friday.

Divide your answer between options available on the requested day and those available every day. Food trucks and restaurants in London to not have menu options available every day. Return the menu for all food trucks.

Divide your answer by cafeteria. Indicate the name of the cafeteria in bold.

Translate the menu options to LANGUAGE.

Include ALL available menu options per restaurants in your answer for the requested date, including the options available every day.

Example of answer with table format and source references (always at the end of your answer):
###
**Cafétéria BHK**

Menu - Monday:

| **Day** | **Menu of the day A** | **Menu of the day B** | **Animation**| **Dessert** |
| --- | --- | --- | --- | --- |
| **Monday** | Burger and fries | Spaghetti Napoli | Saltinboca | Chocolate cake |

Other options available every day:

- **Pasta of the week**: Bolognese sauce pasta
- **Salad**: Assortment of salad

Source:
- Cafétéria BHK: [sourceX]

--------------------

**Cafétéria OHB**

Menu - Monday:

| **Day** | **Menu of the day A** | **Pasta** | **Dessert** |
| --- | --- | --- | --- |
| **Monday** | Pizza |Ravioli | Chocolate creme |

Other options available every day:

- **Sandwich**: Sandwich, panini et croque-monsieur
- **Salad**: Assortment of salad

Source:
- Cafétéria OBH: [sourceY]

--------------------

**Food Trucks**
**Food-Truck 3 AC_50-52**:
- **Monday**: Truck name 1 - Menu 1
**Food-Truck 2 AC_48-50**:
- **Monday**: Truck name 2 - Menu 2
Source:
- Food trucks: [sourceZ]

--------------------

**Menu London**

Menu - Monday:

| **Day** | **The Soup Station** | **The Theatre** | **The Bistro** | **The Bistro - Vegetarian** |
| --- | --- | --- | --- | --- |
| **Monday** | Chicken Soup | Meatball Pasta | Lamb Moussaka | Vegeterian Moussaka |

Source:
- Menu London: [sourceA]
###"""

LUNCH_SEARCH_ANSWER_TRIGGER_PROMT = """Be aware that: Today is TODAY. Tomorrow is TOMORROW.

PROMPT:
\`\`\`
USERMESSAGE

- RESTAURANTLIST
DAYQUERY
\`\`\`

Sources:
\`\`\`
SOURCES
\`\`\`

If a day is mentioned in the PROMPT, return the menu only for that specific day (Today is TODAY). Otherwise include the menu for TODAY. There are no menu options for Saturday and Sunday.

PROMPT:
\`\`\`
USERMESSAGE

- RESTAURANTLIST
DAYQUERY
\`\`\`

Your answer must be in LANGUAGE (STRICTLY reference each used source number, e.g. [source0]).
Include in your answer EXCLUSIVELY one single restaurant, namely 'NAMES':"""
