#!/usr/bin/python3
"""
Task 4: Memory-Efficient Aggregation with Generators
Objective: Use generator to compute memory-efficient aggregate function (average age)
Requirements: Use no more than 2 loops, cannot use SQL AVERAGE, print "Average age of users: {average}"
"""
import seed


def stream_user_ages():
    """
    Generator that yields user ages one by one from the database
    
    Yields: 
        int - age of each user
    """
    connection = seed.connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        # Loop 1: Stream ages one by one
        for row in cursor:
            yield row[0]  # row[0] contains the age value
    
    except Exception as e:
        print(f"Error streaming ages: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    """
    Calculates the average age using the generator without loading 
    the entire dataset into memory
    
    Returns:
        float - calculated average age
    """
    total_age = 0
    count = 0
    
    # Loop 2: Process each age as it's yielded
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age}")
        return average_age
    else:
        print("No users found in database")
        return 0


# Run the calculation when script is executed
if __name__ == "__main__":
    calculate_average_age()