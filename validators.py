 from dataclasses import dataclass
 from typing import List, Dict
 from research_data_lib import validate_dataset

 @dataclass
 class ValidationIssue:
 	row_idx: int
 	column: str
 	rule: str
 	value: object
 	message: str

 @dataclass
 class ValidationReport:
 	issues: List[ValidationIssue]
 	@property
 	def is_valid(self): return not self.issues
 	def to_markdown(self):
     	if not self.issues: return "All checks passed ✅"
     	lines = ["|Row|Column|Rule|Value|Message|","|--|--|--|--|--|"]
     	for i in self.issues:
             lines.append(f"|{i.row_idx}|{i.column}|{i.rule}|{i.value}|{i.message}|")
     	return "\n".join(lines)

 class RulesValidator:
 	def check(self, df, rules: Dict) -> ValidationReport:
     	rows = df.to_dict(orient="records")
     	raw = validate_dataset(rows, rules)
     	issues = [ValidationIssue(**d) for d in raw]
     	return ValidationReport(issues)

