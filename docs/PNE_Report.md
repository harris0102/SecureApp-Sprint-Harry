# Protection Needs Elicitation (PNE) & CIA Mapping Report

## 1. Asset Inventory
* **User Data:** User profiles, passwords hashes, session tokens.
* **Application Files:** Uploaded user documents, images, system scripts.
* **Component Code:** Python Flask source code, C/C++ native helper binaries.
* **Infrastructure:** Docker container runtime, SQLite database.

## 2. Stakeholder Perspectives & CIA Mapping
| Asset | Stakeholder | Protection Need | CIA Mapping | Measurable Security Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **User Passwords** | User / Admin | Prevent unauthorized read/exposure | Confidentiality | Passwords must be hashed using bcrypt/argon2; no plaintext storage. |
| **Uploaded Files** | Operator | Prevent unauthorized execution/modification | Integrity | Filenames and paths must be sanitized; strict allow-lists for extensions. |
| **Native Helper** | Developer | Prevent memory corruption/RCE | Integrity / Availability | Bounds checking on all inputs; stack cookies enabled (`-fstack-protector-strong`). |
| **System API** | End User | Ensure continuous availability | Availability | Rate limiting and resource exhaustion defenses on all endpoints. |
