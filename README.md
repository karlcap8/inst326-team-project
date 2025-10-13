# INST326-Team-Project

# Research Data Pipeline - Function Library

**Team:** Harrang Khalsa, Karl Capili, Sukhman Singh, Aaron Coogan
**Domain:** Research Data Pipeline Management
**Course:** INST326 - Object-Oriented Programming for Information Science  

## Project Overview

This function library provides the foundational utilities for a research data pipeline designed to process and clean survey data collected through platforms such as Qualtrics. The library includes functions for data ingestion, de-identification, cleaning, validation, and documentation. These functions will form the groundwork for future object-oriented modules that automate the research data lifecycle — from raw input to structured, analysis-ready datasets.

## Problem Statement

Researchers frequently face challenges when working with raw survey data, such as:
  - Confusing column headers and inconsistent file structures from survey platforms
  - Presence of personally identifiable information (PII) requiring removal or anonymization
  - Mixed data types, missing values, and inconsistent formatting
  - Lack of validation for input ranges or categorical responses
  - Absence of standardized codebooks documenting dataset variables and structures

Our function library addresses these issues by creating a consistent, automated process to clean and prepare research data for analysis, ensuring data integrity, security, and reproducibility.

---

## Domain Focus and Problem Statement

Researchers often struggle to prepare raw survey exports for analysis due to:
- **Inconsistent column headers** and file formats  
- **Mixed data types** (e.g., numeric vs. string inconsistencies)  
- **Personally identifiable information (PII)** embedded in datasets  
- **Missing values** or invalid categorical responses  
- **Lack of structured documentation** describing dataset variables  

Our library addresses these challenges by automating data cleaning and validation while preserving data integrity and privacy. It ensures that research datasets meet ethical standards, maintain reproducibility, and are ready for statistical or machine learning analysis.

---

## Repository Structure
inst326-team-project/ 
├── README.md 
├── requirements.txt 
├── src/ 
│ ├── init.py 
│ ├── research_data_lib.py 
│ └── src_readme.txt 
├── docs/ 
│ ├── function_reference.md 
│ └── usage_examples.md 
└── examples/ 
└── demo_script.py 
