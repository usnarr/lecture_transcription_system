from dotenv import load_dotenv
import os
import psycopg
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")

async def get_db_connection() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    conn = None
    try:
        conn = await psycopg.AsyncConnection.connect(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        logger.info("Database connection established")
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            await conn.close()
            logger.info("Database connection closed")