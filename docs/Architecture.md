
```markdown
# 🏗️ Research Data Cleaning & Validation Pipeline  
## **System Architecture Document**

This Architecture document explains the inheritance hierarchy, polymorphism decisions, design patterns, and composition structures used in our **Survey Data Cleaning & Validation Pipeline**.  
It is modeled after the “Garden Management System – Architecture Diagram” example provided by our instructor.  
As requested, the structure and explanations parallel that example.  
(Reference: :contentReference[oaicite:0]{index=0})

---

# 📐 Complete System Architecture

```

┌───────────────────────────────────────────────────────────────────────────┐
│                          ABSTRACT BASE LAYER                              │
│                       (Defines Interface Contracts)                       │
├───────────────────────────────────────────────────────────────────────────┤

```
 ┌───────────────────────────────────────────────────────────────┐
 │                        Transformer (ABC)                       │
 ├───────────────────────────────────────────────────────────────┤
 │ + name : str                                                   │
 │ + notes : str                                                  │
 │ + created_at : datetime                                        │
 │ + _history : list[str]                                         │
 │                                                               │
 │ @property                                                      │
 │ + required_columns : list[str]   (ABSTRACT)                    │
 │                                                               │
 │ @abstractmethod                                                │
 │ + _apply(df) → DataFrame                                       │
 │                                                               │
 │ + apply(df) → DataFrame  (TEMPLATE METHOD)                     │
 │ + _preflight(df)                                              │
 │ + _log(message)                                               │
 │ + history() → list[str]                                       │
 └───────────────────────────────────────────────────────────────┘
                             ▲
                             │ inherits
                             │
```

┌───────────────────────────────────────────────────────────────────────────┐
│                    CONCRETE IMPLEMENTATION LAYER                          │
│                 (Inheritance & Polymorphism for Cleaning)                 │
├───────────────────────────────────────────────────────────────────────────┤

```
┌─────────────────────────┐   ┌─────────────────────────┐   ┌──────────────────────────────┐
│    HeaderNormalizer     │   │       PIIRemover        │   │         TypeCaster           │
├─────────────────────────┤   ├─────────────────────────┤   ├──────────────────────────────┤
│ + required_columns = [] │   │ + columns : list[str]   │   │ + type_map : dict             │
│ + _apply(df)            │   │ + required_columns = [] │   │ + required_columns = []       │
│   → cleans headers      │   │ + _apply(df)            │   │ + _apply(df)                  │
└─────────────────────────┘   │   → drops PII columns   │   │   → converts column types     │
                              └─────────────────────────┘   └──────────────────────────────┘
```

└───────────────────────────────────────────────────────────────────────────┘
│
│ used by
▼

┌───────────────────────────────────────────────────────────────────────────┐
│                           COMPOSITION LAYER                               │
│                        (System-Level Coordination)                        │
├───────────────────────────────────────────────────────────────────────────┤

```
  ┌───────────────────────────────────────────────────────────────────┐
  │                             Pipeline                              │
  ├───────────────────────────────────────────────────────────────────┤
  │ + steps : list[Transformer]   ◄──────────── HAS-MANY steps        │
  │ + history : list[str]                                            │
  │                                                                   │
  │ + run(df)                                                        │
  │      → runs each Transformer polymorphically                     │
  │      → collects each step’s log history                          │
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
```

└───────────────────────────────────────────────────────────────────────────┘

````

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


If you'd like, I can also produce a **PDF-ready version**, a **diagram image**, or even a **Mermaid diagram** specifically for the Architecture file.

