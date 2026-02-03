# mapper-file

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A Python utility for analyzing data files and generating Senzing mapper code. Supports CSV, JSON, JSONL, Parquet, and XML formats.

## Features

- **Schema Analysis** - Discover file structure, data types, and field statistics
- **Grouped Analysis** - Analyze data by category/type with `--group_by`
- **Code Enumeration** - Analyze code values and their distributions
- **Mapper Generation** - Auto-generate Python mapper scripts for Senzing
- **Multiple Formats** - CSV, JSON, JSONL, Parquet, and XML support
- **Filtering** - Filter records by attribute values

## Installation

```bash
# Clone the repository
git clone https://github.com/senzing/mapper-file.git
cd mapper-file

# Create virtual environment
python -m venv ./venv
source ./venv/bin/activate

# Install dependencies
python -m pip install --upgrade pip
python -m pip install --group all .
```

### Optional Dependencies

- `pandas` - Required for Parquet file support
- `numpy` - Enhanced array handling
- `prettytable` - Better formatted console output

## Usage

### Basic Schema Analysis

Analyze a file and display field statistics:

```bash
python src/file_analyzer.py data.csv
```

Output:
```
Statistical Analysis Report:
====================================================================================================
Attribute                 Type            Count    Pct      Unique   Top Value
----------------------------------------------------------------------------------------------------
emp_num                   str             10       100.0    10       7 (1)
last_name                 str             10       100.0    9        Martin (2)
first_name                str             10       100.0    10       Gordon (1)
...
```

### Save Schema to File

```bash
# Save as CSV
python src/file_analyzer.py data.csv -o schema.csv

# Save as Markdown
python src/file_analyzer.py data.csv -o schema.md
```

### Grouped Analysis

Analyze data grouped by an attribute:

```bash
python src/file_analyzer.py employees.csv --group_by job_category
```

Filter to a specific group:

```bash
python src/file_analyzer.py employees.csv --group_by job_category=sales
```

### Generate Mapper Code

Generate a Python mapper script:

```bash
python src/file_analyzer.py data.csv -p mapper.py
```

With grouping (shows which groups have each attribute):

```bash
python src/file_analyzer.py data.csv --group_by record_type -p mapper.py
```

Generated code includes:
```python
# Grouped by: record_type
# Groups found: customer, employee, vendor
#

# attribute: name (str)
# groups: ALL
# 100.0% populated, 95.0% unique
#      John Smith (5)
#      Jane Doe (3)
# json_data.add_feature({"name": raw_data.get("name")})

# attribute: employee_id (str)
# groups: employee
# 45.0% populated, 100.0% unique
# json_data.add_feature({"employee_id": raw_data.get("employee_id")})
```

### Code Enumeration

Analyze code values in specific attributes:

```bash
# Legacy format
python src/file_analyzer.py data.jsonl --enumerate "status,type" -o codes.csv

# Pivot format (cross-tabulate)
python src/file_analyzer.py data.jsonl --enumerate "properties:type,country:number" -o analysis.csv
```

### Auto-detect Code Lists

Automatically find and enumerate low-cardinality fields:

```bash
python src/file_analyzer.py data.csv --detect-codes -o codes.csv
```

### Filtering

Analyze only records matching a filter:

```bash
python src/file_analyzer.py data.jsonl --filter "status=active" -o schema.csv
```

## Supported File Formats

| Format  | Extension | Auto-detect | Notes |
|---------|-----------|-------------|-------|
| CSV     | `.csv`    | Yes         | Auto-detects delimiter |
| JSON    | `.json`   | Yes         | Single JSON object or array |
| JSONL   | `.jsonl`  | Yes         | One JSON object per line |
| Parquet | `.parquet`| Yes         | Requires pandas |
| XML     | `.xml`    | Yes         | Converts elements to dict |

## Command Reference

```
usage: file_analyzer.py [-h] [-t FILE_TYPE] [-e ENCODING] [-o OUTPUT_FILE]
                        [--top_values TOP_VALUES] [--filter FILTER]
                        [--group_by GROUP_BY] [--enumerate ENUMERATE]
                        [--detect-codes] [-p PYTHON_FILE_NAME]
                        input_file

Arguments:
  input_file              Input file or directory path

Options:
  -t, --file_type         File type (auto-detected if not specified)
  -e, --encoding          File encoding (default: utf-8)
  -o, --output_file       Output file path (.csv or .md)
  --top_values            Number of top values to display (default: 5)
  --filter                Filter records: 'attribute=value'
  --group_by              Group by attribute: 'attr' or 'attr=value'
  --enumerate             Enumerate code values
  --detect-codes          Auto-detect code lists
  -p, --python_file_name  Generate Python mapper script
```

## Development

### Linting

```bash
# Run pylint
pylint $(git ls-files '*.py' ':!:docs/source/*')

# Format with black
black .

# Sort imports
isort .

# Security check
bandit -r src/

# Type checking
mypy src/
```

### Running Tests

```bash
pytest
```

## License

[Apache License 2.0](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- [Issue Tracker](https://github.com/senzing/mapper-file/issues)
- [Changelog](https://github.com/senzing/mapper-file/blob/main/CHANGELOG.md)
