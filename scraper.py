from dotenv import load_dotenv
import json
import os
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

# Load the .env file
load_dotenv()

# Get the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY is not set. Please check your .env file.")
    exit()
else:
    print("OPENAI_API_KEY:", OPENAI_API_KEY)

graph_config = {
   "llm": {
        "api_key": OPENAI_API_KEY,
        "model": "gpt-3.5-turbo",
   },
}

# Define available categories
RECIPE_CATEGORIES = [
    "Appetizers",
    "Baked Goods",
    "Beverages",
    "Breakfast",
    "Cakes",
    "Candies",
    "Cookies",
    "Cupcakes & Muffins",
    "Frostings & Toppings",
    "Ice Cream",
    "Other",
    "Pies",
    "meat",
    "poultry", 
    "seafood", 
    "other",
    "Salads",
    "Sauces & Dressings",
    "Snacks",
    "Soups"
]

# Define measurement units
MEASUREMENT_UNITS = [
    "clove", "cloves", "cup", "cups", "fl oz", "gallon", "grams", 
    "head", "lb", "ml", "oz", "pieces", "pinch", "pint", "quart", 
    "sprig", "sprigs", "Tbsp", "tsp", "whole"
]

# Define fields to extract
RECIPE_FIELDS = {
    "title": "Recipe Title",
    "description": "Descriptive Text",
    "photo": "Recipe Photo",
    "category": {
        "field": "Category",
        "options": RECIPE_CATEGORIES
    },
    "ingredients": {
        "fields": [
            "ingredient name",
            "quantity",
            {"measurement_unit": MEASUREMENT_UNITS},
            "notes"
        ]
    },
    "instructions": {
        "fields": [
            "step number",
            "description"
        ]
    },
    "prep_time": "Prep Time",
    "cook_time": "Cook Time",
    "difficulty": {
        "field": "Difficulty",
        "scale": "1-5"
    },
    "servings": "Number of servings",
    "yeild": "Yield",
    "original_link": "Link to original recipe",
    "video_link": "Link to video"
}

# Build the prompt dynamically
def build_extraction_prompt(fields=RECIPE_FIELDS):
    prompt = "Extract the following information from the recipe:\n"
    for key, value in fields.items():
        if isinstance(value, dict):
            if "options" in value:
                prompt += f"{value['field']} (one from the following: {', '.join(value['options'])}), "
            elif "fields" in value:
                subfields = [
                    f"{field['measurement_unit']} (one of the following: {MEASUREMENT_UNITS})" 
                    if isinstance(field, dict) and 'measurement_unit' in field
                    else field
                    for field in value['fields']
                ]
                prompt += f"{key.title()} ({', '.join(subfields)}), "
            elif "scale" in value:
                prompt += f"{value['field']} (scale from {value['scale']} Predict Difficulty if not presented with one), "
        else:
            prompt += f"{value}, "
    print(prompt)
    return prompt.rstrip(", ")

def scrape_recipe(url):
    # Create the SmartScraperGraph instance and run it
    smart_scraper_graph = SmartScraperGraph(
        prompt=build_extraction_prompt(),
        source=url,
        config=graph_config
    )

    result = smart_scraper_graph.run()
    return result

import json

# print a pretty json response
def print_json(json_data):
    print(json.dumps(json_data, indent=4))

print_json(scrape_recipe("https://www.simplyrecipes.com/easy-brooklyn-blackout-cake-recipe-8745470"))