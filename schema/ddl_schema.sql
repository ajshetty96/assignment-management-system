-- DDL Schema for Assignment Management System (AMS)

CREATE TABLE course (
    course_id VARCHAR(32) PRIMARY KEY,
    course_code VARCHAR(16) NOT NULL UNIQUE,
    title VARCHAR(128) NOT NULL,
    term VARCHAR(16) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE learner (
    learner_id VARCHAR(32) PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    enrolled_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE course_enrollment (
    enrollment_id VARCHAR(32) PRIMARY KEY,
    course_id VARCHAR(32) NOT NULL REFERENCES course(course_id),
    learner_id VARCHAR(32) NOT NULL REFERENCES learner(learner_id),
    status VARCHAR(16) CHECK (status IN ('Active', 'Dropped', 'Completed')),
    enrolled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (course_id, learner_id)
);

CREATE TABLE assignment (
    assignment_id VARCHAR(32) PRIMARY KEY,
    course_id VARCHAR(32) NOT NULL REFERENCES course(course_id),
    title VARCHAR(128) NOT NULL,
    status VARCHAR(16) CHECK (status IN ('Draft', 'Published', 'Archived')),
    due_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resubmission_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    max_attempts INT NOT NULL DEFAULT 2,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE rubric (
    rubric_id VARCHAR(32) PRIMARY KEY,
    assignment_id VARCHAR(32) NOT NULL UNIQUE REFERENCES assignment(assignment_id),
    title VARCHAR(128) NOT NULL,
    max_score NUMERIC(5, 2) NOT NULL CHECK (max_score > 0)
);

CREATE TABLE rubric_criterion (
    criterion_id VARCHAR(32) PRIMARY KEY,
    rubric_id VARCHAR(32) NOT NULL REFERENCES rubric(rubric_id),
    description VARCHAR(256) NOT NULL,
    max_points NUMERIC(5, 2) NOT NULL CHECK (max_points > 0),
    weight NUMERIC(3, 2) NOT NULL CHECK (weight > 0 AND weight <= 1.0)
);

CREATE TABLE submission (
    submission_id VARCHAR(32) PRIMARY KEY,
    assignment_id VARCHAR(32) NOT NULL REFERENCES assignment(assignment_id),
    learner_id VARCHAR(32) NOT NULL REFERENCES learner(learner_id),
    attempt_number INT NOT NULL DEFAULT 1,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_late BOOLEAN NOT NULL,
    seconds_late BIGINT NOT NULL DEFAULT 0,
    status VARCHAR(16) CHECK (status IN ('Submitted', 'Graded', 'Appealed', 'Superseded')),
    UNIQUE (assignment_id, learner_id, attempt_number)
);

CREATE TABLE submission_artifact (
    artifact_id VARCHAR(32) PRIMARY KEY,
    submission_id VARCHAR(32) NOT NULL REFERENCES submission(submission_id),
    file_path VARCHAR(256) NOT NULL,
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes >= 0),
    checksum_sha256 VARCHAR(64) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE grade (
    grade_id VARCHAR(32) PRIMARY KEY,
    submission_id VARCHAR(32) NOT NULL REFERENCES submission(submission_id),
    evaluator_id VARCHAR(32) NOT NULL,
    raw_score NUMERIC(5, 2) NOT NULL CHECK (raw_score >= 0),
    late_penalty_deduction NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    final_score NUMERIC(5, 2) NOT NULL CHECK (final_score >= 0),
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    parent_grade_id VARCHAR(32) REFERENCES grade(grade_id),
    graded_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE feedback (
    feedback_id VARCHAR(32) PRIMARY KEY,
    grade_id VARCHAR(32) NOT NULL REFERENCES grade(grade_id),
    criterion_id VARCHAR(32) NOT NULL REFERENCES rubric_criterion(criterion_id),
    score_assigned NUMERIC(5, 2) NOT NULL CHECK (score_assigned >= 0),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE appeal (
    appeal_id VARCHAR(32) PRIMARY KEY,
    submission_id VARCHAR(32) NOT NULL REFERENCES submission(submission_id),
    learner_id VARCHAR(32) NOT NULL REFERENCES learner(learner_id),
    reason TEXT NOT NULL,
    status VARCHAR(16) CHECK (status IN ('Pending', 'Approved', 'Rejected', 'Escalated')),
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE
);
