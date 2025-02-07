# Recipe Scraper API

A fast API that scrapes recipes from websites, extracts structured data using an LLM, and returns it in JSON format.

## Features
- Scrapes recipes from any webpage, including Instagram posts.
- Uses OpenAI's GPT-4o-mini to extract structured recipe data.
- Returns a well-defined JSON schema with ingredients, instructions, and metadata.

## Installation
1. Clone the repo:
   ```sh
   git clone https://github.com/yourusername/recipe-scraper.git
   cd recipe-scraper
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up `.env` with your OpenAI API key:
   ```sh
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage
Run the API:
```sh
uvicorn scraper:app --host 0.0.0.0 --port 8000
```

Hit the endpoint:
```sh
GET /recipe?url=your_recipe_url
```

## License
MIT

****
