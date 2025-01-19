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
else:
    print("OPENAI_API_KEY:", OPENAI_API_KEY)

graph_config = {
   "llm": {
        "api_key": OPENAI_API_KEY,
        "model": "gpt-3.5-turbo",
   },
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
   prompt="List me all the projects with their description.",
   # also accepts a string with the already downloaded HTML code
   source="https://perinim.github.io/projects/",
   config=graph_config
)

result = smart_scraper_graph.run()
print(result)
