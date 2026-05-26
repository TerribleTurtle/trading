# Security & Privacy Procedures

This document outlines the strict operational security (OpSec) and privacy procedures for developing, deploying, and maintaining the Kalshi Shadow Trading Bot. As this system deals with market analysis and simulated financial logs (which may eventually transition to live funds), these procedures must be strictly enforced by developers and AI agents alike.

---

## 1. Secrets Management & Environment Isolation

### Rule: Zero Hardcoded Credentials
* **Never** hardcode private API keys, RSA key IDs, webhook URLs, or passwords anywhere in the codebase or tests.
* All configuration must be loaded at runtime from environment variables using `os.getenv` or a validated configuration wrapper.

### Local Development
* A `.env.example` file is provided in the repository root containing empty/placeholder variables.
* **Never** rename `.env.example` directly. Instead, copy it to a local `.env` file (`cp .env.example .env`).
* The local `.env` and any `.env.*` files are explicitly ignored by `.gitignore` and must **never** be committed.

### Cloud/Production Environment (Railway)
* Inject all production secrets strictly through Railway's **Variables** dashboard interface.
* The Kalshi RSA private key (`KALSHI_RSA_KEY_B64`) must be stored as a Base64-encoded string in the environment, never as a raw `.pem` file on disk.

---

## 2. Code & Dependency Safety

### Supply Chain Security
* **Lockfile Enforcement:** Always use `uv.lock` to pin exact dependency versions and hashes. Do not install unverified or unpinned packages.
* **Vulnerability Scanning:** Run security audits on dependencies regularly:
  ```bash
  uv run safety check
  ```

### Non-Root Execution (Container Security)
* The Docker container must **never** run as the root user.
* A dedicated non-privileged user (`appuser`) is configured in the `Dockerfile`. All filesystem operations (like writing to the persistent database) are restricted to `/data` owned by `appuser`.

---

## 3. Data & Privacy Safeguards

### Database Access
* The SQLite shadow trading database contains simulated bankroll state, trade logs, and performance metrics.
* **Never** expose the SQLite database file (`shadow_bot.db`) publicly or commit it to version control. It is explicitly ignored via `.gitignore`.
* In deployment (Railway), the database must reside in an isolated **Persistent Volume** (e.g., mounted at `/data`) to prevent data loss across container restarts while keeping it secured within the private container volume.

### Logging Restrictions
* Under no circumstances should logs contain sensitive credentials, API keys, private keys, or raw request headers containing authorization signatures.
* Market IDs, simulated trade decisions, P&L calculations, and generic system heartbeats are the only authorized log items.

---

## 4. Test-Driven Development (TDD) Isolation

* **Strict Mocking:** All unit tests must use mock interfaces (e.g., `unittest.mock`) to prevent external network or live database access.
* **Zero Live Connections in CI:** Tests executed by GitHub Actions or local runners must run 100% offline. Under no circumstances should a test suite trigger actual HTTP requests to Kalshi endpoints.

---

## 5. Incident Response & Credential Rotation

If any credentials (e.g., Kalshi Key ID, Private Key, Discord Webhook) are ever accidentally committed or leaked:
1. **Immediate Revocation:** Log in to the Kalshi dashboard and immediately revoke the compromised Key ID.
2. **Deactivate Webhooks:** Delete the compromised Discord Webhook URL from the channel settings.
3. **Purge Git History:** Use `git-filter-repo` or standard Git purge tools to scrub the secret from the entire history before force-pushing.
4. **Generate New Keys:** Generate a brand-new RSA key pair on Kalshi, update Railway's environment variables, and re-deploy.
