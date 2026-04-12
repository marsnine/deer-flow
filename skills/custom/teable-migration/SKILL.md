---
name: teable-migration
description: Use this skill when the user requests to migrate a database from Airtable to a self-hosted Teable instance. It handles schema generation, base creation, records migration (via official tools or API), and complex multi-step dependency resolution for Relational Links, Lookups, Rollups, and Formulas.
---

# Teable Migration Skill

## Overview

The `teable-migration` skill provides a systematic workflow for migrating a complete database from Airtable to a self-hosted Teable instance. Because Teable has strict relational and typing constraints (especially around Lookups, Rollups, and Formulas), this skill breaks the migration down into three sequential phases to ensure all dependencies are satisfied in the correct order.

## Prerequisites

Before starting the migration, you MUST clarify and collect the following credentials from the user:
- **Airtable Base ID** (e.g., `appXXXXXXXXX`)
- **Airtable Personal Access Token (PAT)**
- **Teable Server URL** (e.g., `https://teable.example.com`)
- **Teable Base ID** (The target base where data will go)
- **Teable API Key**

## Migration Workflow

You must execute the migration in these exact steps. Do not run the next step until the current one is completed successfully.

### Step 1: Base Migration (Schema, Links, and Records)
Run `scripts/step1_migrate_base.py`. 
- **What it does**: Executes a 3-phase migration:
  - **Phase A**: Creates all Teable tables with non-link fields (text, number, select, etc.) and inserts records. Builds a global Airtable-to-Teable record ID mapping via positional matching from the insert API response.
  - **Phase B**: Creates `link` type fields with `foreignTableId` pointing to the correct Teable target table. Handles reciprocal (inverse) link deduplication so Teable's auto-created symmetric fields are not duplicated.
  - **Phase C**: Populates link field data by converting Airtable record ID arrays to Teable record IDs using the mapping from Phase A, then PATCHing link values into each record.
- **Skipped field types**: `formula`, `rollup`, and `multipleLookupValues` fields are intentionally skipped (not created as placeholder text fields). They are handled by Step 2 and Step 3.
- **Mapping file**: Saves `scripts/migration_mapping.json` with Airtable→Teable table/record ID mappings and attachment field info. This is consumed by Step 4.
- **Important**: You may need to edit `scripts/step1_migrate_base.py` to inject the user's provided credentials before running it.

### Step 2: Lookups and Rollups
Run `scripts/step2_migrate_lookups.py`.
- **What it does**: Reconstructs Lookup and Rollup fields. In Teable, a Lookup must strictly match the data type of the target field it is referencing. This script applies fuzzy matching and fallback mapping to bypass missing dependencies.
- **Important**: Edit credentials in the script before running.

### Step 3: Formulas and Final Dependencies
Run `scripts/step3_migrate_formulas.py`.
- **What it does**: Parses the Airtable formula AST syntax (`{fld...}`) and converts it to Teable syntax. Handles unsupported functions (like `REGEX_MATCH` or `IRR`) by inserting string placeholders so the schema does not break.
- **Important**: Edit credentials in the script before running.

### Step 4: Attachments (per-table)
Run `scripts/step4_migrate_attachments.py` **one table at a time**.
- **What it does**: Uploads Airtable attachment files to Teable via `fileUrl`. Fetches fresh Airtable records at execution time so URLs are not expired (Airtable URLs expire after 2 hours).
- **Usage**:
  - `python step4_migrate_attachments.py` — Lists all tables with attachment fields
  - `python step4_migrate_attachments.py "테이블이름"` — Migrate one table
  - `python step4_migrate_attachments.py --all` — Migrate all tables sequentially
- **Why per-table**: Each table's migration fits within the sandbox bash timeout (10 min). Running one table at a time also keeps Airtable URLs fresh.
- **Prerequisite**: `scripts/migration_mapping.json` must exist (created by Step 1).
- **Important**: Edit credentials in the script before running.

## Best Practices
1. **Always Verify Credentials**: Do not hardcode the demo credentials. Always ask the user for their specific environment variables.
2. **Handle Errors Gracefully**: Teable will return HTTP 400/500 if a formula dependency is missing. Fall back to creating a `singleLineText` field or a placeholder string if a calculation fails.
3. **Data Verification**: Recommend the user manually verify records after completion, as API delays can occasionally skip records during heavy uploads.

## Included Scripts
- `step1_migrate_base.py`
- `step2_migrate_lookups.py`
- `step3_migrate_formulas.py`
- `step4_migrate_attachments.py`
