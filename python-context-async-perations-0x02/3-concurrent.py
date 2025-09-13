#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries
"""
import asyncio
import aiosqlite


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database
    
    Returns:
        list: All user records from the database
    """
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        print("All users fetched")
        return users


async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database
    
    Returns:
        list: User records where age > 40
    """
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        older_users = await cursor.fetchall()
        await cursor.close()
        print("Users older than 40 fetched")
        return older_users


async def fetch_concurrently():
    """
    Execute both fetch functions concurrently using asyncio.gather
    
    Returns:
        tuple: Results from both queries (all_users, older_users)
    """
    print("Starting concurrent database queries...")
    
    # Execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print(f"Total users: {len(all_users)}")
    print(f"Users older than 40: {len(older_users)}")
    
    return all_users, older_users


# Main execution
if __name__ == "__main__":
    # Run the concurrent fetch operation
    asyncio.run(fetch_concurrently())