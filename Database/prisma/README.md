# Prisma migrations and usage (Database/prisma)

This file explains how to apply the new Role enum migration and regenerate the Prisma client.

Prerequisites
- Ensure DATABASE_URL is set in your environment (example):
  - Windows (PowerShell): $env:DATABASE_URL = "postgresql://user:pass@host:5432/db"
  - macOS / Linux: export DATABASE_URL="postgresql://user:pass@host:5432/db"
- Install dependencies: npm install -D prisma @prisma/client

Apply migrations (production)

1. Pull latest code:

   git pull origin main

2. Deploy migrations:

   npx prisma migrate deploy --schema Database/prisma/schema.prisma

3. Generate client:

   npx prisma generate --schema Database/prisma/schema.prisma

Local development (interactive)

1. Pull latest code:

   git pull origin main

2. Run migrate dev (creates migration locally if needed):

   npx prisma migrate dev --name convert-role-to-enum --schema Database/prisma/schema.prisma

3. Generate client (usually automatic after migrate dev):

   npx prisma generate --schema Database/prisma/schema.prisma

Verification
- Check `users` table: role column values should be one of: 'admin', 'manager', 'employee'.
- The Prisma schema uses the Role enum; mapped values are lowercase in the DB.

Notes
- Migration is idempotent and will create the PostgreSQL enum type if missing, set NULL roles to 'employee', and convert the existing column.
- If you run into issues, share the error and the team can coordinate.
