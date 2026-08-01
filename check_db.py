import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        user="postgres",
        password="TqlVgiuDR8nDimU3",
        database="postgres",
        host="127.0.0.1",
        port=5432
    )

    databases = await conn.fetch(
        "SELECT datname FROM pg_database;"
    )

    for db in databases:
        print(db["datname"])

    await conn.close()


asyncio.run(main())