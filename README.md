# AIChatbot — WhatsApp AI Assistant

A production-ready WhatsApp chatbot powered by **OpenAI Assistants**, **Flask**, and **MongoDB**. It handles real-time conversations, manages users, and generates **AFIP-compliant electronic invoices** for Argentine small businesses (monotributistas).

---

## What Problem It Solves

Argentine monotributistas (self-employed workers) need a fast, accessible way to manage clients and issue legal invoices. This bot turns WhatsApp — a tool they already use — into an AI-powered business assistant that can:

- **Answer questions** via natural language
- **Register and manage clients**
- **Generate PDF invoices** and send them via WhatsApp
- **Integrate with AFIP/ARCA** for electronic invoice authorization (CAE)

---

## Key Features

| Feature | Description |
|---|---|
| 🤖 AI Conversations | OpenAI Assistants API with thread management and automatic cleanup |
| 📱 WhatsApp Integration | Meta Cloud API webhooks for real-time message processing |
| 🧾 Invoice Generation | PDF invoices with ReportLab, sent directly via WhatsApp |
| 🏛️ AFIP/ARCA Integration | CAE authorization for Argentine tax-compliant electronic invoices |
| 👥 User Management | MongoDB-backed CRUD for clients and monotributistas |
| 🔐 Webhook Security | HMAC-SHA256 signature validation on all incoming requests |

---

## Architecture Overview

```
WhatsApp User
    │
    ▼
Meta Cloud API ──▶ Flask Webhook (/webhook POST)
                        │
                        ├─▶ Signature Validation (HMAC-SHA256)
                        ├─▶ Message Processing
                        │       │
                        │       ▼
                        │   OpenAI Assistants API
                        │       │
                        │       ├─▶ Function Calls (tool_outputs)
                        │       │       ├─▶ FacturaController
                        │       │       ├─▶ MonotributistaController
                        │       │       └─▶ ClienteController
                        │       │
                        │       └─▶ AI Response
                        │
                        └─▶ WhatsApp Reply
                                │
                                ├─▶ Text Messages
                                └─▶ PDF Documents (invoices)

MongoDB                 AFIP/ARCA
  │                        │
  ├── Usuarios             ├── WSAA Authentication
  ├── Facturas             └── CAE Authorization
  └── Threads
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | Python 3.10+ |
| **Framework** | Flask 3.1 |
| **AI** | OpenAI Assistants API |
| **Database** | MongoDB (pymongo) |
| **PDF** | ReportLab |
| **Messaging** | Meta WhatsApp Cloud API |
| **Tax Integration** | AFIP/ARCA via pyafipws |

---

## Folder Structure

```
├── run.py                      # Application entry point
├── app/
│   ├── __init__.py             # Flask app factory
│   ├── config/
│   │   ├── config.py           # Environment + logging configuration
│   │   ├── database.py         # MongoDB connection
│   │   ├── arca_config.py      # AFIP service URLs and paths
│   │   └── palabras_clave.json # Keyword classification rules
│   ├── views/
│   │   └── views.py            # Webhook routes (GET verify, POST message)
│   ├── controllers/
│   │   ├── thread_controller.py        # OpenAI thread lifecycle
│   │   ├── factura_controller.py       # Invoice creation + PDF dispatch
│   │   ├── monotributista_controller.py # Monotributista operations
│   │   └── cliente_controller.py       # Client CRUD
│   ├── services/
│   │   ├── openai_service.py           # OpenAI Assistants orchestration
│   │   ├── factura_service.py          # Invoice persistence (MongoDB)
│   │   ├── monotributista_service.py   # Monotributista persistence
│   │   ├── cliente_service.py          # Client persistence
│   │   ├── arca_service.py             # CAE generation
│   │   └── arca_auth_service.py        # AFIP authentication
│   ├── models/
│   │   ├── usuario.py          # Abstract base user
│   │   ├── cliente.py          # Client model
│   │   ├── monotributista.py   # Monotributista model
│   │   └── factura.py          # Invoice + Product models, PDF generation
│   ├── utils/
│   │   ├── whatsapp_utils.py   # Message sending, document upload
│   │   └── string_utils.py     # JSON extraction, keyword matching
│   ├── decorators/
│   │   └── security.py         # HMAC signature validation decorator
│   └── arca/                   # AFIP electronic invoice modules
│       ├── authentication.py
│       ├── arca_auth.py
│       ├── electronic_invoice.py
│       ├── journal.py
│       └── wsaa.py
├── test/                       # Unit tests
├── docs/                       # Documentation and assets
├── templates/                  # HTML templates (invoice)
└── img/                        # Static images
```

---

## Installation

### Prerequisites

- Python 3.10+
- MongoDB instance (local or Atlas)
- Meta Developer account with WhatsApp Business API access
- OpenAI API key with Assistants access
- (Optional) AFIP certificates for production invoice authorization

### Setup

```bash
# Clone the repository
git clone https://github.com/facundocarrizo99/AIChatbot.git
cd AIChatbot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For development
```

### Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and fill in your credentials:

| Variable | Description |
|---|---|
| `ACCESS_TOKEN` | Meta WhatsApp API access token |
| `APP_SECRET` | Meta app secret (for webhook signature validation) |
| `PHONE_NUMBER_ID` | WhatsApp phone number ID |
| `VERIFY_TOKEN` | Custom webhook verification token |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_ASSISTANT_ID_ORIGINAL` | OpenAI Assistant ID |
| `MONGO_URI` | MongoDB connection string |
| `DB_NAME` | Production database name |
| `DB_NAME_TEST` | Test database name |

See `.env.example` for the full list including AFIP/ARCA configuration.

---

## Running Locally

```bash
python run.py
```

The server starts on `http://0.0.0.0:8000`.

### Webhook Setup

For local development, expose your server with a tunnel:

```bash
ngrok http 8000
```

Then configure the webhook URL in the Meta Developer Dashboard:

1. Go to **WhatsApp** → **Configuration**
2. Set the webhook URL to `https://<your-ngrok-url>/webhook`
3. Set the verify token to match your `VERIFY_TOKEN` env var
4. Subscribe to the **messages** field

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run a specific test file
pytest test/test_string_to_json.py -v
```

> **Note:** Most tests that interact with MongoDB or OpenAI require valid credentials in `.env`.

---

## API Overview

### `GET /webhook`

Webhook verification endpoint for Meta WhatsApp API.

**Query Parameters:**
- `hub.mode` — Must be `subscribe`
- `hub.verify_token` — Must match `VERIFY_TOKEN`
- `hub.challenge` — Returned on success

### `POST /webhook`

Receives incoming WhatsApp messages. Protected by HMAC-SHA256 signature validation.

**Headers:**
- `X-Hub-Signature-256` — `sha256=<signature>`

**Flow:**
1. Validates signature
2. Extracts message from webhook payload
3. Sends message to OpenAI Assistant
4. Returns AI response via WhatsApp

---

## Scripts

| Command | Description |
|---|---|
| `python run.py` | Start the Flask server |
| `pytest` | Run test suite |
| `pytest --cov=app` | Run tests with coverage report |

---

## Deployment Notes

- Set `AFIP_ENVIRONMENT=production` for real invoice authorization
- Ensure AFIP certificates (`AFIP_CERT_FILE`, `AFIP_PRIVATE_KEY_FILE`) are properly configured
- Use a production WSGI server (e.g., Gunicorn): `gunicorn run:app -b 0.0.0.0:8000`
- Set up persistent MongoDB (Atlas recommended)
- Configure Meta webhook with your production domain (HTTPS required)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit with clear messages: `git commit -m "Add: feature description"`
6. Push and open a Pull Request

---

## License

This project is licensed under the [MIT License](LICENCE.txt).
