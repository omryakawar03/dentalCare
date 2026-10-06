# Digital Nagar Palika - Deployment Guide (Hinglish)

Yeh guide current repository scaffold ko local setup aur controlled staging tak le jaati hai. **Abhi is scaffold ko live citizen production par deploy na karein:** OTP/authentication, citizen/complaint APIs, real notification/payment/GIS/AI providers, full administrative workflows, production secrets, and municipality policy approvals abhi configure/implement hone baaki hain. Deployment ka matlab sirf container chalna nahi; production se pehle neeche ke gates complete hone chahiye.

## 0. Deployment ka scope samjhein

Current deliverables: FastAPI service shell, PostgreSQL/PostGIS schema migration, Redis dependency, health endpoints, tenant/ward authorization helper, web/mobile UI shells, CI security checks, and architecture/runbook documents. `/api/v1/health/live`, `/api/v1/health/ready`, aur `/api/v1/public/config` available hain. Citizen login, grievance submit/update, admin analytics data aur external integrations abhi functional endpoints nahi hain.

## 1. Prerequisites

**Kya chahiye:** Windows PowerShell ya Linux/macOS shell, Docker Desktop/Engine, Python 3.12+, Node.js 22+, pnpm, Git, aur (staging/production ke liye) municipality-approved cloud account.

**Kyun:** API, PostGIS database, Redis, Next.js web aur Expo mobile alag runtime use karte hain.

**Files:** `README.md`, `.env.example`, `docker-compose.yml`, `apps/api/pyproject.toml`, `apps/web/package.json`, `apps/mobile/package.json`.

**Check commands (PowerShell):**

```powershell
docker --version
python --version
node --version
corepack pnpm --version
git --version
```

**Security:** Sirf official/vendor approved installers use karein; shared server par personal admin account use na karein. **Verify:** versions output aaye aur Docker daemon running ho.

## 2. Code checkout aur environment file

Project root mein aayein (`digital-nagar-palika`):

```powershell
Set-Location "C:\path\to\digital-nagar-palika"
Copy-Item .env.example .env
notepad .env
```

`.env` mein `JWT_SIGNING_KEY` ko unique random 32+ byte value se replace karein; `DATABASE_URL` aur `REDIS_URL` ko selected environment ke mutabik rakhein. Production secret ko password manager/secret manager se set karein; `.env` Git mein commit nahi karna.

**Kyun:** har deployment ka host, database aur credential alag hai. **Files:** `.env.example`, `.gitignore`. **Security:** asli OTP, payment, AI ya cloud keys local file mein share nahi; production mein managed secret store. **Verify:** `git status --short` mein `.env` listed na ho.

## 3. PostgreSQL/PostGIS aur Redis start karein

```powershell
docker compose up -d db redis
docker compose ps
docker compose logs --tail 50 db redis
```

Compose PostGIS-enabled PostgreSQL 16 aur Redis 7 local development ke liye start karta hai. API host machine se `localhost` par connect karegi.

**Files:** `docker-compose.yml`. **Security:** yeh local-only credentials hain; local ports public network par expose na karein. Production mein managed private DB/cache use karein. **Verify:** containers healthy hon; PostgreSQL log mein ready aur Redis health check pass ho.

## 4. API virtual environment aur dependencies

Naye PowerShell terminal mein:

```powershell
Set-Location "C:\path\to\digital-nagar-palika\apps\api"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Linux/macOS activation: `source .venv/bin/activate`.

**Kyun:** API dependencies project se isolated rahein. **Files:** `apps/api/pyproject.toml`. **Security:** dependency audit ko CI findings ke saath review karein; production image mein dev dependencies na rakhein. **Verify:** `python -c "import fastapi, sqlalchemy; print('API dependencies ready')"`.

## 5. Database migration lagayein

API folder aur active virtual environment se:

```powershell
alembic upgrade head
```

Migration organization hierarchy, wards, household/citizen records, complaint history, audit, service, document aur payment-reference schema banata hai. PostGIS extension bhi enable hota hai.

**File:** `apps/api/migrations/versions/0001_platform_foundation.py`. **Security:** migration ko production startup par auto-run na karein. Staging backup lekar pehle apply karein. RLS tenant tables par `app.organization_id` maangta hai; future authenticated request/worker code ko verified principal ke basis par transaction ke andar yeh value set karni hogi. Abhi koi production citizen endpoint is RLS contract ko complete nahi karta. **Verify:** command exit code 0; rollback production mein bina DBA-reviewed plan ke na karein.

## 6. API local run aur health check

API folder se:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Doosre PowerShell window se:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/live
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
Invoke-RestMethod http://127.0.0.1:8000/api/v1/public/config
```

Development OpenAPI: `http://127.0.0.1:8000/api/v1/docs`.

**Files:** `apps/api/app/main.py`, `app/api/routes.py`. **Security:** production docs off; TLS reverse proxy aur production allowlist configure honi chahiye. **Verify:** liveness `{status: ok}` aur readiness tabhi ready jab DB aur Redis reachable hon. Health response citizen personal data nahi deta.

## 7. Web portal local run

```powershell
Set-Location "C:\path\to\digital-nagar-palika\apps\web"
corepack pnpm install
corepack pnpm dev
```

Browser: `http://localhost:3000`; admin layout: `/admin`.

**Files:** `apps/web/src/app/page.tsx`, `src/app/admin/page.tsx`, `src/app/style.css`. **Security:** UI shell login/API se connected nahi; `/admin` ko production mein internet par expose na karein. Kisi browser bundle mein secret na rakhein. **Verify:** teen language switch aur mobile viewport dekh lein. Dashes/blank values placeholder hain, live municipal data nahi.

## 8. Mobile shell local run

```powershell
Set-Location "C:\path\to\digital-nagar-palika\apps\mobile"
corepack pnpm install
corepack pnpm start
```

Expo dev QR sirf trusted local network par scan karein. Android device/emulator par language cycling aur screen sizes check karein. **Files:** `apps/mobile/app.json`, `app/index.tsx`. **Security:** token auth, encrypted offline data, QR onboarding, push notifications aur Play Store signing abhi integrated nahi. Test build ko citizen data se connect na karein.

## 9. CI aur change review

Pull request workflow: `.github/workflows/ci.yml`. Isme API lint/pytest aur Semgrep, Gitleaks, Trivy filesystem scan configured hain. Repo root se push/PR par workflow run hona chahiye. Agar project ko alag GitHub repository banayein, workflow ka `working-directory` `digital-nagar-palika/apps/api` se `apps/api` karein aur Trivy ka scan path `digital-nagar-palika` se `.` karein.

**Required next gates:** web/mobile lint and build, dependency audit/OWASP Dependency Check, IaC scan, SBOM, image build+scan, staging DAST (ZAP), API integration/E2E, accessibility, load test, signed image and protected production approval. **Security:** workflow token read-only hi rakhein; production secrets PR jobs ko na dein. **Verify:** findings triage, critical/high block, documented owner+expiry ke bina exception nahi.

## 10. Staging container build

Abhi API Dockerfile hai; web/mobile production Dockerfiles aur full deploy chart/workflow is repository mein nahi hain. API image ka local build:

```powershell
Set-Location "C:\path\to\digital-nagar-palika"
docker build -t dnp-api:staging .\apps\api
docker image inspect dnp-api:staging
```

**File:** `apps/api/Dockerfile`. Image non-root user se run hoti hai. **Security:** tag ko staging-only rakhein; registry push se pehle image scan, SBOM aur secret check karein. Image ko real credentials ke saath run na karein jab tak staging secrets configured na hon. **Verify:** container start/health check, logs aur runtime UID inspect karein.

## 11. Real staging/prod infrastructure (approval gate)

Production se pehle municipality/hosting team decide kare:

1. Approved cloud/account, India-region/data residency and data-sharing policy.
2. Private Postgres+PostGIS, PITR backup, Redis, private object storage and malware quarantine.
3. TLS domain, WAF, private ingress, DNS, egress controls and managed secret/KMS.
4. OIDC workload identity, MFA privileged admin, RBAC/ABAC matrix, login/OTP provider.
5. Approved SMS/push/email, GIS, payment and AI provider contracts and retention rules.
6. Defined SLO, RPO/RTO, alert ownership, incident response and support escalation.
7. Reviewed Terraform plan, network/data flows, threat model and procurement/security sign-off.

Infrastructure directories abhi implementation blueprint hain: `infra/terraform/README.md`, `infra/kubernetes/README.md`. Inmein deployable resource modules/Helm chart abhi complete nahi. **Koi public production address, emergency number, provider key ya municipality record invent na karein.**

## 12. Release, rollback aur after-deploy

Jab deployment pipeline and approvals implemented hon: immutable digest build karein; staging mein migration+smoke+security review; production environment approval; canary/rolling rollout; dashboards monitor; rollback criteria pehle likhein. Schema changes expand/migrate/contract pattern se karein. Database restore rollback plan separately rehearse ho.

**Files:** `docs/operations/deployment.md`, `disaster-recovery.md`, `docs/security/security.md`. **Security:** deploy credentials OIDC/short-lived; DB migration app boot se alag; audit/alerts production par verified. **Verify:** health checks, error/latency, backup success, notification test and access-scope checks. Citizen announcement sirf official approval ke baad.

## 13. Production readiness decision

Niche ke sab boxes complete hone tak service ko internal sandbox/staging tak rakhein:

- [ ] OTP/IdP login, session rotation/revocation, MFA and rate limits implemented.
- [ ] API authentication, tenant context/RLS transaction binding, field masking and negative authorization tests.
- [ ] Complaint/household/admin workflows, approval and append-only audit end-to-end.
- [ ] Object upload scan/quarantine; encryption, retention, consent, export/delete policies.
- [ ] Real providers tested in sandbox; payment reconciliation and webhook validation.
- [ ] CI scans, DAST, load, accessibility, mobile security and independent security review.
- [ ] Encrypted backup restore exercise; approved RPO/RTO met; on-call and incident runbook.
- [ ] Municipality-approved Marathi/Hindi/English content, contact numbers, schemes and public notices.
- [ ] User acceptance, data-protection/legal review and written production approval.

**Reliability ka honest promise:** koi responsible engineer “zero failures guaranteed” nahi bol sakta. Target yeh hona chahiye: failure ko pehle detect karna, impact ko limit karna, safe fallback dena, recover karna aur incident se improve karna. Backup tabhi kaam ka hai jab restore test pass kare; dashboard tabhi useful hai jab owner alerts ka response de.
