# KrishiMitra

KrishiMitra is a full-stack agricultural advisory application that brings
crop-health guidance, weather insights, market-price estimates, government
scheme matching, and a farmer-focused chatbot into one interface.

The project is built with a Flask REST API, a React single-page application,
and MongoDB. Gemini powers conversational answers and image-based crop
disease suggestions; Open-Meteo provides weather data.

> **Important:** KrishiMitra is a learning/demo project, not a substitute for
> advice from agricultural experts or official scheme administrators.
> Disease results and price estimates are informational and should be
> independently verified. Sample market-price data is included.

## Features

- Farmer registration, sign-in, and profile management with JWT authentication.
- Leaf-image analysis with suggested disease information and treatment guidance.
- Chat responses grounded in the project's scheme catalogue.
- Scheme matching using farmer profile details.
- Historical crop prices and trend-based estimates.
- Current weather, a short forecast, and rule-based farm advisories.
- Docker Compose setup for running the complete local stack.

## Technology

| Area | Stack |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS |
| API | Python, Flask, Flask-JWT-Extended |
| Database | MongoDB |
| AI | Google Gemini |
| Weather | Open-Meteo |
| Packaging | Docker, Docker Compose |

## Run locally with Docker

Prerequisites: Docker with the Compose plugin and a Gemini API key. The
bundled MongoDB service is used for local development; no Atlas account is
required.

```bash
cp backend/.env.example backend/.env
```

Set `GEMINI_API_KEY` and replace `JWT_SECRET_KEY` in `backend/.env` with a
long, random value. Then start the stack:

```bash
docker compose up --build
```

Open the frontend at <http://localhost:5173>. The API listens on
<http://localhost:5000>; check <http://localhost:5000/api/health> for its
health response. Stop the services with `docker compose down`. To also
remove the local database volume, use `docker compose down --volumes`.

The Compose configuration points the backend at its bundled MongoDB
container. To use MongoDB Atlas instead, update `MONGO_URI` in
`backend/.env` and remove the local MongoDB URI override and dependency from
`docker-compose.yml`.

## Run services without Docker

### Backend

Requires Python 3.10 or newer and a reachable MongoDB instance.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Configure `MONGO_URI`, `JWT_SECRET_KEY`, and `GEMINI_API_KEY` in
`backend/.env`, then run:

```bash
python run.py
```

### Frontend

Requires Node.js 20 or newer.

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The Vite development server runs at <http://localhost:5173>. Set
`VITE_API_URL` in `frontend/.env` if the API is hosted at a different URL.
For Docker builds, configure the URL with the frontend build argument in
`docker-compose.yml`; Vite embeds it at build time.

## Configuration

Backend settings are read from `backend/.env` or the process environment.
See [`backend/.env.example`](backend/.env.example) for the complete template.

| Variable | Purpose |
| --- | --- |
| `MONGO_URI` | MongoDB connection string |
| `MONGO_DB_NAME` | Database name |
| `JWT_SECRET_KEY` | Secret used to sign access tokens; set a unique value |
| `JWT_ACCESS_TOKEN_EXPIRES_MIN` | Access-token lifetime in minutes |
| `GEMINI_API_KEY` | Google AI Studio key for chatbot and image analysis |
| `GEMINI_MODEL` | Gemini model identifier |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `VITE_API_URL` | Frontend API base URL |

Never commit `.env` files, API keys, database credentials, or production
secrets. The repository's `.gitignore` excludes local environment files.

## API overview

All protected endpoints require a bearer access token obtained from
`POST /api/auth/login`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Register a farmer account |
| `POST` | `/api/auth/login` | Authenticate and receive an access token |
| `GET` | `/api/auth/me` | Get the signed-in user's profile |
| `PUT` | `/api/auth/me/profile` | Update the signed-in user's profile |
| `POST` | `/api/disease/detect` | Analyze an uploaded leaf image |
| `GET` | `/api/disease/history` | List the user's prior scans |
| `POST` | `/api/chatbot/ask` | Ask the agricultural chatbot |
| `GET` | `/api/chatbot/history` | List the user's chatbot history |
| `GET` | `/api/schemes/` | List available government schemes |
| `GET` | `/api/schemes/match` | Match schemes to the user's profile |
| `GET` | `/api/price/history?crop=wheat` | Get sample price history |
| `GET` | `/api/price/predict?crop=wheat&days_ahead=14` | Estimate a crop price trend |
| `GET` | `/api/weather/current?location=Ayodhya` | Get weather and farm guidance |
| `GET` | `/api/health` | Check API availability |

## Tests and production notes

Run the backend test suite from the backend directory:

```bash
cd backend
python -m pytest tests/ -v
```

The tests cover the scheme matcher, price model, weather advisory logic, and
vision-client behavior. External model calls are mocked in the vision-client
tests.

Before production use, configure secure secrets and origins, use a shared
rate-limit store when running multiple API workers, and replace the included
sample price data with a trusted live or historical source. Validate all
AI-generated guidance and price estimates before relying on them.
