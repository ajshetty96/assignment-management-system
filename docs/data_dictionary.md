# Data Dictionary: Assignment Management System (AMS)

| Entity | Field Name | Data Type | Requirement | Constraints / Allowed Values | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Course** | `course_id` | VARCHAR(32) | Required | Primary Key (`CRS-XXXXXX`) | Unique identifier for academic course. |
| **Learner** | `learner_id` | VARCHAR(32) | Required | Primary Key (`LRN-XXXXXX`) | Student identifier. |
| **Assignment** | `assignment_id` | VARCHAR(32) | Required | Primary Key (`ASN-YYYY-XXXXXX`) | Published coursework item. |
| **Rubric** | `rubric_id` | VARCHAR(32) | Required | Primary Key (`RUB-<assignment_id>-01`) | Evaluation rubric tied to assignment. |
| **Submission** | `submission_id` | VARCHAR(32) | Required | Primary Key (`SUB-<assignment_id>-<learner_id>-01`) | Student submission record. |
| **Grade** | `grade_id` | VARCHAR(32) | Required | Primary Key (`GRD-<submission_id>`) | Evaluated score and penalties. |
| **Appeal** | `appeal_id` | VARCHAR(32) | Required | Primary Key (`APP-YYYY-XXXXXX`) | Grade review appeal request. |
