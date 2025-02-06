from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from enum import Enum
from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import instagram_scraper as instagram_scraper
import uvicorn

# Load the .env file
load_dotenv()

# Create server
app = FastAPI()

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
    prep_time: int | None = None
    cook_time: int | None = None
    difficulty: int
    servings: int
    yield_: int | None = None
    original_link: str | None = None
    video_link: str | None = None


# Function to scrape the webpage and extract raw HTML
def scrape_html_classical(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        cleaned_text = soup.get_text()
        return cleaned_text
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching the URL: {str(e)}")

def is_instagram_url(url: str) -> bool:
    parsed_url = urlparse(url)
    return parsed_url.netloc.endswith("instagram.com")

def scrape_url(url: str) -> str:
    if(is_instagram_url(url)):
        print("Instagram URL detected")
        return instagram_scraper.get_instagram_post(url)
    else:
        print("Classical URL detected")
        return scrape_html_classical(url)


prompt = """ Extract structured recipe information from the given text and return it in JSON format matching the Recipe schema.
    Notes: You are allowed to predict or infer the following information if you don't find it in the text:
    2- measurement_unit
    3- yield
    4- prep_time
    5- cook_time
    6- difficulty
 """

# Function to extract structured recipe information using OpenAI
def extract_recipe(scraped_content: str) -> Recipe:

    # Call OpenAI API to extract structured data
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": scraped_content},
        ],
        response_format=Recipe,
    )

    recipe = completion.choices[0].message.parsed
    # Convert JSON response to Recipe object
    return recipe


# API endpoint to extract recipe from a URL
@app.get("/recipe", response_model=Recipe)
def get_recipe(url: str):
    scraped_content = scrape_url(url)
    recipe = extract_recipe(scraped_content)
    return recipe

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
