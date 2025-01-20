from urllib.parse import urlparse
import json
from dotenv import load_dotenv
import os
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info
from validators import url as is_valid_url

# Load the .env file
load_dotenv()

# Get the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY is not set. Please check your .env file.")
    exit()

graph_config = {
   "llm": {
        "api_key": OPENAI_API_KEY,
        "model": "gpt-3.5-turbo",
   },
    "verbose": True,
    "headless": True,
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
    "Meat",
    "Poultry", 
    "Seafood", 
    "Other",
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
    prompt = "Extract the following information from the recipe webpage:\n"
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
        elif key == "photo":
            # Add specific instructions for fetching the photo
            prompt += (
                "Recipe Photo (retrieve the main image associated with the recipe, "
                "preferably from meta tags like 'og:image', 'twitter:image', or the "
                "largest image prominently displayed near the title), "
            )
        else:
            prompt += f"{value}, "
    return prompt.rstrip(", ")

def scrape_recipe(url):
    # Create the SmartScraperGraph instance and run it
    smart_scraper_graph = SmartScraperGraph(
        prompt=build_extraction_prompt(),
        source=url,
        config=graph_config
    )

    result = smart_scraper_graph.run()

    def clean_url(url):
        """
        Clean a URL string by:
        1. Replacing double backslashes with forward slashes
        2. Replacing single backslashes with forward slashes
        3. Converting multiple consecutive slashes to single slashes
        
        Args:
            url (str): The URL string to clean
            
        Returns:
            str: The cleaned URL string
        """
        # Replace double backslashes with forward slashes
        cleaned = url.replace('\\\\', '/')
        
        # Replace any remaining single backslashes with forward slashes
        cleaned = cleaned.replace('\\', '/')
        
        # Replace multiple consecutive slashes with a single slash
        # (except for http:// or https://)
        import re
        cleaned = re.sub(r'(?<!:)/{2,}', '/', cleaned)
    
        return cleaned

    # Sanitize the photo URL if present
    if "Recipe Photo" in result and result["Recipe Photo"]:
        result["Recipe Photo"] = clean_url(result["Recipe Photo"])

    return result

# Print a pretty JSON response
def print_json(json_data):
    print(json.dumps(json_data, indent=4))

print_json(scrape_recipe("https://www.simplyrecipes.com/easy-brooklyn-blackout-cake-recipe-8745470"))