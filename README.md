# mapper-file

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Overview

**file_analyzer.py** analyzes source data files and generates Python mapper scripts that transform the data into Senzing JSON format for entity resolution.

It does two jobs in one tool:

1. **Shows you what's in your data** — attribute names, data types, how populated each field is, how unique the values are, and sample values
2. **Writes the starter code** — a complete, runnable Python mapper script with every attribute pre-populated, each annotated with statistics and a commented-out mapping call ready for you to edit

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

- `pandas` — Required for Parquet file support
- `numpy` — Enhanced array handling
- `prettytable` — Better formatted console output

## Typical Use

The typical workflow is: analyze your data, generate a mapper script, edit the script to assign Senzing feature types, then run it.

### Step 1: Analyze your source file

Run file_analyzer.py on your data file to see what you're working with:

```bash
python src/file_analyzer.py employees.csv
```

Output:

```
Attribute                 Type            Count    Pct      Unique   Top Value
----------------------------------------------------------------------------------------------------
emp_num                   str             10       100.0    10       7 (1)
last_name                 str             10       100.0    9        Martin (2)
first_name                str             10       100.0    10       Gordon (1)
addr1                     str             10       100.0    10       963 Maple Street (1)
city                      str             10       100.0    9        Anaheim (2)
ssn                       str             10       100.0    10       546-95-7680 (1)
job_category              str             10       100.0    5        sales (4)
salary                    str             10       100.0    3        50k (4)
rehire_flag               str             10       100.0    1        null (10)
...
```

This tells you at a glance:

- **Count / Pct** — How many records have this field populated (and what percentage)
- **Unique** — How many distinct values exist. High uniqueness (like `emp_num` at 10/10) suggests an identifier. Low uniqueness (like `salary` at 3/10) suggests a code or category.
- **Top Value** — The most common values and their frequencies

You can also save the schema to a file for reference:

```bash
python src/file_analyzer.py employees.csv -o schema.md    # Markdown format
python src/file_analyzer.py employees.csv -o schema.csv   # CSV format
```

### Step 2: Generate the mapper script

```bash
python src/file_analyzer.py employees.csv -p employee_mapper.py
```

This generates a complete, runnable Python script. Inside the `map_record()` function, every attribute from your data appears as a block like this:

```python
# attribute: last_name (str)
# 100.0% populated, 90.0% unique
#      Martin (2)
#      Mcpherson (1)
#      Spector (1)
#      Furman (1)
#      Angel (1)
# json_data.add_feature({"last_name": raw_data.get("last_name")})
```

Each block includes the statistics as comments so you can make mapping decisions right in the code, and a **commented-out** `add_feature()` call ready for you to edit.

The script also includes placeholder lines you need to fill in:

```python
json_data.set_data_source("")       # supply a value for this data source
json_data.set_record_id(raw_data[""])   # supply a 100% unique attribute
json_data.set_record_type("")       # should be PERSON or ORGANIZATION
```

### Step 3: Edit the generated code

This is where you decide what each attribute means to Senzing. Go through each attribute block and choose one of three actions:

**Uncomment and edit `add_feature()`** — for attributes Senzing should use for entity resolution (names, addresses, phones, DOB, SSN, IDs). Features go into the `FEATURES` array and Senzing uses them for matching.

**Change to `add_payload()`** — for supplemental data you want to keep but not use for matching (job title, salary, hire date). Payload attributes become peer-level JSON attributes in the output.

**Leave commented out** — for attributes you don't need at all.

#### Before and after example

Here's what the generated code looks like for a few attributes, and what the edited version looks like:

**Generated (before editing):**

```python
# attribute: last_name (str)
# 100.0% populated, 90.0% unique
#      Martin (2)
# json_data.add_feature({"last_name": raw_data.get("last_name")})

# attribute: first_name (str)
# 100.0% populated, 100.0% unique
#      Gordon (1)
# json_data.add_feature({"first_name": raw_data.get("first_name")})

# attribute: ssn (str)
# 100.0% populated, 100.0% unique
#      546-95-7680 (1)
# json_data.add_feature({"ssn": raw_data.get("ssn")})

# attribute: job_category (str)
# 100.0% populated, 50.0% unique
#      sales (4)
# json_data.add_feature({"job_category": raw_data.get("job_category")})
```

**Edited (after your changes):**

```python
# attribute: last_name (str)
# 100.0% populated, 90.0% unique
#      Martin (2)
json_data.add_feature("NAME1", {"NAME_LAST": raw_data.get("last_name")})

# attribute: first_name (str)
# 100.0% populated, 100.0% unique
#      Gordon (1)
json_data.add_feature("NAME1", {"NAME_FIRST": raw_data.get("first_name")})

# attribute: ssn (str)
# 100.0% populated, 100.0% unique
#      546-95-7680 (1)
json_data.add_feature({"SSN_NUMBER": raw_data.get("ssn")})

# attribute: job_category (str)
# 100.0% populated, 50.0% unique
#      sales (4)
json_data.add_payload({"job_category": raw_data.get("job_category")})
```

Notice:

- **`last_name` and `first_name`** are grouped under `"NAME1"` — this tells Senzing they belong to the same name feature. The dict keys use Senzing attribute names (`NAME_LAST`, `NAME_FIRST`).
- **`ssn`** is a standalone feature — no group name needed, just the Senzing attribute name `SSN_NUMBER`.
- **`job_category`** is changed to `add_payload()` — it's kept in the output but not used for matching.

#### Grouped features

When related fields should be treated as a single feature, use the same group name:

```python
# Name fields → one name feature
json_data.add_feature("NAME1", {"NAME_FIRST": raw_data.get("first_name")})
json_data.add_feature("NAME1", {"NAME_LAST": raw_data.get("last_name")})
json_data.add_feature("NAME1", {"NAME_MIDDLE": raw_data.get("middle_name")})

# Address fields → one address feature
json_data.add_feature("ADDR1", {"ADDR_LINE1": raw_data.get("addr1")})
json_data.add_feature("ADDR1", {"ADDR_CITY": raw_data.get("city")})
json_data.add_feature("ADDR1", {"ADDR_STATE": raw_data.get("state")})
json_data.add_feature("ADDR1", {"ADDR_POSTAL_CODE": raw_data.get("zip")})
```

#### Fill in the header fields

```python
json_data.set_data_source("EMPLOYEES")
json_data.set_record_id(raw_data["emp_num"])
json_data.set_record_type("PERSON")
```

### Step 4: Run the mapper

**Interactive mode** — review records one at a time:

```bash
python employee_mapper.py employees.csv
```

```
--- Record 1 ---
{
    "DATA_SOURCE": "EMPLOYEES",
    "RECORD_ID": "1",
    "RECORD_TYPE": "PERSON",
    "FEATURES": [
        {"NAME_FIRST": "Gordon", "NAME_LAST": "Mcpherson", "NAME_MIDDLE": "P"},
        {"ADDR_LINE1": "963 Maple Street", "ADDR_CITY": "Anaheim", "ADDR_STATE": "CA", "ADDR_POSTAL_CODE": "92805"},
        {"PHONE_NUMBER": "714-387-2863"},
        {"DATE_OF_BIRTH": "3/28/64"},
        {"SSN_NUMBER": "546-95-7680"},
        {"EMPLOYER": "ABC Company"}
    ],
    "job_category": "management",
    "job_title": "Level 1 manager",
    "hire_date": "1/10/10",
    "salary": "100k"
}
Press Enter for next, 'r' to show raw source (Ctrl+C to abort):
```

**Batch mode** — write all records to a JSONL file:

```bash
python employee_mapper.py employees.csv -o employees.jsonl
```

The output JSONL file is ready to load into Senzing.

## Additional Options

### Grouped analysis (`--group_by`)

When your data has multiple record types in one file, group the analysis by a category attribute:

```bash
python src/file_analyzer.py data.csv --group_by record_type
```

This shows which groups contain each attribute. When combined with `-p`, the generated code includes group annotations:

```python
# attribute: name (str)
# groups: ALL
# 100.0% populated, 95.0% unique
# json_data.add_feature({"name": raw_data.get("name")})

# attribute: employee_id (str)
# groups: employee
# 45.0% populated, 100.0% unique
# json_data.add_feature({"employee_id": raw_data.get("employee_id")})
```

Filter to a specific group:

```bash
python src/file_analyzer.py data.csv --group_by record_type=employee
```

### Code enumeration (`--enumerate`)

Deep-dive into code values and their distributions:

```bash
# Legacy format — list codes in specific attributes
python src/file_analyzer.py data.jsonl --enumerate "status,type" -o codes.csv

# Pivot format — cross-tabulate dimensions against values
python src/file_analyzer.py data.jsonl --enumerate "properties:type,country:number" -o analysis.csv
```

### Auto-detect code lists (`--detect-codes`)

Automatically find low-cardinality fields and enumerate their values:

```bash
python src/file_analyzer.py data.csv --detect-codes -o codes.csv
```

### Filtering (`--filter`)

Focus the analysis on a subset of records:

```bash
python src/file_analyzer.py data.jsonl --filter "status=active"
```

### Top values (`--top_values`)

Control how many sample values are shown per attribute (default: 5):

```bash
python src/file_analyzer.py data.csv --top_values 10
```

### Save schema output (`-o`)

```bash
python src/file_analyzer.py data.csv -o schema.md    # Markdown
python src/file_analyzer.py data.csv -o schema.csv   # CSV
```

## Supported File Formats

| Format  | Extension  | Auto-detect | Notes                      |
|---------|------------|-------------|----------------------------|
| CSV     | `.csv`     | Yes         | Auto-detects delimiter     |
| JSON    | `.json`    | Yes         | Single JSON object or array|
| JSONL   | `.jsonl`   | Yes         | One JSON object per line   |
| Parquet | `.parquet` | Yes         | Requires pandas            |
| XML     | `.xml`     | Yes         | Converts elements to dict  |

## Command Reference

```
usage: file_analyzer.py [-h] [-t FILE_TYPE] [-e ENCODING] [-o OUTPUT_FILE]
                        [--top_values TOP_VALUES] [--filter FILTER]
                        [--group_by GROUP_BY] [--enumerate ENUMERATE]
                        [--detect-codes] [-p PYTHON_FILE_NAME]
                        input_file

positional arguments:
  input_file              Input file or directory path

options:
  -h, --help              Show help message
  -t, --file_type         File type (auto-detected if not specified)
  -e, --encoding          File encoding (default: utf-8)
  -o, --output_file       Save schema to file (.md or .csv)
  -p, --python_file_name  Generate Python mapper script
  --top_values            Number of top values to display (default: 5)
  --filter                Filter records: 'attribute=value'
  --group_by              Group by attribute: 'attr' or 'attr=value'
  --enumerate             Enumerate code values (requires -o)
  --detect-codes          Auto-detect and enumerate code lists
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
