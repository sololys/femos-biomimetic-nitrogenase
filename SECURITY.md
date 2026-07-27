# Security & Supply Chain Policy: Reismannpoint Observatorium

## 1. Security Philosophy & Fail-Closed Guarantee
Reismannpoint Observatorium operates under Level 0 Locus Zero fail-closed security guarantees:
- **Axiom 0:** "Kognisjon er fail-open. Konsekvens er fail-closed."
- **3-Tier Verification Requirement:** All 43 metamorphosis engines are validated against `SOFTWARE_PASS`, `MODEL_PASS`, and `EVIDENCE_PASS`. Unverified or unapproved code states result in immediate execution interlock (`KILL` / `HOLD`).

## 2. CodeQL & Static Analysis
Static code analysis is performed via GitHub CodeQL (`security-extended` & `security-and-quality` suites) on every push and pull request. CodeQL ensures:
- No hardcoded credentials or API keys.
- Safe process execution and input sanitization.
- Cryptographic hash integrity across WORM ledgers.

## 3. Secret Scanning & Supply Chain Protection
- **Secret Scanning:** All commits are scanned for API keys, private keys, and authorization tokens.
- **Dependency Auditing:** Dependencies (`numpy`, `scipy`) are locked and scanned for supply-chain vulnerabilities via automated security updates.

## 4. Reporting a Vulnerability
If you discover a potential security flaw or cryptographic weakness:
1. Do **NOT** open a public issue.
2. Submit a private security advisory via GitHub Security Advisories or contact maintainers directly.
3. Include detailed steps to reproduce, sample payloads, and proposed patch guidance.
