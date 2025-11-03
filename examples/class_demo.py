# for dataset.py

from src.dataset import Dataset

rows = [
    {"Q1": "19", "Q2": "Yes", "Email Address": "a@b.com", "joined": "2024-10-01"},
    {"Q1": "21", "Q2": "No",  "Email Address": "c@d.com", "joined": "2024-10-03"},
]

ds = Dataset(
    rows,
    name="pilot_survey",
    rename_map={"Q1": "age", "Q2": "consent", "Email Address": ""},  # drop PII
    type_map={"age": "int", "consent": "bool", "joined": "datetime:%Y-%m-%d"},
    pii_columns=set(),  # not needed because we drop via rename_map above
)

ds.clean_headers()
ds.apply_rename_map()
ds.cast_types()

issues = ds.validate({
    "age": {"type": "int", "min": 0, "max": 120, "required": True},
    "consent": {"type": "bool", "required": True},
    "joined": {"type": "datetime:%Y-%m-%d", "required": True},
})

print(ds)
print("Columns:", ds.columns)
print("Issues:", len(issues))
print("Snapshot:", ds.snapshot())




#Sukhman Class demo

import pandas as pd
from src.data_pipeline import DataPipeline  # adjust import if needed

# -- Sample Data --

# First dataset: some messy text, missing values
df1 = pd.DataFrame({
    "Name": [" Alice ", "Bob ", "  Carol"],
    "Age": [25, None, 29],
    "Department": ["Research ", " Dev", " Research"]
})

# Second dataset: another batch to merge
df2 = pd.DataFrame({
    "Name": ["Dave", "Eve"],
    "Age": [31, 27],
    "Department": ["Dev", "Research"]
})

# -- Create and Run the Pipeline --

pipeline = DataPipeline(df1, name="employee_batch_1")

# Step 1: Strip whitespace from all string columns
pipeline.strip_text()

# Step 2: Fill missing numeric values (using mean strategy)
pipeline.fill_missing(strategy="mean")

# Step 3: Merge with a second dataset
pipeline.merge([df2], how="outer")

# Step 4: Generate a data report (saved to file)
report_path = pipeline.generate_report("output/employee_report.txt")

# -- Print Results --

print(pipeline)
print("Name:", pipeline.name)
print("Shape:", pipeline.shape)
print("History:", pipeline.history)
print("Cleaned?:", pipeline.is_cleaned)
print("Snapshot preview:\n", pipeline.snapshot().head())
print("Report saved to:", report_path)



#Harrang class demo

import pandas as pd
from src.data_analysis import DataAnalysis 

# Sample DataFrame: Employee data with age and email
df = pd.DataFrame({
    'age': [25, 30, 35, 40, 22],
    'email': ['test@example.com', 'invalid-email', 'user@example.com', 'another@example.com', 'valid@domain.com']
})

# Initialize DataAnalysis class with the sample DataFrame
analysis = DataAnalysis(df)

# -- 1. Validate Email --
print("Email Validation:")
emails_to_check = [
    "test@example.com",
    "invalid-email",
    "user@example.com",
    "another@example.com",
    "valid@domain.com"
]
for email in emails_to_check:
    print(f"{email}: {analysis.validate_email(email)}")

# -- 2. Filter Rows by Condition (Age > 30) --
print("\nFiltered Rows (Age > 30):")
filtered_df = analysis.filter_rows_by_condition(lambda row: row['age'] > 30)
print(filtered_df)

# -- 3. Count Unique Values --
print("\nCount of Unique Values in Columns:")
unique_counts = analysis.count_unique_values()
print(unique_counts)

# -- 4. Pivot and Aggregate Data (Summing Ages per Email) --
print("\nPivot and Aggregate Data (Summing Ages per Email):")
pivot_df = analysis.pivot_and_aggregate('email', 'age', agg_func='sum')
print(pivot_df)

# -- 5. Show String Representations --
print("\nString Representations:")
print(str(analysis))  # __str__ method
print(repr(analysis))  # __repr__ method

# -- 6. Access History and Cleaned Status --
print("\nOperation History:")
print(analysis.history)

print("\nCleaned Status:")
print(analysis.is_cleaned)
