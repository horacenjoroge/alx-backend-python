#!/usr/bin/python3
"""
Task 1: Generator that streams rows from an SQL database one by one
Objective: Create a generator using yield to fetch users one by one
Requirements: Use only 1 loop, must use yield generator
"""
import seed


def stream_users():
    """
    Generator that yields user data one by one from the database
    Uses yield to create a generator for memory-efficient streaming
    
    Yields: dict - user information with keys: user_id, name, email, age
    """
    connection = seed.connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        # Single loop as required - yield each row one by one
        for row in cursor:
            yield {
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'age': row['age']
            }
    
    except Exception as e:
        print(f"Error streaming users: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()