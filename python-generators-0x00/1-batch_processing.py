#!/usr/bin/python3
"""
Task 2: Batch processing Large Data
Objective: Create generator to fetch and process data in batches, filter users over age 25
Requirements: Use no more than 3 loops, must use yield generator
"""
import seed


def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows in batches from the database
    
    Args: 
        batch_size (int) - number of rows to fetch in each batch
    
    Yields: 
        list - batch of user dictionaries
    """
    connection = seed.connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        
        # Loop 1: Continue fetching batches until no more data
        while True:
            cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
            batch = cursor.fetchall()
            
            if not batch:  # No more data to fetch
                break
                
            yield batch
            offset += batch_size
    
    except Exception as e:
        print(f"Error streaming batches: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25
    
    Args: 
        batch_size (int) - size of each batch to process
    """
    # Loop 2: Process each batch
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Process each user in the batch (filter age > 25)
        for user in batch:
            if user['age'] > 25:
                print(user)