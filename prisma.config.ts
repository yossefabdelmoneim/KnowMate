import "dotenv/config";
import { defineConfig } from "prisma/config";

export default defineConfig({
  schema: "Database/prisma/schema.prisma",
  migrations: {
    path: "Database/prisma/migrations",
  },
  datasource: {
    url: process.env["DATABASE_URL"],
  },
});