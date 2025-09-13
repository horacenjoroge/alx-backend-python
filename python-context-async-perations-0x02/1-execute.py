#!/usr/bin/env python3
"""
Reusable Query Context Manager
"""
import sqlite3


class ExecuteQuery:
    """
    A reusable context manager that executes SQL queries
    Manages both connection and query execution
    """
    
    def __init__(self, database_name, query, params=None):
        """
        Initialize the query context manager
        
        Args:
            database_name (str): Path to the SQLite database file
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
        """
        self.database_name = database_name
        self.query = query
        self.params = params if params is not None else ()
        self.connection = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - open connection and execute query
        
        Returns:
            list: Query results
        """
        self.connection = sqlite3.connect(self.database_name)
        cursor = self.connection.cursor()
        
        if self.params:
            cursor.execute(self.query, self.params)
        else:
            cursor.execute(self.query)
        
        self.results = cursor.fetchall()
        cursor.close()
        return self.results
    
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
    # Use the reusable query context manager
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    
    with ExecuteQuery('users.db', query, params) as results:
        print("Users older than 25:")
        for row in results:
            print(row)