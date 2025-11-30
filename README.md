# Lift4M – Lift Project Management & Marketplace (Demo)

This is a FastAPI demo of Lift4M, a role-based lift project management and
marketplace platform. It implements:

- Role-based dashboards:
  - Super Admin
  - Building Manager / Customer
  - Manufacturer
  - Maintenance Provider
- Canonical 10-stage workflow backbone
- Stage mappings for:
  - New Installation
  - Retrofit (treated similarly for this demo)
  - Service / AMC (condensed mapping)
- A timeline UI per project with per-stage status, dates and notes

## Quick start (local dev)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn lift4m.main:app --host 0.0.0.0 --port 8000
