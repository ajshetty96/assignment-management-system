import os
import csv
import random
import hashlib
from datetime import datetime, timedelta, timezone

# ------------------------------------------------------------------------------
# CONFIGURATION & REPRODUCIBILITY SEED
# ------------------------------------------------------------------------------
SEED = 20261022
random.seed(SEED)

OUTPUT_DIR = "./data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Parameterized Volume Baseline
NUM_COURSES = 50
NUM_LEARNERS = 10000
NUM_ASSIGNMENTS = 1000
NUM_SUBMISSIONS = 30000

# Edge Case Injection Counts
NUM_UNENROLLED_SUBMISSIONS = 50
NUM_OVERFLOW_GRADES = 50
NUM_DOUBLE_LATE_PENALTIES = 50
NUM_ORPHAN_APPEAL_GRADES = 50

START_DATE = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
print("Initializing synthetic data generation...")

# ------------------------------------------------------------------------------
# MASTER DATA GENERATION
# ------------------------------------------------------------------------------
courses = []
for i in range(1, NUM_COURSES + 1):
    courses.append({
        "course_id": f"CRS-{i:06d}",
        "course_code": f"CS-{100 + i}",
        "title": f"Computer Science Course {i}",
        "term": "2026-Spring",
        "created_at": START_DATE.isoformat()
    })

learners = []
for i in range(1, NUM_LEARNERS + 1):
    learners.append({
        "learner_id": f"LRN-{i:06d}",
        "first_name": f"First_{i}",
        "last_name": f"Last_{i}",
        "email": f"learner_{i}@university.edu",
        "enrolled_at": (START_DATE + timedelta(days=random.randint(0, 10))).isoformat()
    })

course_enrollments = []
enrollment_map = set()
enrollment_counter = 1

for c in courses:
    selected_learners = random.sample(learners, k=min(200, NUM_LEARNERS))
    for l in selected_learners:
        course_enrollments.append({
            "enrollment_id": f"ENR-{enrollment_counter:06d}",
            "course_id": c["course_id"],
            "learner_id": l["learner_id"],
            "status": "Active",
            "enrolled_at": START_DATE.isoformat()
        })
        enrollment_map.add((c["course_id"], l["learner_id"]))
        enrollment_counter += 1

assignments = []
rubrics = []
rubric_criteria = []

for i in range(1, NUM_ASSIGNMENTS + 1):
    asn_id = f"ASN-2026-{i:06d}"
    course_id = random.choice(courses)["course_id"]
    due_at = START_DATE + timedelta(days=random.randint(15, 90), hours=random.randint(0, 23))
    
    assignments.append({
        "assignment_id": asn_id,
        "course_id": course_id,
        "title": f"Assignment {i} for {course_id}",
        "status": "Published",
        "due_at": due_at.isoformat(),
        "resubmission_allowed": True,
        "max_attempts": 2,
        "created_at": START_DATE.isoformat()
    })

    rubric_id = f"RUB-{asn_id}-01"
    rubrics.append({
        "rubric_id": rubric_id,
        "assignment_id": asn_id,
        "title": f"Rubric for {asn_id}",
        "max_score": 100.00
    })

    for c_idx in range(1, 5):
        rubric_criteria.append({
            "criterion_id": f"CRT-{rubric_id}-{c_idx:02d}",
            "rubric_id": rubric_id,
            "description": f"Criterion {c_idx} evaluation",
            "max_points": 25.00,
            "weight": 0.25
        })

crit_dict = {}
for rc in rubric_criteria:
    crit_dict.setdefault(rc["rubric_id"], []).append(rc)

# ------------------------------------------------------------------------------
# TRANSACTION & EVENT DATA GENERATION
# ------------------------------------------------------------------------------
submissions = []
submission_artifacts = []
grades = []
feedbacks = []
appeals = []
ground_truth = []

artifact_counter = 1
fb_counter = 1
app_counter = 1
valid_enrollment_list = list(enrollment_map)
asn_dict = {a["assignment_id"]: a for a in assignments}

for _ in range(NUM_SUBMISSIONS):
    course_id, learner_id = random.choice(valid_enrollment_list)
    course_asns = [a for a in assignments if a["course_id"] == course_id]
    if not course_asns:
        continue
    asn = random.choice(course_asns)
    asn_id = asn["assignment_id"]
    due_dt = datetime.fromisoformat(asn["due_at"])

    is_late_flag = random.random() < 0.15
    if is_late_flag:
        submitted_dt = due_dt + timedelta(hours=random.randint(1, 72))
        sec_late = int((submitted_dt - due_dt).total_seconds())
    else:
        submitted_dt = due_dt - timedelta(hours=random.randint(1, 120))
        sec_late = 0

    sub_id = f"SUB-{asn_id}-{learner_id}-01"
    if any(s["submission_id"] == sub_id for s in submissions):
        continue

    submissions.append({
        "submission_id": sub_id,
        "assignment_id": asn_id,
        "learner_id": learner_id,
        "attempt_number": 1,
        "submitted_at": submitted_dt.isoformat(),
        "is_late": is_late_flag,
        "seconds_late": sec_late,
        "status": "Graded"
    })

    submission_artifacts.append({
        "artifact_id": f"ART-{artifact_counter:08d}",
        "submission_id": sub_id,
        "file_path": f"/uploads/{asn_id}/{learner_id}_v1.pdf",
        "file_size_bytes": random.randint(1024, 1048576),
        "checksum_sha256": hashlib.sha256(sub_id.encode()).hexdigest(),
        "uploaded_at": submitted_dt.isoformat()
    })
    artifact_counter += 1

    rub_id = f"RUB-{asn_id}-01"
    criteria = crit_dict[rub_id]
    raw_score = 0.0
    grd_id = f"GRD-{sub_id}"
    
    for cr in criteria:
        pts = round(random.uniform(18.0, 25.0), 2)
        raw_score += pts
        feedbacks.append({
            "feedback_id": f"FBK-{fb_counter:08d}",
            "grade_id": grd_id,
            "criterion_id": cr["criterion_id"],
            "score_assigned": pts,
            "comments": "Good work on this section.",
            "created_at": (submitted_dt + timedelta(days=2)).isoformat()
        })
        fb_counter += 1

    late_deduction = 10.00 if is_late_flag else 0.00
    final_score = max(0.00, round(raw_score - late_deduction, 2))

    grades.append({
        "grade_id": grd_id,
        "submission_id": sub_id,
        "evaluator_id": "INST-001",
        "raw_score": round(raw_score, 2),
        "late_penalty_deduction": late_deduction,
        "final_score": final_score,
        "is_current": True,
        "parent_grade_id": "",
        "graded_at": (submitted_dt + timedelta(days=2)).isoformat()
    })

# ------------------------------------------------------------------------------
# INJECT ANOMALIES & GROUND TRUTH LABELS
# ------------------------------------------------------------------------------
for i in range(NUM_UNENROLLED_SUBMISSIONS):
    asn = random.choice(assignments)
    enrolled_learners = {e["learner_id"] for e in course_enrollments if e["course_id"] == asn["course_id"]}
    available = [l for l in learners if l["learner_id"] not in enrolled_learners]
    if not available: continue
    l_rogue = random.choice(available)
    sub_id = f"SUB-{asn['assignment_id']}-{l_rogue['learner_id']}-01"
    
    submissions.append({
        "submission_id": sub_id, "assignment_id": asn["assignment_id"], "learner_id": l_rogue["learner_id"],
        "attempt_number": 1, "submitted_at": asn["due_at"], "is_late": False, "seconds_late": 0, "status": "Submitted"
    })
    ground_truth.append({"entity_type": "Submission", "entity_id": sub_id, "issue_type": "UNENROLLED_LEARNER_SUBMISSION", "description": "Learner submitted work without active enrollment."})

for i in range(NUM_OVERFLOW_GRADES):
    target_sub = random.choice(submissions)
    bad_grd_id = f"GRD-OVERFLOW-{i:04d}"
    grades.append({
        "grade_id": bad_grd_id, "submission_id": target_sub["submission_id"], "evaluator_id": "INST-999",
        "raw_score": 125.00, "late_penalty_deduction": 0.00, "final_score": 125.00, "is_current": False, "parent_grade_id": "", "graded_at": START_DATE.isoformat()
    })
    ground_truth.append({"entity_type": "Grade", "entity_id": bad_grd_id, "issue_type": "GRADE_EXCEEDS_RUBRIC_MAXIMUM", "description": "Final score exceeds 100.00 max."})

for i in range(NUM_DOUBLE_LATE_PENALTIES):
    target_sub = random.choice([s for s in submissions if s["is_late"]])
    bad_grd_id = f"GRD-DBLLATE-{i:04d}"
    grades.append({
        "grade_id": bad_grd_id, "submission_id": target_sub["submission_id"], "evaluator_id": "SYS_ERR",
        "raw_score": 90.00, "late_penalty_deduction": 20.00, "final_score": 70.00, "is_current": False, "parent_grade_id": "", "graded_at": START_DATE.isoformat()
    })
    ground_truth.append({"entity_type": "Grade", "entity_id": bad_grd_id, "issue_type": "DOUBLE_LATE_PENALTY_APPLIED", "description": "Late penalty applied twice."})

for i in range(NUM_ORPHAN_APPEAL_GRADES):
    target_sub = random.choice(submissions)
    app_id = f"APP-2026-{app_counter:06d}"; app_counter += 1
    appeals.append({
        "appeal_id": app_id, "submission_id": target_sub["submission_id"], "learner_id": target_sub["learner_id"],
        "reason": "Regrade request.", "status": "Approved", "submitted_at": START_DATE.isoformat(), "resolved_at": START_DATE.isoformat()
    })
    orphan_grd_id = f"GRD-ORPHAN-{i:04d}"
    grades.append({
        "grade_id": orphan_grd_id, "submission_id": target_sub["submission_id"], "evaluator_id": "ADMIN-01",
        "raw_score": 95.00, "late_penalty_deduction": 0.00, "final_score": 95.00, "is_current": True, "parent_grade_id": "", "graded_at": START_DATE.isoformat()
    })
    ground_truth.append({"entity_type": "Grade", "entity_id": orphan_grd_id, "issue_type": "APPEAL_GRADE_CHANGE_MISSING_AUDIT_LINEAGE", "description": "Grade updated via appeal without parent lineage."})

# ------------------------------------------------------------------------------
# EXPORT TO CSV
# ------------------------------------------------------------------------------
def export(filename, data, fields):
    with open(os.path.join(OUTPUT_DIR, filename), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

export("courses.csv", courses, ["course_id", "course_code", "title", "term", "created_at"])
export("learners.csv", learners, ["learner_id", "first_name", "last_name", "email", "enrolled_at"])
export("course_enrollments.csv", course_enrollments, ["enrollment_id", "course_id", "learner_id", "status", "enrolled_at"])
export("assignments.csv", assignments, ["assignment_id", "course_id", "title", "status", "due_at", "resubmission_allowed", "max_attempts", "created_at"])
export("rubrics.csv", rubrics, ["rubric_id", "assignment_id", "title", "max_score"])
export("rubric_criteria.csv", rubric_criteria, ["criterion_id", "rubric_id", "description", "max_points", "weight"])
export("submissions.csv", submissions, ["submission_id", "assignment_id", "learner_id", "attempt_number", "submitted_at", "is_late", "seconds_late", "status"])
export("submission_artifacts.csv", submission_artifacts, ["artifact_id", "submission_id", "file_path", "file_size_bytes", "checksum_sha256", "uploaded_at"])
export("grades.csv", grades, ["grade_id", "submission_id", "evaluator_id", "raw_score", "late_penalty_deduction", "final_score", "is_current", "parent_grade_id", "graded_at"])
export("feedbacks.csv", feedbacks, ["feedback_id", "grade_id", "criterion_id", "score_assigned", "comments", "created_at"])
export("appeals.csv", appeals, ["appeal_id", "submission_id", "learner_id", "reason", "status", "submitted_at", "resolved_at"])
export("ground_truth.csv", ground_truth, ["entity_type", "entity_id", "issue_type", "description"])

print("Successfully generated all dataset CSV files inside the './data' directory!")