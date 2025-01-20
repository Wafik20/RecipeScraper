from urllib.parse import urlparse
import json
from dotenv import load_dotenv
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

def build_extraction_prompt(fields=RECIPE_FIELDS):
    def format_field(key, value):
        # Handle nested dictionary fields
        if isinstance(value, dict):
            # Category field with options
            if "options" in value:
                return f"{value['field']} (select one: {', '.join(value['options'])})"
            
            # Ingredients or Instructions with subfields
            elif "fields" in value:
                if key == "ingredients":
                    return '''ingredients (list each with:
- Name
- Quantity (numbers only)
- Unit (must be one from: {measurement_units})
  Rules for units:
  - Use 'whole' for countable items (e.g., '2 eggs' → quantity: 2, unit: whole)
  - Use 'Tbsp' for tablespoon(s)
  - Use 'tsp' for teaspoon(s)
  - Split combined values (e.g., '2 tablespoons' → quantity: 2, unit: Tbsp)
- Additional notes'''.format(measurement_units=', '.join(MEASUREMENT_UNITS))
                elif key == "instructions":
                    return "instructions (list each with step number and description)"
            
            # Difficulty with scale
            elif "scale" in value:
                return f"{value['field']} (scale {value['scale']}, estimate if not provided)"
        
        # Photo field with special instructions
        elif key == "photo":
            return ("photo (main recipe image URL, preferably from meta tags "
                   "'og:image'/'twitter:image' or largest image near title)")
        
        # Simple fields
        else:
            return value

    # Build sections of the prompt
    sections = [
        "Extract the following recipe information. Return in JSON format:",
        "Basic Information:",
    ]
    
    # Add fields in a structured way
    for key, value in fields.items():
        formatted = format_field(key, value)
        if formatted:
            sections.append(f"• {formatted}")
    
    # Add final instructions
    sections.append("\nUse 'Not specified' for any missing information.")
    
    return "\n".join(sections)

def scrape_recipe(url):
    # Create the SmartScraperGraph instance and run it
    smart_scraper_graph = SmartScraperGraph(
        prompt=build_extraction_prompt(),
        source=url,
        config=graph_config
    )
    result = smart_scraper_graph.run()
    return result

# Print a pretty JSON response
def print_json(json_data):
    print(json.dumps(json_data, indent=4))

print_json(scrape_recipe("https://www.foodnetwork.com/recipes/giada-de-laurentiis/chicken-florentine-style-recipe-1942850"))