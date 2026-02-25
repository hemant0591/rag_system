import asyncio
from sqlalchemy import text
from app.core.database import engine


async def test_connection():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB connected:", result.scalar())


if __name__ == "__main__":
    asyncio.run(test_connection())