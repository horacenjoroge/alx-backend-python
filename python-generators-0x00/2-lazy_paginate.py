#!/usr/bin/python3
"""
Task 3: Lazy loading Paginated Data
Objective: Simulate fetching paginated data using generator to lazily load each page
Requirements: Use only 1 loop, include paginate_users function, must use yield
"""
import seed


def paginate_users(page_size, offset):
    """
    Fetches a specific page of users from the database
    
    Args:
        page_size (int) - number of users per page
        offset (int) - starting position for the page
    
    Returns: 
        list - list of user dictionaries for the requested page
    """
    connection = seed.connect_to_prodev()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        return rows
    
    except Exception as e:
        print(f"Error paginating users: {e}")
        return []
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def lazy_pagination(page_size):
    """
    Generator that lazily loads pages of user data
    Only fetches the next page when needed at an offset starting from 0
    
    Args: 
        page_size (int) - number of users per page
    
    Yields: 
        list - list of user dictionaries for each page
    """
    offset = 0
    
    # Single loop as required - continues until no more pages
    while True:
        page = paginate_users(page_size, offset)
        
        if not page:  # No more data to paginate
            break
            
        yield page
        offset += page_size