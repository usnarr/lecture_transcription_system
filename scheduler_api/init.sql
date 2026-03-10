-- Create enum types (only if they don't exist)
DO $$ BEGIN
    CREATE TYPE lecture_type_enum AS ENUM ('math', 'programming', 'tech_theory', 'soft_skill');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_status_enum AS ENUM ('pending', 'success', 'fail');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create task_statuses table
CREATE TABLE IF NOT EXISTS task_statuses (
    id SERIAL PRIMARY KEY,
    status task_status_enum NOT NULL UNIQUE
);

-- Create transcriptions table
CREATE TABLE IF NOT EXISTS transcriptions (
    id SERIAL PRIMARY KEY,
    transcription_text TEXT NOT NULL
);

-- Create summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id SERIAL PRIMARY KEY,
    summary_text TEXT NOT NULL,
    last_processing_timestamp TIMESTAMP
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_status_id INTEGER NOT NULL REFERENCES task_statuses(id),
    transcription_id INTEGER REFERENCES transcriptions(id),
    summary_id INTEGER REFERENCES summaries(id),
    celery_task_id VARCHAR NOT NULL,
    last_processing_timestamp TIMESTAMP
);

-- Create lectures table
CREATE TABLE IF NOT EXISTS lectures (
    lecture_id SERIAL PRIMARY KEY,
    lecture_recording_path VARCHAR NOT NULL,
    lecture_type lecture_type_enum NOT NULL,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    task_id INTEGER REFERENCES tasks(id)
);

-- Create prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    type VARCHAR NOT NULL,
    prompt_text TEXT NOT NULL
);

-- Insert default task statuses (only if they don't exist)
INSERT INTO task_statuses (status) 
VALUES 
    ('pending'),
    ('success'),
    ('fail')
ON CONFLICT (status) DO NOTHING;

-- Create indexes for better performance (only if they don't exist)
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(task_status_id);
CREATE INDEX IF NOT EXISTS idx_tasks_celery_id ON tasks(celery_task_id);
CREATE INDEX IF NOT EXISTS idx_lectures_processed ON lectures(is_processed);
CREATE INDEX IF NOT EXISTS idx_lectures_task_id ON lectures(task_id);