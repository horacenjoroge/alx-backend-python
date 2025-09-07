# Python Generators - Database Streaming

This project demonstrates the use of Python generators for memory-efficient database operations.

## Overview

Python generators allow us to process large datasets without loading everything into memory at once. This is particularly useful when working with databases containing thousands or millions of records.

## Files Description

### `seed.py`
Sets up the MySQL database and populates it with sample data.

**Functions:**
- `connect_db()` - Connects to MySQL server
- `create_database(connection)` - Creates ALX_prodev database
- `connect_to_prodev()` - Connects to ALX_prodev database
- `create_table(connection)` - Creates user_data table
- `insert_data(connection, data)` - Inserts CSV data into database

### `0-stream_users.py`
Basic generator that streams user records one by one.

**Function:**
- `stream_users()` - Generator yielding user dictionaries

### `1-batch_processing.py`
Batch processing implementation using generators.

**Functions:**
- `stream_users_in_batches(batch_size)` - Generator yielding batches of users
- `batch_processing(batch_size)` - Processes batches and filters users over 25

### `2-lazy_paginate.py`
Lazy pagination implementation that only loads pages when needed.

**Functions:**
- `paginate_users(page_size, offset)` - Fetches specific page of users
- `lazy_pagination(page_size)` - Generator for lazy page loading

### `4-stream_ages.py`
Memory-efficient aggregation to calculate average age.

**Functions:**
- `stream_user_ages()` - Generator yielding ages one by one
- `calculate_average_age()` - Calculates average without loading all data

## Database Schema

```sql
CREATE TABLE user_data (
    user_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age DECIMAL(3,0) NOT NULL,
    INDEX idx_user_id (user_id)
);
```

## Prerequisites

1. MySQL server installed and running
2. Python 3.x
3. Required Python packages:
   ```bash
   pip install mysql-connector-python
   ```

## Setup

1. Update database credentials in `seed.py`:
   ```python
   user='your_mysql_username'
   password='your_mysql_password'
   ```

2. Ensure you have `user_data.csv` file with sample data

3. Run the setup:
   ```bash
   python3 seed.py
   ```

## Usage Examples

### Basic Streaming
```python
from itertools import islice
import stream_users

# Get first 6 users
for user in islice(stream_users.stream_users(), 6):
    print(user)
```

### Batch Processing
```python
import batch_processing

# Process users in batches of 50, filter age > 25
batch_processing.batch_processing(50)
```

### Lazy Pagination
```python
import lazy_paginate

# Process 100 users per page
for page in lazy_paginate.lazy_pagination(100):
    for user in page:
        print(user)
```

### Average Age Calculation
```python
import stream_ages

# Calculate average age efficiently
stream_ages.calculate_average_age()
```

## Key Benefits of Generators

1. **Memory Efficiency**: Process large datasets without loading everything into RAM
2. **Lazy Evaluation**: Data is only fetched when needed
3. **Scalability**: Works with datasets of any size
4. **Performance**: Reduces memory usage and can improve processing speed

## Generator Concepts Explained

- **`yield`**: Pauses function execution and returns a value, resuming from that point on next call
- **Memory Efficiency**: Only one record/batch is in memory at a time
- **Lazy Loading**: Data is fetched on-demand rather than all at once
- **Iterators**: Generators implement the iterator protocol automatically

This approach is essential for handling big data applications where memory constraints are critical.