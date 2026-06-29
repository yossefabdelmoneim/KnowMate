-- Add role column to User
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "role" VARCHAR(50) NOT NULL DEFAULT 'employee';
