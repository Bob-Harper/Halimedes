import os
import aiohttp
from dotenv import load_dotenv
from datetime import datetime
from helpers.response_utils import Response_Manager  # Import here


# Load environment variables from .env
load_dotenv()
news_api_key = os.getenv("NEWSAPIDOTCOM")


class NewsAPI():
    def __init__(self):
        self.response_manager = Response_Manager()  # No need to pass this manually

    @staticmethod
    async def connect_to_news_api(endpoint_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint_url) as response:
                if response.status == 200:
                    result = await response.json()
                    if "error" in result:
                        return {"error": result["error"]}
                    return result
                else:
                    return {"error": f"API request failed with status code {response.status}"}
                
    async def startup_fetch_news(self, llm_client):
        news_articles = await self.fetch_top_news()
        if isinstance(news_articles, str):  # Check for error message
            await self.response_manager.speak_with_flite("Checking news satellite connection. Status: Offline.")
        else:
            # Store headlines in conversation history for potential reference by the LLM
            formatted_news = "Here are today’s top science and tech headlines:\n" + "\n".join(news_articles)
            llm_client.conversation_history.append({"role": "system", "content": f"If it becomes relevant, here are today's headlines: {formatted_news}"})        
            await self.response_manager.speak_with_flite("Checking news satellite connection. Status: Online.")

    async def fetch_top_news(self):
        """
        Builds the API request for top science and tech news and retrieves the data.
        """
        endpoint = (
            f"https://api.thenewsapi.com/v1/news/top"
            f"?api_token={news_api_key}&locale=ca,us,uk,au,nz&categories=science&limit=3"
            f"&exclude_categories=tech,sports,entertainment,politics,general,food,travel,business,health"
        )

        # Fetch news using the general API connector
        api_response = await self.connect_to_news_api(endpoint)

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

    @staticmethod
    def current_datetime():
        """
        Returns the current date and time as a formatted string.
        """
        return datetime.now().strftime("%A, %B %d, %Y. The time is %I:%M %p.")
    