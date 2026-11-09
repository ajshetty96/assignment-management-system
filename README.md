# Assignment Management System (AMS)

An end-to-end relational data pipeline and workflow solution managing assignment publication, submissions, rubric-based grading, resubmissions, and grade appeals with deterministic synthetic data generation and anomaly isolation.

## Project Structure
assignment-management-system/
    ├── schema/
    │   └── ddl_schema.sql         # Database DDL schema & constraints
    ├── src/
    │   ├── generate_data.py       # Parameterized synthetic data generator script
    │   └── validate_data.py       # Automated data integrity & validation script
    ├── docs/
    │   └── data_dictionary.md     # Field specifications, types, and validation rules
    └── data/                      # Generated CSV files (created on execution)

---

## Instructions for Running the Project

Follow these steps to clone the repository, generate the synthetic dataset, and run the validation checks locally on your machine.

### Prerequisites
* **Python 3.x** installed on your system.
* **Pandas** library (required for data validation).

### Step 1: Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone [https://github.com/ajshetty96/assignment-management-system.git](https://github.com/ajshetty96/assignment-management-system.git)
cd assignment-management-system
