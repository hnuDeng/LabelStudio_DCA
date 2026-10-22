# LabelStudio DCA (Data-Centric AI)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![React](https://img.shields.io/badge/react-19.0%2B-blue)

LabelStudio DCA is a comprehensive Data-Centric AI toolkit, featuring both a Python backend and a React/Vite frontend. It includes modules for active learning, anomaly detection, data augmentation, data quality, and drift detection.

## 📁 Repository Structure

- `backend/` - Python backend API and core DCA modules
- `frontend/` - React frontend built with Vite
- `scripts/` - Automation and utility scripts
- `docs/` - Project documentation
- `tests/` - Backend test suites

## 🚀 Getting Started

### Prerequisites
- Python 3.11+ (CI uses Python 3.11)
- Node.js 22.12+ (CI uses Node.js 24; the locked Vite 8 packages require Node.js 20.19+ or 22.12+)

### Backend Setup
```bash
python -m venv venv
```

Activate the environment in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Or in Bash:

```bash
source venv/bin/activate
```

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

Configure webhook authentication as described below, then start the backend from the repository root:

```bash
python -m uvicorn backend.server:app --reload --host 127.0.0.1 --port 8000
```

Open [the health endpoint](http://127.0.0.1:8000/api/health) to check the server, or [the API documentation](http://127.0.0.1:8000/docs) to try requests. Webhooks require the authentication configuration below. The current webhook handlers acknowledge events and return demonstration responses; the DCA pipeline calls inside them are placeholders.

### Webhook Authentication

Set `LABEL_STUDIO_WEBHOOK_SECRET` to a random token before starting the backend. It has no default value. Generate and set one in your server shell:

```powershell
$env:LABEL_STUDIO_WEBHOOK_SECRET = python -c "import secrets; print(secrets.token_urlsafe(32))"
```

For Bash:

```bash
export LABEL_STUDIO_WEBHOOK_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

In Label Studio, open **Project Settings → Webhooks → Add Webhook**, set the payload URL to `http://127.0.0.1:8000/api/webhooks/label-studio` when both services run on the same host, and enable the payload. For remote instances, use the backend's reachable HTTPS URL. Add a header named `Authorization` with value `Bearer <the token you generated>`, then select the required events and save. See the [official webhook configuration guide](https://labelstud.io/guide/webhooks#add-a-webhook-in-label-studio-ui).

Label Studio supports configured static headers; its [webhook sender](https://github.com/HumanSignal/label-studio/blob/develop/label_studio/webhooks/utils.py) does not generate an HMAC signature. This endpoint checks the Bearer token with constant-time comparison. It does not verify a body signature or prevent replay; use HTTPS for transport integrity. The former prototype `x-label-studio-signature` header is not accepted as authentication.

- Configured secret: missing, malformed, or incorrect tokens return HTTP 403.
- No secret: webhook requests return HTTP 503; the health endpoint remains available.
- Local unsigned demo: explicitly set `LABEL_STUDIO_ALLOW_UNSIGNED_WEBHOOKS=true` and leave the secret unset. Keep this mode on a local development server. A configured secret always requires authentication, even when the demo flag is enabled.

In a second Bash terminal, set `LABEL_STUDIO_WEBHOOK_SECRET` to the same token used by the server, then try an authenticated request:

```bash
curl http://127.0.0.1:8000/api/webhooks/label-studio \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LABEL_STUDIO_WEBHOOK_SECRET" \
  -d '{"action":"TASKS_CREATED","project":{"id":1},"tasks":[{"id":100}]}'
```

Expected response: `{"status":"received","action":"TASKS_CREATED","message":"Processed new tasks"}`.

### Frontend Setup
```bash
cd frontend
npm ci
npm run dev
```

### Verification

From the repository root:

```bash
python -m pytest tests/ -q
```

From `frontend/`:

```bash
npm run build
npm run lint
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
