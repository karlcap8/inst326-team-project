
# 🏗️ Research Data Cleaning & Validation Pipeline  
## **System Architecture Document**

This Architecture document explains the inheritance hierarchy, polymorphism decisions, design patterns, and composition structures used in our **Survey Data Cleaning & Validation Pipeline**.  


---
# 🧱 Architecture Overview
raw CSV
   ↓
load_raw_csv()
   ↓
Pipeline
   ├── HeaderNormalizer
   ├── PIIRemover
   └── TypeCaster
   ↓
cleaned DataFrame
   ↓
RulesValidator
   ↓
ValidationReport
   ↓
save_cleaned_csv() + save_validation_report()
   ↓
(optional) save_state()


The architecture cleanly separates:

Transformation logic (pure functions or small classes)

Pipeline orchestration (Pipeline)

Validation rules

I/O + persistence

Application runner

# 📐 Complete System Architecture
```
┌───────────────────────────────────────────────────────────────────────────┐
│                          ABSTRACT BASE LAYER                              │
│                       (Defines Interface Contracts)                       │
├───────────────────────────────────────────────────────────────────────────┤

 ┌───────────────────────────────────────────────────────────────┐
 │                        Transformer (ABC)                      │
 ├───────────────────────────────────────────────────────────────┤
 │ + name : str                                                  │
 │ + notes : str                                                 │
 │ + created_at : datetime                                       │
 │ + _history : list[str]                                        │
 │                                                               │
 │ @property                                                     │
 │ + required_columns : list[str]   (ABSTRACT)                   │
 │                                                               │
 │ @abstractmethod                                               │
 │ + _apply(df) → DataFrame                                      │
 │                                                               │
 │ + apply(df) → DataFrame  (TEMPLATE METHOD)                    │
 │ + _preflight(df)                                              │
 │ + _log(message)                                               │
 │ + history() → list[str]                                       │
 └───────────────────────────────────────────────────────────────┘
└───────────────────────────────────────────────────────────────────────────┘
                             ▲
                             │ inherits
                             │

┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CONCRETE IMPLEMENTATION LAYER                          │
│                              (Inheritance & Polymorphism for Cleaning)                 │
├────────────────────────────────────────────────────────────────────────────────────────┤

┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────────┐
│    HeaderNormalizer     │   │       PIIRemover        │   │         TypeCaster          │
├─────────────────────────┤   ├─────────────────────────┤   ├─────────────────────────────┤
│ + required_columns = [] │   │ + columns : list[str]   │   │ + type_map : dict           │
│ + _apply(df)            │   │ + required_columns = [] │   │ + required_columns = []     │
│   → cleans headers      │   │ + _apply(df)            │   │ + _apply(df)                │
└─────────────────────────┘   │   → drops PII columns   │   │   → converts column types   │
                              └─────────────────────────┘   └─────────────────────────────┘


└────────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ used by
                                      ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                           COMPOSITION LAYER                               │
│                        (System-Level Coordination)                        │
├───────────────────────────────────────────────────────────────────────────┤


  ┌───────────────────────────────────────────────────────────────────┐
  │                             Pipeline                              │
  ├───────────────────────────────────────────────────────────────────┤
  │ + steps : list[Transformer]   ◄──────────── HAS-MANY steps        │
  │ + history : list[str]                                             │
  │                                                                   │
  │ + run(df)                                                         │
  │      → runs each Transformer polymorphically                      │
  │      → collects each step’s log history                           │
  └───────────────────────────────────────────────────────────────────┘

                             │
                             ▼

  ┌───────────────────────────────────────────────────────────────────┐
  │                        Validation Subsystem                       │
  ├───────────────────────────────────────────────────────────────────┤
  │ RulesValidator                                                    │
  │   + check(df, rules) → ValidationReport                           │
  │                                                                   │
  │ ValidationReport                                                  │
  │   + issues : list[ValidationIssue]                                │
  │   + is_valid : bool                                               │
  │   + to_markdown()                                                 │
  │                                                                   │
  │ ValidationIssue                                                   │
  │   + column : str                                                  │
  │   + message : str                                                 │
  └───────────────────────────────────────────────────────────────────┘


└───────────────────────────────────────────────────────────────────────────┘

```

---

# 🔍 Key Architectural Relationships

## **1. Inheritance (is-a)**

- `HeaderNormalizer` **is a** `Transformer`
- `PIIRemover` **is a** `Transformer`
- `TypeCaster` **is a** `Transformer`

**Why this design?**

All cleaning steps:
- Follow a common interface  
- Require consistent preflight checks  
- Need shared logging and history  
- Must be swappable in any order  

Putting shared logic in the ABC enables each subclass to focus solely on specific cleaning logic.

---

## **2. Composition (has-a)**

- `Pipeline` **has many** `Transformer` objects  
- `RulesValidator` **produces** a `ValidationReport`  
- `ValidationReport` **has many** `ValidationIssue` objects  

**Why composition instead of inheritance?**

A Pipeline is not a Transformer — it *uses* Transformers.  
This preserves conceptual clarity and allows:

- Reordering steps  
- Adding new Transformers without modifying Pipeline  
- Clean separation of responsibilities  

---

## **3. Polymorphism (same interface, different behavior)**

Pipeline does:

```python
for step in self.steps:
    df = step.apply(df)
````

But `apply()` produces different effects:

* `HeaderNormalizer` renames columns
* `PIIRemover` drops sensitive columns
* `TypeCaster` enforces correct data types

This allows:

* Extensibility (plug in new Transformers easily)
* Reversible ordering
* Cleaner, simpler Pipeline logic

### Why is this important?

Researchers often want different cleaning orders:
e.g.,

* Normalize headers → drop PII → cast types
  vs.
* Drop PII → normalize → cast types

Polymorphism enables this flexibility without changing Pipeline code.

---

# 🧩 Design Pattern Usage

## **1. Template Method Pattern (Primary Pattern Used)**

`Transformer.apply()` acts as a **template**:

1. Run `_preflight()`
2. Call subclass `_apply()`
3. Log results
4. Return cleaned data

Subclasses override only `_apply()`, not the entire flow.

---

## **2. Strategy Pattern**

Each Transformer subclass represents a **strategy** for cleaning data.

Pipeline selects which strategy to apply at runtime.

This enables:

* Swappable behaviors
* Cleaner design
* Extensibility

---

## **3. Composition Pattern**

`Pipeline` coordinates independent strategy objects rather than inheriting them.

---

## **4. Separation of Concerns**

* Cleaning logic in Transformers
* Orchestration in Pipeline
* Validation in RulesValidator
* Reporting in ValidationReport

Clear modular responsibilities.

---

# 🔄 Data Flow Example

```
1. User passes raw DataFrame to Pipeline.run(df)

2. Pipeline iterates over Transformers:
      step.apply(df)

3. Each transformer:
      - validates required columns
      - runs its subclass cleaning logic
      - logs result

4. Cleaned DataFrame returned

5. RulesValidator checks cleaned data:
      → ValidationReport

6. ValidationReport summarizes structural or logical issues
```

---

# 💾 I/O & Persistence Architecture

Our system includes a dedicated I/O layer (`io_utils.py`) responsible for file handling, serialization, and error safety. This layer is required for Project 4’s persistence feature set.

## File Loading
### `load_raw_csv(path)`
- Uses `pandas.read_csv` with exception handling  
- Ensures unreadable or missing files trigger descriptive errors  
- Returns a clean DataFrame for the pipeline

## Output Writing
### `save_cleaned_csv(df, output_path)`
- Writes the cleaned DataFrame to disk
- Automatically creates directories if they don’t exist
- Ensures atomic writes to avoid partial corruption

### `save_validation_report(report, output_path)`
- Accepts either text or Markdown output
- Writes human-readable validation issues
- Ensures export consistency across runs

## State Persistence
### `save_state(state_dict, state_path)`
- Saves a JSON representation of:
  - config
  - pipeline history
  - timestamped runs
- Allows the application to be resumed or repeated deterministically

### `load_state(state_path)`
- Safely loads JSON state
- Handles:
  - missing files  
  - malformed JSON  
  - unexpected schema
- Supports the “optional state mode” in `app.py`

**Why separate I/O from business logic?**
- Prevents pipeline classes from doing file operations  
- Keeps the system modular and testable  
- Allows unit tests to mock or isolate file I/O  

# 🚀 Application Runner (`app.py`)

The `app.py` module is the high-level interface that ties together all major subsystems (Pipeline, Validators, and I/O).

## Responsibilities

### 1. Argument Parsing
The CLI supports:
- Input CSV path
- Output directory path
- Optional `--state-file`
- Optional `--no-state` mode

This provides an end-user interface suitable for real-world researchers.

### 2. Workflow Orchestration
`run_workflow(input_csv, output_dir, state_path=None)`:
1. Loads raw CSV  
2. Constructs Pipeline with default Transformers  
3. Runs the pipeline  
4. Validates cleaned data  
5. Saves cleaned CSV  
6. Saves validation report  
7. Saves state (unless suppressed)

### 3. Error Handling
- Missing input file → non-zero exit code  
- Pipeline errors → logged and surfaced cleanly  
- Invalid types / malformed CSV → validation report still generated  

### 4. Integration Layer
`app.py` is the only module that:
- Talks to both I/O utilities and Transformers  
- Bundles multiple subsystems into a coherent user workflow  
- Ensures Project 4’s “complete end-to-end system” requirement is met

This separates “core system logic” from “execution logic,” improving maintainability.

# 🧠 Design Decisions Summary

Below is a concise summary of key design decisions made in the architecture:

### 1. Use of Abstract Base Transformer
Provides a consistent interface and enforces preflight checks. Ensures subclasses focus only on their specific transformation logic.

### 2. Pipeline as a Composition Container
Pipeline uses (has-a) transformers instead of inheriting from them. This keeps responsibilities clean, allows reordering steps, and supports extensibility.

### 3. Template Method Pattern
`apply()` defines shared transformation flow. `_apply()` is overridden per transformer. Ensures consistent behavior while supporting customization.

### 4. Strategy Pattern for Transformers
Each transformer is a strategy for cleaning. This allows swapping, extending, and reordering cleaning behaviors without modifying pipeline code.

### 5. Separation of Concerns
Cleaning, validation, I/O, and orchestration reside in separate modules. Improves maintainability and testing.

### 6. Dedicated I/O Layer
File loading, saving, and state persistence are isolated in `io_utils.py` to avoid coupling business logic with file operations.

### 7. Application Runner Design
`app.py` coordinates the entire workflow and exposes a CLI interface. This follows best practices for real-world data processing tools.

### 8. JSON State Persistence
State is saved in JSON so runs are repeatable and to meet Project 4 persistence requirements.
