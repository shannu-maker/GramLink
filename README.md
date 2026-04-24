# Gram Connect

## Overview
Gram Connect is a multi-role commerce platform that connects three stakeholders:

- Customers: discover products from local shops, add to cart, checkout, and track orders
- Shopkeepers: manage products and orders via a dedicated dashboard
- Delivery Partners: accept ready orders and update delivery status

The app also includes an on-site AI assistant that helps users navigate common flows (login/register, open dashboards, view orders, browse products). The assistant can answer FAQs using rules, and optionally generate responses using local Transformers or Hugging Face Inference API when configured.

## Key Features

- Multi-role dashboards: `customer`, `shopkeeper`, `delivery`
- Product management for shopkeepers (add, edit, delete)
- Customer checkout creating per-shop orders with server-side order items
- Order management with clear status flow
- Delivery partner acceptance and delivery status updates
- Public and session-aware product APIs with simple search
- Reorder previous orders (rebuilds cart from last/specific order)
- Price History API with analysis and buy recommendations
- Location master data APIs (states, districts, mandals, villages)
- Multi-language scaffolding (English, Hindi, Tamil, Telugu, Kannada, Malayalam)

## Project Structure (High-Level)

- Custom user model: `members.Shopkeeper` (see `AUTH_USER_MODEL` in `mysite/settings.py`)
- Templates in `templates/` for all roles and flows
- Static files in `static/`; user uploads in `media/`
- Localization files in `locale/` with `LocaleMiddleware` enabled

## URLs & Endpoints

### Web Routes (examples)
- `/` → Home
- `/shopkeeper/login`, `/shopkeeper/register`, `/shopkeeper/dashboard`
- `/customer/login`, `/customer/register`, `/customer/dashboard`, `/customer/cart`, `/customer/orders`
- `/delivery/login`, `/delivery/register`, `/delivery/dashboard`
- `/logout`

### JSON APIs
- Auth (Customer):
  - `POST /api/customer/login/`
  - `POST /api/customer/register/`
- Auth (Shopkeeper):
  - `POST /api/shopkeeper/login/`
  - `POST /api/shopkeeper/register/`
- Auth (Delivery):
  - `POST /api/delivery/login/`
  - `POST /api/delivery/register/`
- Products:
  - `GET /api/products/?mode=alphabetical|shopwise&q=<search>` (filters by customer's village when logged in)
- Price History:
  - `GET /api/product/<product_id>/price-history/`
- Locations:
  - `GET /api/states/`
  - `GET /api/districts/<state_id>/`
  - `GET /api/mandals/<district_id>/`
  - `GET /api/villages/<mandal_id>/`

Note: The previous `POST /api/ai/chat/` endpoint is not present. The assistant currently runs on-page using `members/ai_bot.py` logic (rule-based and optional model integration) and does not expose a dedicated HTTP endpoint by default.

## Order Status Flow

`pending → confirmed → ready → assigned → out_for_delivery → delivered` (plus `cancelled` when applicable)

## Reorder Capability

- Reorder last order: `GET /customer/reorder/`
- Reorder by order id: `GET /customer/reorder/<order_id>/`

These routes reconstruct a cart (client localStorage) and redirect to the cart/checkout flow.

## Localization (i18n)

- Enabled languages: English (`en`), Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Malayalam (`ml`)
- Language switcher base route: `/i18n/`
- Translation files live in `locale/<lang>/LC_MESSAGES/`

## Installation & Setup (Windows PowerShell)

1. Create and activate a virtual environment (optional if `env/` exists)
   - `python -m venv env`
   - `./env/Scripts/Activate.ps1`
2. Install dependencies
   - `pip install -r requirements.txt`
3. Run database migrations
   - `python manage.py migrate`
4. (Optional) Load location master data
   - `python manage.py populate_locations`
5. Start the development server
   - `python manage.py runserver`
6. Visit `http://127.0.0.1:8000/`

## Configuration

- `mysite/settings.py`
  - `AUTH_USER_MODEL = 'members.Shopkeeper'`
  - `LANGUAGES`, `LOCALE_PATHS`, `LocaleMiddleware` enabled
  - `STATIC_URL`, `MEDIA_URL`, `MEDIA_ROOT` configured

- AI Assistant (optional)
  - Local model (if `transformers` is installed): set `AI_TEXT_GEN_MODEL` (default `distilgpt2`)
  - Hugging Face Inference API: set `HF_API_TOKEN` (or `HUGGINGFACEHUB_API_TOKEN`) and optionally `HF_MODEL_ID` (default `google/gemma-2-2b-it`)

## Development Notes

- Products are filtered to a customer's village when a customer session exists
- Price history analysis returns min/avg/max, trend, and a human-readable recommendation
- Static assets are served from `static/`; user-uploaded images from `media/` (dev only)

## License

MIT
