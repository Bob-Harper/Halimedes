import os
import aiohttp
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
news_api_key = os.getenv("NEWSAPIDOTCOM")

async def connect_to_news_api(endpoint_url):
    """
    Handles the connection to the API and returns the JSON response.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint_url) as response:
            if response.status == 200:
                return await response.json()  # Return parsed JSON response
            else:
                return {"error": f"API request failed with status code {response.status}"}
            
async def fetch_top_news():
    """
    Builds the API request for top science and tech news and retrieves the data.
    """
    endpoint = (
        f"https://api.thenewsapi.com/v1/news/top"
        f"?api_token={news_api_key}&locale=ca&language=en&categories=science&limit=3"
        f"&exclude_categories=tech,sports,entertainment,politics,general,food,travel,business,health"
    )

    # Fetch news using the general API connector
    api_response = await connect_to_news_api(endpoint)

    # Check if API response contains an error
    if "error" in api_response:
        return api_response["error"]

    # Parse and format the top news
    news_articles = []
    for article in api_response.get("data", []):
        title = article.get("title", "No title")
        description = article.get("description", "No description")
        news_articles.append(f"{title}: {description}")

    # Return formatted articles or fallback message
    if news_articles:
        return news_articles
    else:
        return ["No relevant news found."]

# Test the function if running this script independently
if __name__ == "__main__":
    async def test():
        news_headlines = await fetch_top_news()
        for headline in news_headlines:
            print("-", headline)

    asyncio.run(test())
