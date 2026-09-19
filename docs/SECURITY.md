# Security Architecture & Controls

## 1. Role-Based Access Control (RBAC)
- Strict authorization barriers enforcing permissions across 4 tiers: `EMPLOYEE`, `TRAINER`, `ADMIN`, `SUPER_ADMIN`.
- Endpoints are protected by `OAuth2PasswordBearer` JWT tokens with expiration and signature verification.
- Sensitive administrative routes (heatmaps, audit logs, provider syncing, user management) are blocked for non-admin accounts (verified in automated security test `test_employee_cannot_access_admin_endpoints`).

## 2. Protection Against Prompt & Document Injection (Rule 8 & 35)
- Documents and user prompts are treated as **untrusted data**, never as system instructions.
- Strict structural separation is maintained in all AI prompts:
  - `SYSTEM INSTRUCTIONS`
  - `USER CONTENT`
  - `RETRIEVED DOCUMENT CONTENT`
- The AI question validation pipeline scans candidate questions for hostile tokens (`system prompt`, `ignore previous`, `jailbreak`, etc.) and rejects tainted inputs.

## 3. File Security & Upload Constraints (Rule 36)
- File uploads are validated against an explicit whitelist of allowed extensions (`pdf`, `docx`, `pptx`, `txt`).
- Filenames are sanitized using `os.path.basename` to prevent path traversal attacks.
- File size is constrained by `UPLOAD_MAX_MB` (default 25 MB).
- Unsupported or executable MIME types are rejected with HTTP 400 (verified in `test_unsupported_file_extension_rejected`).

## 4. Immutable Audit Logging (Section 37)
- System events (logins, logouts, profile edits, assessment submissions, score recalculations, document ingestions, question publications) are recorded in the `audit_logs` table.
- Passwords, secret keys, and raw tokens are stripped before logging.
