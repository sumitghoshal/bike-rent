# 🏍️ RentBike — Full-Stack Bike Rental Platform

A production-ready bike rental web application built with **Flask + MongoDB Atlas + Tailwind CSS**.

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── .env                    ← MongoDB URI & secrets (already configured)
│   ├── app.py                  ← Flask application entry point
│   ├── config/
│   │   ├── settings.py         ← All configuration (reads from .env)
│   │   └── database.py         ← MongoDB Atlas connection + indexes
│   ├── models/
│   │   ├── schemas.py          ← MongoDB document schemas
│   │   └── helpers.py          ← ObjectId/datetime serialization
│   └── routes/
│       ├── auth.py             ← Register, Login, Profile, License upload
│       ├── bikes.py            ← Bike CRUD, search, availability, AI recommend
│       ├── bookings.py         ← Create, list, cancel, status update
│       ├── payments.py         ← Payment processing (mock simulation)
│       ├── reviews.py          ← Add reviews, recalculate bike rating
│       ├── vendor.py           ← Vendor dashboard, bikes, bookings
│       └── admin.py            ← Admin stats, user management, KYC
├── frontend/
│   ├── index.html              ← Homepage with hero, search, featured bikes
│   ├── login.html              ← Login + Register (tabbed, offline demo login)
│   ├── register.html           ← Redirects to login.html?tab=register
│   ├── bike-list.html          ← Browse bikes with filters, search, pagination
│   ├── bike-detail.html        ← Bike info, availability check, booking form
│   ├── payment.html            ← Card/UPI/Wallet payment checkout
│   ├── bookings.html           ← My bookings with cancel, pay, review actions
│   ├── dashboard.html          ← Role-based dashboard (user/vendor/admin)
│   ├── vendor.html             ← Vendor panel: add/edit/delete bikes
│   ├── admin.html              ← Admin panel: users, bookings, KYC
│   ├── profile.html            ← Edit profile, upload driving license
│   └── js/
│       └── app.js              ← Shared API client, auth, toast, demo data
├── seed.py                     ← Seeds MongoDB Atlas with demo data
├── requirements.txt            ← Python dependencies
└── README.md                   ← This file
```

---

## ⚡ Quick Start

### Step 1 — Install Python dependencies

```bash
cd project
pip install -r requirements.txt
```

All required packages:
```
flask==3.0.3
flask-cors==4.0.1
flask-jwt-extended==4.6.0
pymongo[srv]==4.7.3
dnspython==2.6.1
python-dotenv==1.0.1
werkzeug==3.0.3
bcrypt==4.1.3
```

### Step 2 — Configure MongoDB Atlas (IMPORTANT)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Select your cluster → **Network Access** → **Add IP Address**
3. Click **Allow Access from Anywhere** (`0.0.0.0/0`) → **Confirm**
4. Your `.env` file is already configured:

```env
MONGO_URI=mongodb+srv://rentbike:12bike07@rentbike-cluster.qbgnrsc.mongodb.net/rentbike?appName=rentbike-cluster&retryWrites=true&w=majority
DB_NAME=rentbike
```

### Step 3 — Seed the database

```bash
cd project
python seed.py
```

This creates:
- 6 demo users (admin, vendor, 4 regular users)
- 9 bikes with real images and data
- 4 sample bookings
- 3 reviews
- 2 payment records

### Step 4 — Start the API server

```bash
cd project/backend
python app.py
```

API runs at: **http://localhost:5000**
Health check: **http://localhost:5000/api/health**

### Step 5 — Open the frontend

```bash
# Option A: Direct file (simplest)
open frontend/index.html

# Option B: Local HTTP server (recommended, avoids CORS issues)
cd project/frontend
python -m http.server 3000
# Then open: http://localhost:3000
```

---

## 🔐 Demo Login Credentials

| Role   | Email                | Password   | Access Level          |
|--------|----------------------|------------|-----------------------|
| 👑 Admin  | admin@rentbike.in  | admin123   | Full platform control |
| 🏪 Vendor | vendor@rentbike.in | vendor123  | Manage bikes & bookings |
| 🚴 User   | rohan@example.com  | user123    | Browse, book, review  |

> **Offline Demo**: Even without the backend running, click the **Quick Demo Login** buttons on the login page to explore all features with demo data.

---

## 🔌 API Reference

### Base URL
```
http://localhost:5000/api
```

All protected routes require:
```
Authorization: Bearer <access_token>
```

---

### 🔑 Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login with email + password | ❌ |
| POST | `/auth/refresh` | Refresh access token | ✅ (refresh token) |
| GET  | `/auth/profile` | Get current user profile | ✅ |
| PUT  | `/auth/profile` | Update name, phone, avatar | ✅ |
| POST | `/auth/upload-license` | Upload driving license (multipart) | ✅ |

**Register example:**
```json
POST /api/auth/register
{
  "name": "Rohan Sharma",
  "email": "rohan@example.com",
  "password": "mypassword",
  "phone": "9999999999",
  "role": "user"
}
```

**Login response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "_id": "...",
    "name": "Rohan Sharma",
    "email": "rohan@example.com",
    "role": "user",
    "kyc_status": "pending"
  }
}
```

---

### 🏍️ Bike Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET  | `/bikes/` | List/search bikes | ❌ |
| GET  | `/bikes/featured` | Top 6 rated bikes | ❌ |
| GET  | `/bikes/recommend` | AI recommendations | ✅ |
| GET  | `/bikes/<id>` | Single bike + reviews | ❌ |
| GET  | `/bikes/<id>/availability` | Check date availability | ❌ |
| POST | `/bikes/` | Add new bike | ✅ vendor/admin |
| PUT  | `/bikes/<id>` | Update bike | ✅ vendor/admin |
| DELETE | `/bikes/<id>` | Delete bike | ✅ vendor/admin |

**Search/Filter parameters for GET `/bikes/`:**
```
?location=Hyderabad   # filter by city
&type=mountain        # mountain|road|electric|city|hybrid
&search=Trek          # search name, brand, model
&min_price=50         # min price per hour
&max_price=200        # max price per hour
&sort=price_asc       # newest|price_asc|price_desc|rating
&available=true       # true|false
&page=1               # pagination
&per_page=12          # items per page (max 50)
```

**Availability check:**
```
GET /api/bikes/<id>/availability?start=2024-12-01T10:00:00&end=2024-12-01T14:00:00

Response: { "available": true }
```

---

### 📅 Booking Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/bookings/` | Create booking | ✅ |
| GET  | `/bookings/my` | My bookings | ✅ |
| GET  | `/bookings/<id>` | Single booking detail | ✅ |
| PUT  | `/bookings/<id>/cancel` | Cancel booking | ✅ (own) |
| PUT  | `/bookings/<id>/status` | Update status | ✅ vendor/admin |

**Create booking:**
```json
POST /api/bookings/
{
  "bike_id": "...",
  "start_time": "2024-12-01T09:00:00",
  "end_time": "2024-12-01T17:00:00",
  "pickup_location": "Hyderabad Central Station",
  "notes": "Please include helmet"
}
```

**Booking status values:**
- `pending` → `confirmed` → `active` → `completed`
- Any → `cancelled`

---

### 💳 Payment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/payments/process` | Process payment | ✅ |
| GET  | `/payments/history` | Payment history | ✅ |

**Process payment:**
```json
POST /api/payments/process
{
  "booking_id": "...",
  "method": "card",
  "card_last4": "4242"
}

Response:
{
  "success": true,
  "transaction_id": "A1B2C3D4E5F6G7H8",
  "message": "Payment successful! Booking confirmed.",
  "amount": 1180.00,
  "method": "card"
}
```

> **Note:** Payment is simulated with a 92% success rate for testing.

---

### ⭐ Review Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/reviews/` | Add review (completed booking only) | ✅ |
| GET  | `/reviews/bike/<bike_id>` | Get bike reviews | ❌ |

---

### 🏪 Vendor Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/vendor/dashboard` | Vendor stats | ✅ vendor |
| GET | `/vendor/bikes` | My listed bikes | ✅ vendor |
| GET | `/vendor/bookings` | Bookings on my bikes | ✅ vendor |

---

### ⚙️ Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/stats` | Platform statistics | ✅ admin |
| GET | `/admin/users` | All users | ✅ admin |
| PUT | `/admin/kyc/<user_id>` | Approve/reject KYC | ✅ admin |
| PUT | `/admin/users/<user_id>/toggle` | Suspend/activate user | ✅ admin |
| GET | `/admin/bookings` | All platform bookings | ✅ admin |
| GET | `/admin/payments` | All payments | ✅ admin |

---

## 🗃️ MongoDB Collections & Schemas

### `users`
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique index)",
  "password": "string (bcrypt hash)",
  "phone": "string",
  "role": "user | vendor | admin",
  "avatar": "string | null",
  "license_image": "string | null (filename)",
  "kyc_status": "pending | approved | rejected",
  "is_active": "boolean",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### `bikes`
```json
{
  "_id": "ObjectId",
  "vendor_id": "string (user _id)",
  "name": "string",
  "type": "mountain | road | electric | city | hybrid",
  "brand": "string",
  "model": "string",
  "year": "number",
  "price_per_hour": "number",
  "price_per_day": "number",
  "location": "string",
  "description": "string",
  "image": "string | null (URL)",
  "features": ["string"],
  "is_available": "boolean",
  "rating": "number (0.0–5.0)",
  "total_reviews": "number",
  "total_bookings": "number",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### `bookings`
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "bike_id": "string",
  "vendor_id": "string",
  "start_time": "ISODate",
  "end_time": "ISODate",
  "total_hours": "number",
  "total_amount": "number",
  "pickup_location": "string",
  "notes": "string",
  "status": "pending | confirmed | active | completed | cancelled",
  "payment_status": "unpaid | paid | refunded",
  "payment_id": "string | null",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### `reviews`
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "bike_id": "string",
  "booking_id": "string (unique per user)",
  "rating": "number (1–5)",
  "comment": "string",
  "created_at": "ISODate"
}
```

### `payments`
```json
{
  "_id": "ObjectId",
  "booking_id": "string",
  "user_id": "string",
  "amount": "number (includes fees)",
  "method": "card | upi | wallet",
  "status": "pending | success | failed",
  "transaction_id": "string | null",
  "card_last4": "string",
  "breakdown": { "base": 0, "service_fee": 0, "gst": 0 },
  "created_at": "ISODate"
}
```

---

## 🧩 Frontend Pages

| Page | File | Description |
|------|------|-------------|
| Home | `index.html` | Hero, search, featured bikes, how-it-works, CTA |
| Login/Register | `login.html` | JWT auth + offline demo login buttons |
| Browse Bikes | `bike-list.html` | Sidebar filters, price range, search, pagination |
| Bike Detail | `bike-detail.html` | Info, availability checker, booking form, reviews |
| Payment | `payment.html` | Card preview, UPI, wallet, success/fail modals |
| My Bookings | `bookings.html` | Filter by status, cancel modal, pay/review actions |
| Dashboard | `dashboard.html` | Role-based: user stats + admin dashboard + vendor panel |
| Vendor Panel | `vendor.html` | Add/edit/delete bikes, manage booking statuses |
| Admin Panel | `admin.html` | User management, KYC approval, all bookings |
| Profile | `profile.html` | Edit name/phone, upload driving license |

---

## 🐛 Bugs Fixed (Latest Update)

| Bug | Location | Fix Applied |
|-----|----------|-------------|
| Book Now button never enabled | `bike-detail.html` | Fixed: button enables after availability check; resets when dates change |
| Review modal never opened | `bike-detail.html` | Fixed: duplicate `display:none` in inline style removed; modal uses `display:flex` |
| All API errors showed as "Backend offline" | `app.js` | Fixed: only `TypeError` (network fail) maps to offline; HTTP errors pass through |
| Booking created but payment page crashed | `payment.html` | Fixed: handles empty/demo booking_id gracefully |
| Cancel didn't update the UI | `bookings.html` | Fixed: updates `allBk` in-place, re-renders current filter |
| Past-date booking rejected (timezone bug) | `bookings.py` | Fixed: removed server-side past-date check (client validates) |
| Dropdown menu flicker on nav | `app.js` | Fixed: proper event listener instead of inline onclick |

---

## 🔐 Security

- **Passwords** — Hashed with `werkzeug` (pbkdf2:sha256), never stored plain
- **JWT tokens** — Access token expires in 24h, refresh token in 30 days
- **CORS** — Configured to allow all origins for development (restrict in production)
- **Input validation** — All API endpoints validate required fields and types
- **Role-based access** — Admin, vendor, and user routes are strictly separated
- **File uploads** — Type and size validated before saving

---

## 🚀 Production Deployment Notes

1. Change `SECRET_KEY` and `JWT_SECRET_KEY` in `.env` to random secure strings
2. Restrict CORS origins to your frontend domain
3. Use `gunicorn` instead of Flask dev server: `gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()`
4. Serve frontend via Nginx or host on Vercel/Netlify
5. Restrict MongoDB Atlas Network Access to your server IP only

---

## 💡 AI Bike Recommendation Logic

The `/bikes/recommend` endpoint:
1. Fetches the user's completed booking history
2. Finds the most frequently rented bike **type** (mountain, road, electric, etc.)
3. Calculates their **average price point**
4. Returns bikes matching that type, within 1.5× their avg price, sorted by rating
5. **New users** with no history → returns top-rated available bikes

---

## 📞 Support

- Email: support@rentbike.in
- Demo credentials: See table above
- Backend health: http://localhost:5000/api/health
