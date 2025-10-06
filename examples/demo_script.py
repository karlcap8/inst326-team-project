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
