#!/usr/bin/env python3
"""
Custom class-based context manager for database connections
"""
import sqlite3


class DatabaseConnection:
    """
    A custom context manager class for handling database connections
    Automatically opens connection on enter and closes on exit
    """
    
    def __init__(self, database_name):
        """
        Initialize the context manager with database name
        
        Args:
            database_name (str): Path to the SQLite database file
        """
        self.database_name = database_name
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context manager - open database connection
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        self.connection = sqlite3.connect(self.database_name)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - close database connection
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self.connection:
            self.connection.close()


# Usage example
if __name__ == "__main__":
    # Use the context manager with the 'with' statement
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        # Print the results
        print("Users from database:")
        for row in results:
            print(row)