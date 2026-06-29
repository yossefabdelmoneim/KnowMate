-- Create Role enum and convert existing User.role to enum
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role') THEN
    CREATE TYPE "Role" AS ENUM ('admin','manager','employee');
  END IF;
END$$;

-- Ensure no NULLs (set defaults for existing rows)
UPDATE "User" SET "role" = 'employee' WHERE "role" IS NULL;

-- Convert column type from text/varchar to enum
ALTER TABLE "User" ALTER COLUMN "role" TYPE "Role" USING ("role")::text::"Role";

-- Set default and not null
ALTER TABLE "User" ALTER COLUMN "role" SET DEFAULT 'employee';
ALTER TABLE "User" ALTER COLUMN "role" SET NOT NULL;
