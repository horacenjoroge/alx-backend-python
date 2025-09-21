# Utils Module Testing Project

This project contains utility functions for GitHub organization client operations and their corresponding unit tests.

## Project Structure

```
.
├── README.md
├── utils.py          # Utility functions module
└── test_utils.py     # Unit tests for utils module
```

## Modules

### utils.py
Contains generic utility functions including:
- `access_nested_map`: Access nested dictionaries/mappings using a key path
- `get_json`: Retrieve JSON data from remote URLs
- `memoize`: Decorator for memoizing method results

### test_utils.py
Contains unit tests for the utility functions using Python's unittest framework and parameterized testing.

## Requirements

- Python 3.7 (Ubuntu 18.04 LTS)
- All files follow pycodestyle (version 2.5)
- All functions and classes are properly documented
- All functions are type-annotated
- All files are executable and end with a newline

## Dependencies

- `requests`: For HTTP operations
- `parameterized`: For parameterized testing
- `unittest`: For unit testing (built-in)

## Usage

### Running Tests
```bash
python3 test_utils.py
```

### Example Usage of access_nested_map
```python
from utils import access_nested_map

nested_data = {"a": {"b": {"c": 1}}}
result = access_nested_map(nested_data, ["a", "b", "c"])
print(result)  # Output: 1
```

## Testing

The project includes comprehensive unit tests for the `access_nested_map` function, testing various nested dictionary structures and access paths to ensure reliable functionality.

## Code Style

All code follows PEP 8 guidelines and pycodestyle standards for consistent formatting and readability.