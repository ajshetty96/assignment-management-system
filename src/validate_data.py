import os
import pandas as pd

DATA_DIR = "./data"

def run_validation():
    print("=== STARTING DATA INTEGRITY VALIDATION ===")
    
    # Load Tables
    courses = pd.read_csv(f"{DATA_DIR}/courses.csv")
    learners = pd.read_csv(f"{DATA_DIR}/learners.csv")
    enrollments = pd.read_csv(f"{DATA_DIR}/course_enrollments.csv")
    assignments = pd.read_csv(f"{DATA_DIR}/assignments.csv")
    rubrics = pd.read_csv(f"{DATA_DIR}/rubrics.csv")
    criteria = pd.read_csv(f"{DATA_DIR}/rubric_criteria.csv")
    submissions = pd.read_csv(f"{DATA_DIR}/submissions.csv")
    grades = pd.read_csv(f"{DATA_DIR}/grades.csv")
    ground_truth = pd.read_csv(f"{DATA_DIR}/ground_truth.csv")

    # 1. Primary Key Uniqueness Verification
    pk_checks = {
        "courses": (courses, "course_id"),
        "learners": (learners, "learner_id"),
        "assignments": (assignments, "assignment_id"),
        "submissions": (submissions, "submission_id"),
        "grades": (grades, "grade_id")
    }
    for name, (df, pk) in pk_checks.items():
        assert df[pk].is_unique, f"VALIDATION ERROR: Primary Key collision detected in {name}.{pk}"
    print("[PASS] Primary Key Uniqueness Checks Passed.")

    # 2. Foreign Key & Anomaly Isolation Check
    valid_enrollment_pairs = set(zip(enrollments["course_id"], enrollments["learner_id"]))
    submission_pairs = list(zip(submissions["assignment_id"], submissions["learner_id"]))
    asn_course_map = dict(zip(assignments["assignment_id"], assignments["course_id"]))
    
    unenrolled_count = 0
    for asn_id, l_id in submission_pairs:
        c_id = asn_course_map[asn_id]
        if (c_id, l_id) not in valid_enrollment_pairs:
            unenrolled_count += 1

    gt_unenrolled = ground_truth[ground_truth["issue_type"] == "UNENROLLED_LEARNER_SUBMISSION"]
    assert unenrolled_count == len(gt_unenrolled), f"FK Mismatch: Found {unenrolled_count} unenrolled submissions, expected {len(gt_unenrolled)}"
    print(f"[PASS] FK Integrity Check: Isolated exactly {unenrolled_count} unenrolled submission anomalies.")

    # 3. Arithmetic Reconciliation Check
    overflow_grades = grades[grades["final_score"] > 100.00]
    gt_overflows = ground_truth[ground_truth["issue_type"] == "GRADE_EXCEEDS_RUBRIC_MAXIMUM"]
    assert len(overflow_grades) == len(gt_overflows), "Arithmetic Mismatch: Score overflow count does not match ground truth."
    print(f"[PASS] Score Bounds Check: Isolated {len(overflow_grades)} overflow grade records.")

    print("[PASS] Synthetic Validation Pipeline Completed Successfully.")

if __name__ == "__main__":
    run_validation()