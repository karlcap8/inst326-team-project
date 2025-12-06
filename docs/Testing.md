
# 🧪 **TESTING.md — Research Survey Data Pipeline**

## **Testing Strategy & Coverage Documentation**

This document explains the full testing strategy used in our **Survey Data Cleaning & Validation Pipeline**, including unit tests, integration tests, and system tests. It describes what each test suite covers, why these tests were chosen, and how to run them.

Project 04 requires a complete set of automated tests that verify the correctness, robustness, and reliability of the full end-to-end system. Our testing approach ensures that every subsystem works independently (unit tests), works together (integration tests), and behaves correctly when executed as a full application (system tests).

---

# 🧩 **Overview of Test Types**

Our test suite is organized into three layers:

```
Unit Tests  →  Integration Tests  →  System Tests
```

Each layer builds confidence in increasingly large portions of the pipeline.

---

# 1️⃣ **Unit Tests**

**Files:**

* `test_survey_system.py`
* `test_io_and_state.py`

### ✔ Purpose

Unit tests verify that **individual components** of the system behave correctly in isolation.
These are the smallest and most focused tests.

---

## **1.1 Project 3 Unit Tests — `test_survey_system.py`**

These tests verify:

* `HeaderNormalizer` correctly normalizes column names
* `PIIRemover` removes sensitive fields
* `TypeCaster` correctly converts data types
* `Pipeline` properly applies steps in order
* `RulesValidator` produces correct `ValidationReport` objects

These tests ensure that our transformation logic is **stable and backward-compatible** with Project 3.

---

## **1.2 Project 4 Unit Tests — `test_io_and_state.py`**

These tests validate the new **I/O & persistence layer**:

### `load_raw_csv`

* Correctly loads valid CSVs
* Raises `FileNotFoundError` for missing files
* Raises `ValueError` for malformed/empty CSVs

### `save_cleaned_csv`

* Writes cleaned DataFrames to disk
* Output integrity is verified with a reload

### `save_validation_report`

* Exports human-readable Markdown reports

### `save_state` & `load_state`

* Verify JSON state round-tripping
* Handle malformed JSON
* Enforce required keys (`config` and `history`)

**Why included?**
These functions enable Project 4’s persistence and reproducibility requirements.

---

# 2️⃣ **Integration Tests**

**File:** `test_integration.py`

### ✔ Purpose

Integration tests ensure that **multiple subsystems work correctly together**.

This suite validates the full interaction of:

* Pipeline
* Transformers
* Type casting
* PII removal
* Rules validation
* Cleaned file saving
* Validation report saving

### What these tests cover:

| Component                   | Verified Behavior                                       |
| --------------------------- | ------------------------------------------------------- |
| **Pipeline + Transformers** | Steps applied in correct order, correct output columns  |
| **TypeCaster**              | String → int conversion validated                       |
| **PIIRemover**              | Sensitive fields removed                                |
| **RulesValidator**          | Output `ValidationReport` has zero issues on valid data |
| **I/O utilities**           | Cleaned CSV + report written successfully               |

**Why included?**
These tests prove that the major parts of the system can interoperate reliably even if each individual module works.

---

# 3️⃣ **System Tests**

**File:** `test_system_workflow.py`

### ✔ Purpose

System tests evaluate the **entire end-to-end application**, simulating real-world usage.

These tests call:

```
run_workflow()
```

—the same function used by `app.py`.

### What these tests verify:

### **1. Happy Path (with state)**

* Real CSV is created
* Pipeline runs
* Validation succeeds
* Cleaned data saved
* Report saved
* JSON state created and contains correct keys

### **2. Happy Path (no state mode)**

* Application runs without generating a state file
* Cleaned + report outputs still created

### **3. Missing Input File**

* Proper error handling
* Non-zero exit code
* No output directories created

**Why included?**
These tests demonstrate that the system fulfills Project 4’s requirement for a complete workflow from:

> *user input → pipeline → validation → output → persistence*

and handles errors gracefully.

---

# 🧪 **How to Run Tests**

From the project root:

### ✔ Run all tests

```bash
py -3 -m unittest
```

### ✔ Run a single test suite

```bash
py -3 -m unittest test_io_and_state.py
```

### ✔ Run with verbose output

```bash
py -3 -m unittest -v
```

---

# 📈 **Test Coverage Summary**

| Test Type         | Files                                           | Purpose                                         | Status           |
| ----------------- | ----------------------------------------------- | ----------------------------------------------- | ---------------- |
| Unit Tests        | `test_survey_system.py`, `test_io_and_state.py` | Validate individual components                  | ✔ All tests pass |
| Integration Tests | `test_integration.py`                           | Validate pipeline + validator + I/O interaction | ✔ All tests pass |
| System Tests      | `test_system_workflow.py`                       | Validate full end-to-end workflow               | ✔ All tests pass |

Combined, these tests provide confidence that:

* The system is correct
* Each part works in isolation
* All parts work together
* The entire workflow functions reliably

---

# 🏁 **Conclusion**

This testing suite satisfies all Project 4 requirements for automated testing:

* **Unit Tests** ensure correctness at the smallest level
* **Integration Tests** validate multi-component interactions
* **System Tests** confirm that the complete workflow behaves as expected

With all tests passing, the pipeline is verified as:

* Reliable
* Modular
* Extensible
* Ready for real survey data
* Fully aligned with INST326 Project 4 standards

---
