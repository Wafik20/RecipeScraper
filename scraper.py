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

prompt = '''Extract the following structured information from the recipe webpage. Format your response using clear headings and maintain consistent data structures.

1. Basic Information
- Recipe Title
- Descriptive Text/Introduction
- Category (select ONE only):
  Appetizers, Baked Goods, Beverages, Breakfast, Cakes, Candies, Cookies, Cupcakes & Muffins, Frostings & Toppings, Ice Cream, Pies, Meat, Poultry, Seafood, Salads, Sauces & Dressings, Snacks, Soups, Other

2. Media Content
- Recipe Photo URL (in priority order):
  - Meta tags (og:image, twitter:image)
  - Largest image near title
  (ensure URL is properly formatted)
- Video Link (if available)
- Original Recipe URL

3. Recipe Details
- Prep Time
- Cook Time
- Number of Servings/Yield
- Difficulty (1-5 scale, estimate if not provided)

4. Ingredients
List each ingredient with:
- Name
- Quantity (NUMBERS ONLY - if "2 tablespoons" appears, put "2" here)
- Unit (MUST be one of these - intelligently infer based on context):
  - Volume: cup(s), fl oz, gallon, ml, pint, quart, Tbsp [use for "tablespoon(s)"], tsp [use for "teaspoon(s)"]
  - Weight: grams, lb, oz
  - Count: clove(s), head, piece(s), pinch, sprig(s), whole
- Additional notes

IMPORTANT RULES FOR UNITS:
1. When quantity and unit appear together, separate them:
   - CORRECT:   "Quantity": "2", "Unit": "Tbsp"
   - INCORRECT: "Quantity": "2 tablespoons", "Unit": "Not specified"

2. Use "whole" as the unit when:
   - The ingredient is a discrete item without a specified unit (e.g., "2 eggs" → Quantity: "2", Unit: "whole")
   - The recipe lists countable items (e.g., "3 bell peppers" → Quantity: "3", Unit: "whole")
   - Single items are referenced (e.g., "1 onion" → Quantity: "1", Unit: "whole")

Examples of correct parsing:
"2 tablespoons shallots" → Quantity: "2", Unit: "Tbsp"
"3 cups flour" → Quantity: "3", Unit: "cups"
"1/2 teaspoon salt" → Quantity: "1/2", Unit: "tsp"
"2 eggs" → Quantity: "2", Unit: "whole"
"1 large onion" → Quantity: "1", Unit: "whole"
"3 bell peppers, diced" → Quantity: "3", Unit: "whole"

Note: Size descriptions (large, medium, small) and preparation instructions (diced, chopped, sliced) should go in Additional notes.

5. Instructions
List each step with:
- Step number
- Detailed description

Mark any missing information as "Not specified". Return the data in a clear, structured format suitable for parsing.'''

def scrape_recipe(url):
    # Create the SmartScraperGraph instance and run it
    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config
    )
    result = smart_scraper_graph.run()
    return result

# Print a pretty JSON response
def print_json(json_data):
    print(json.dumps(json_data, indent=4))

print_json(scrape_recipe("https://www.foodnetwork.com/recipes/food-network-kitchen/slow-cooker-pinto-beans-10076200"))