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
