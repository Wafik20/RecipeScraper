from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from enum import Enum

# Load the .env file
load_dotenv()

# Get the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Error: OPENAI_API_KEY is not set. Please check your .env file.")

client = OpenAI()

class MeasurementUnit(str, Enum):
    CLOVE = "clove"
    CLOVES = "cloves"
    CUP = "cup"
    FL_OZ = "fl oz"
    GALLON = "gallon"
    GRAMS = "grams"
    HEAD = "head"
    LB = "lb"
    ML = "ml"
    OZ = "oz"
    PIECES = "pieces"
    PINCH = "pinch"
    PINT = "pint"
    QUART = "quart"
    SPRIG = "sprig"
    SPRIGS = "sprigs"
    TBSP = "Tbsp"
    TSP = "tsp"
    WHOLE = "whole"

class Category(str, Enum):
    APPETIZERS = "Appetizers"
    BAKED_GOODS = "Baked Goods"
    BEVERAGES = "Beverages"
    BREAKFAST = "Breakfast"
    CAKES = "Cakes"
    CANDIES = "Candies"
    COOKIES = "Cookies"
    CUPCAKES_MUFFINS = "Cupcakes & Muffins"
    FROSTINGS_TOPPINGS = "Frostings & Toppings"
    ICE_CREAM = "Ice Cream"
    OTHER = "Other"
    PIES = "Pies"
    MEAT = "Meat"
    POULTRY = "Poultry"
    SEAFOOD = "Seafood"
    SALADS = "Salads"
    SAUCES_DRESSINGS = "Sauces & Dressings"
    SNACKS = "Snacks"
    SOUPS = "Soups"

class Ingredient(BaseModel):
    ingredient_name: str
    quantity: float
    measurement_unit: MeasurementUnit
    notes: str | None = None

class Instruction(BaseModel):
    step_number: int
    description: str

class Recipe(BaseModel):
    title: str
    description: str | None = None
    photo: str | None = None
    category: Category
    ingredients: list[Ingredient]
    instructions: list[Instruction]
    prep_time: str | None = None
    cook_time: str | None = None
    difficulty: int
    servings: int
    yield_: str | None = None
    original_link: str | None = None
    video_link: str | None = None

completion = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extract structured recipe information."},
        {"role": "user", "content": "This is a recipe for a cake."},
    ],
    response_format=Recipe,
)

recipe = completion.choices[0].message.parsed
print(recipe)
