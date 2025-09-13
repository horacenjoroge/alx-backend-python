import time
import sqlite3 
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Call the function with connection as first argument
            return func(conn, *args, **kwargs)
        finally:
            # Always close the connection
            conn.close()
    return wrapper

query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key based on function name and arguments
        # Look for the query in args or kwargs
        query = None
        if len(args) > 1:  # conn is first arg, query might be second
            query = args[1]
        elif 'query' in kwargs:
            query = kwargs['query']
        
        # Create cache key using function name and query
        cache_key = f"{func.__name__}:{query}" if query else f"{func.__name__}:{str(args[1:])}{str(kwargs)}"
        
        # Check if result is already cached
        if cache_key in query_cache:
            print(f"Cache hit for query: {query}")
            return query_cache[cache_key]
        
        # If not cached, execute the function and cache the result
        print(f"Cache miss for query: {query}")
        result = func(*args, **kwargs)
        query_cache[cache_key] = result
        
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")