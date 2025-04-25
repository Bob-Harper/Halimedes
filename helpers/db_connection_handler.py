import aiomysql
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DbConnectionHandler:
    def __init__(self):
        self.pool = None

    async def init_db(self):
        """Initialize a connection pool."""
        if not self.pool:
            self.pool = await aiomysql.create_pool(
                host=os.getenv("SQLHOST"),
                port=int(os.getenv("SQLPORT", 3306)),  # Default MySQL port
                user=os.getenv("SQLUSER"),
                password=os.getenv("SQLPASSWORD"),
                db=os.getenv("SQLDATABASE"),
                loop=asyncio.get_event_loop(),
                autocommit=True
            )

    async def close_db(self):
        """Close the connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def fetch_prompt(self, speaker_name):
        """Fetch the appropriate prompt for a recognized speaker."""
        if not self.pool:
            await self.init_db()

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT prompt_template FROM custom_prompts WHERE name = %s", (speaker_name,))
                result = await cursor.fetchone()
                return result[0] if result else None  # Return the prompt or None
