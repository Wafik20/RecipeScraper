from dotenv import load_dotenv
import os
from openai import OpenAI

# Load the .env file
load_dotenv()

# Get the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY is not set. Please check your .env file.")
    exit()

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are a recipe assistant here to help you parse recipes.",
            },
            {"role": "user", "content": "this is a recipe for a cake"},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "recipe",
                "strict": False,
                "schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "photo": {"type": "string", "format": "uri"},
                        "category": {
                            "type": "string",
                            "enum": [
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
                                "Salads",
                                "Sauces & Dressings",
                                "Snacks",
                                "Soups",
                            ],
                        },
                        "ingredients": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ingredient_name": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "measurement_unit": {
                                        "type": "string",
                                        "enum": [
                                            "clove",
                                            "cloves",
                                            "cup",
                                            "fl oz",
                                            "gallon",
                                            "grams",
                                            "head",
                                            "lb",
                                            "ml",
                                            "oz",
                                            "pieces",
                                            "pinch",
                                            "pint",
                                            "quart",
                                            "sprig",
                                            "sprigs",
                                            "Tbsp",
                                            "tsp",
                                            "whole",
                                        ],
                                    },
                                    "notes": {"type": "string"},
                                },
                                "required": [
                                    "ingredient_name",
                                    "quantity",
                                    "measurement_unit",
                                ],
                            },
                        },
                        "instructions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_number": {"type": "integer"},
                                    "description": {"type": "string"},
                                },
                                "required": ["step_number", "description"],
                            },
                        },
                        "prep_time": {"type": "string"},
                        "cook_time": {"type": "string"},
                        "difficulty": {"type": "integer", "minimum": 1, "maximum": 5},
                        "servings": {"type": "integer"},
                        "yield": {"type": "string"},
                        "original_link": {"type": "string", "format": "uri"},
                        "video_link": {"type": "string", "format": "uri"},
                    },
                    "required": ["title", "ingredients", "instructions"],
                },
            },
        },
        strict=True,
    )

    
    recipe = response.choices[0].message['content']
    if (recipe.refusal):
        print(recipe.refusal)
    else:
        print(recipe.parsed)
except Exception as e:
    # handle errors like finish_reason, refusal, content_filter, etc.
    pass
