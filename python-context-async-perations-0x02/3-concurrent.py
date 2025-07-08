import asyncio
import aiosqlite

# Async function to fetch all users
async def async_fetch_users():
    async with aiosqlite.connect("ALX_prodev.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print("\nAll Users:")
            for user in users:
                print(user)
            return users

# Async function to fetch users older than 40
async def async_fetch_older_users():
    async with aiosqlite.connect("ALX_prodev.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            older_users = await cursor.fetchall()
            print("\nUsers older than 40:")
            for user in older_users:
                print(user)
            return older_users

# Function to run both queries concurrently
async def fetch_concurrently():
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# Run the asynchronous tasks
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
