# Simple 1- Karl
from src.research_data_lib import normalize_header

headers = ["Q3 - Overall Satisfaction (1-5)", "Email Address", "123"]
print([normalize_header(h) for h in headers])

# Medium 1- Karl
from src.research_data_lib import cast_row_types

row = {'age': '19', 'score': '3.5', 'consent': 'Yes', 'joined': '2024-10-01', 'note': 'ok'}
type_map = {
    'age': 'int',
    'score': 'float',
    'consent': 'bool',
    'joined': 'datetime:%Y-%m-%d'
}

print(cast_row_types(row, type_map))
# Expected keys cast: age -> 19, score -> 3.5, consent -> True, joined -> datetime(2024,10,1)

# Medium 2 - Karl
from src.research_data_lib import rename_columns

row = {"Q1": "19", "Q2": "Yes", "Email Address": "a@b.com", "Note": "ok"}
rename_map = {
    "Q1": "age",
    "Q2": "consent",
    "Email Address": "",   # drop PII
    # "Note" unmapped -> kept by default
}

print(rename_columns(row, rename_map))
# Expected example:
# {'age': '19', 'consent': 'Yes', 'Note': 'ok'}


# Complex 1 - Karl
from src.research_data_lib import validate_dataset

rows = [
    {"id": "A1", "age": "19", "consent": "Yes", "score": "3.5", "joined": "2024-10-01"},
    {"id": "A2", "age": "-5", "consent": "no",  "score": "x",   "joined": "2024-13-01"},
    {"id": "A1", "age": "200", "consent": "Y",  "score": "4.2", "joined": "2024-09-30"},
    {"id": "",   "age": "  ",  "consent": "",   "score": "",    "joined": ""},
]

rules = {
    "id": {"type": "str", "required": True, "len_min": 1, "unique": True},
    "age": {"type": "int", "min": 0, "max": 120, "required": True},
    "consent": {"type": "bool", "required": True},
    "score": {"type": "float", "min": 0.0, "max": 5.0},
    "joined": {"type": "datetime:%Y-%m-%d"},
}

issues = validate_dataset(rows, rules)
print(f"Issues found: {len(issues)}")
for e in issues:
    print(e)
# Expect: type/range/required/unique violations across several rows



#Sukhman - Simple Function Demo
from src.research_data_lib import strip_whitespace
import pandas as pd

raw_df = pd.DataFrame({
    "Name": ["  Sydney  ", " Jordan", "Tommy "],
    "Email": [" alice@email.com ", "bob@email.com ", " charlie@email.com"],
    "Score": [85, 90, 78]
})

print("Original DataFrame:")
print(raw_df)

clean_df = strip_whitespace(raw_df)

print("\nAfter strip_whitespace():")
print(clean_df)

# Expected: No leading/trailing spaces in string columns
# Original DataFrame remains unchanged
print("\nCheck original unchanged:", raw_df.equals(clean_df) is False)


# Sukhman - Medium Function Demo 1
from src.research_data_lib import merge_datasets
import pandas as pd

df1 = pd.DataFrame({
    "ID": [1, 2, 3],
    "Name": ["John", "Jessie", "Andrew"],
    "Score": [85, 90, 78]
})

df2 = pd.DataFrame({
    "ID": [2, 3, 4],
    "City": ["NYC", "LA", "Chicago"]
})

merged_df = merge_datasets([df1, df2], how="outer")
print("\nMerged DataFrame:")
print(merged_df)

# Expected:
# Includes all IDs 1–4
# Columns: ID, Name, Score, City
# NaN values where data is missing


# Sukhman - Medium Function Demo 2
from src.research_data_lib import fill_missing_values
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Math": [85, np.nan, 78],
    "Science": [np.nan, 90, np.nan],
    "English": [88, 92, np.nan]
})

print("Original DataFrame:")
print(df)

filled_df = fill_missing_values(df, strategy="mean")
print("\nAfter fill_missing_values(strategy='mean'):")
print(filled_df)

# Expected:
# Missing numeric values replaced with column means.
# Original DataFrame unchanged.


# Sukhman - Complex Function Demo
from src.research_data_lib import generate_data_report
import pandas as pd
import os

data = {
    "Name": ["Gemma", "Harry", "Jaden", "David"],
    "Score": [85, None, 78, 90],
    "City": ["NYC", "LA", "Chicago", None]
}
df = pd.DataFrame(data)

report_path = generate_data_report(df, "outputs/demo_data_report.txt")

print("\nReport generated at:", report_path)
print("File exists:", os.path.exists(report_path))

# Expected:
# File "outputs/demo_data_report.txt" created
# Contains summary stats (missing %, unique counts, sample values)




# Harrang -  Simple Demo
from src.research_data_lib import validate_email

# Valid email
valid_email = "test@example.com"
print(f"Is '{valid_email}' a valid email? {validate_email(valid_email)}")

# Invalid email
invalid_email = "invalid-email"
print(f"Is '{invalid_email}' a valid email? {validate_email(invalid_email)}")

# Expected output:
# Is 'test@example.com' a valid email? True
# Is 'invalid-email' a valid email? False


# Harrang - Medium Demo
import pandas as pd
from src.research_data_lib import filter_rows_by_condition

# Sample DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 35, 40, 20],
    'city': ['NY', 'LA', 'SF', 'LA']
}
df = pd.DataFrame(data)

# Filter rows where age is greater than 30
filtered_df = filter_rows_by_condition(df, lambda row: row['age'] > 30)

print("Filtered DataFrame (age > 30):")
print(filtered_df)

# Expected output:
# Filtered DataFrame (age > 30):
#     name  age city
# 1    Bob   35   LA
# 2  Charlie   40   SF


# Harrang - Medium Demo 2
import pandas as pd
from src.research_data_lib import count_unique_values

# Sample DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Alice'],
    'age': [25, 35, 40, 25],
    'city': ['NY', 'LA', 'SF', 'NY']
}
df = pd.DataFrame(data)

# Count unique values in each column
unique_counts = count_unique_values(df)

print("Unique Value Counts:")
print(unique_counts)

# Expected output:
# Unique Value Counts:
# {'name': 3, 'age': 3, 'city': 3}


# Harrang - Complex Demo
import pandas as pd
from src.research_data_lib import pivot_and_aggregate

# Sample DataFrame
data = {
    'category': ['A', 'A', 'B', 'B', 'A', 'B'],
    'sales': [100, 150, 200, 250, 120, 300]
}
df = pd.DataFrame(data)

# Pivot the DataFrame by 'category' and aggregate 'sales' using the sum
pivot_df = pivot_and_aggregate(df, pivot_column='category', value_column='sales', agg_func='sum')

print("Pivoted and Aggregated DataFrame (sum of sales):")
print(pivot_df)

# Expected output:
# Pivoted and Aggregated DataFrame (sum of sales):
#            sales
# category        
# A            370
# B            750




# Simple 1 - Demo - Removing punctuation from string columns

from src.research_data_lib import remove_punctuation
import pandas as pd

# Sample DataFrame
data = {
    "Name": ["Alice!", "Bob?", "Charlie."],
    "Email": ["alice@email.com", "bob@email.com", "charlie@email.com"],
    "Score": [90, 85, 88]
}

df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Cleaned DataFrame
clean_df = remove_punctuation(df)

print("\nAfter remove_punctuation():")
print(clean_df)

# Expected output: No punctuation in "Name" and "Email" columns.


# Medium 1 - Demo - Handling outliers in numeric columns

from src.research_data_lib import handle_outliers
import pandas as pd

# Sample DataFrame with outliers
data = {
    "Age": [25, 30, 35, 40, 500],
    "Score": [88, 92, 95, 78, 1000]
}

df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Handle outliers
clean_df = handle_outliers(df, threshold=1.5)

print("\nAfter handle_outliers():")
print(clean_df)



# Medium 2 - Demo - Splitting multi-response column into separate binary columns

from src.research_data_lib import split_multi_response
import pandas as pd

# Sample DataFrame with multi-response column
data = {
    "Responses": ["Yes, No", "Yes, Maybe", "No, Maybe"]
}

df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Split the multi-response column into separate binary columns
split_df = split_multi_response(df, column_name="Responses", delimiter=", ")

print("\nAfter split_multi_response():")
print(split_df)

# Expected output:
# A new DataFrame where the 'Responses' column is split into separate binary columns:
# 'Responses_response_1', 'Responses_response_2', etc., with 1 or 0 indicating presence/absence of a response.



# Complex 1 - Demo - Data profiling and report generation

from src.research_data_lib import generate_data_profile
import pandas as pd
import os

# Sample DataFrame with missing values and categorical data
data = {
    "Name": ["Alice", "Bob", "Charlie", "David"],
    "Age": [25, 30, 35, None],
    "Score": [90, None, 88, 92],
    "City": ["NYC", "LA", "Chicago", "Chicago"]
}

df = pd.DataFrame(data)

# Generate the data profiling report
report_path = generate_data_profile(df, report_file="outputs/demo_data_report.txt")

print("\nReport generated at:", report_path)
print("File exists:", os.path.exists(report_path))

# Expected output:
# A report file "outputs/demo_data_report.txt" is generated.
# The report contains:
# - Missing percentage for each column
# - Unique values count
# - Statistical summary for numeric columns (mean, min, max, etc.)
# - Histograms for numeric columns and bar charts for categorical columns

