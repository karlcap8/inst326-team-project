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
