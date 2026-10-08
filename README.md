# Smart Restaurant Food Ordering & Kitchen Dashboard (GourmetOS)
**Capstone Project 2 — Django Full-Stack Assignment**

A modern full-stack web application built with **Django 6**, **SQLite**, **Bootstrap 5**, and **JavaScript**, featuring customer table ordering, a dynamic shopping cart, real-time order tracking, and an interactive Kitchen Display System (KDS) for culinary staff.

---

## 🌟 Key Features

1. **Responsive Food Menu with Dietary Badges**:
   - Filter by categories: **Appetizers**, **Main Course**, **Desserts**, and **Beverages**.
   - Instant search by dish name and description.
   - Dietary badges (🌿 Vegetarian, 🍗 Non-Vegetarian) and real-time availability statuses.
   - Quantity stepper and "Add to Cart" with live toast notifications.

2. **Dynamic Shopping Cart & Checkout**:
   - Client-side `localStorage` caching combined with server-side Django session synchronization (`request.session['cart']`).
   - Interactive slide-over offcanvas cart drawer and dedicated cart review page.
   - Dynamic subtotal, sales tax (5%), and grand total calculations.
   - Server-side price verification and stock validation (prevents client price tampering).
   - Table-side checkout form capturing customer name, phone, table number (1–50), and kitchen notes.
   - Automatic cart clearance upon order completion.

3. **Visual Real-Time Order Tracking**:
   - Live order tracking page accessible by numeric Order ID (e.g. `1`) or readable ticket code (e.g. `ORD-71D329`).
   - 4-milestone visual stepper and progress bar:
     $$\text{Received (25\%)} \longrightarrow \text{Preparing (50\%)} \longrightarrow \text{Ready (75\%)} \longrightarrow \text{Completed (100\%)}$$
   - Background JSON status polling every 4 seconds without manual page refreshes.

4. **Kitchen Display System (KDS)**:
   - High-contrast kitchen display interface (`/kitchen/`).
   - Metric overview cards for Active, Received, Preparing, Ready, and Completed orders.
   - Live ticket cards showing table number, customer details, elapsed cooking time, itemized orders, and special dietary requests.
   - One-click workflow transition buttons:
     - `Received` $\rightarrow$ **"Start Cooking (Preparing)"**
     - `Preparing` $\rightarrow$ **"Mark Ready to Serve"**
     - `Ready` $\rightarrow$ **"Complete & Clear Ticket"**
   - Toggleable auto-refresh every 15 seconds.

5. **Django Admin Management**:
   - Pre-configured admin portal at `/admin/` with inlines for `OrderItem`, editable statuses, category sorting, and search filters.
   - Default superuser credentials provided (`admin` / `admin123`).

---

## 🛠️ Mandatory Tech Stack

- **Backend**: Python 3.11+ / 3.13, Django 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3` — Django default, no external DB required)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Production Server**: Gunicorn 26.x
- **Static Assets**: WhiteNoise 6.x
- **Cloud Deployment**: Render Blueprint (`render.yaml`)

---

## 🚀 Local Development Setup

### 1. Activate Virtual Environment
```bash
# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py migrate
```

### 4. Load Sample Data & Superuser (Optional)
```bash
python manage.py load_sample_data
python create_superuser.py
```
> **Default Admin Credentials**:
> - Username: `admin`
> - Password: `admin123`

### 5. Start Development Server
```bash
python manage.py runserver
```
Visit:
- **Menu & Ordering**: `http://127.0.0.1:8000/`
- **Order Tracking**: `http://127.0.0.1:8000/track/`
- **Kitchen Dashboard**: `http://127.0.0.1:8000/kitchen/`
- **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 🧪 Running Automated Tests
```bash
python manage.py test
```
All tests verify models, menu filtering, session cart calculations, checkout validation, order tracking, and kitchen status updates.

---

## ☁️ Deploying to Render

This project includes a pre-configured `render.yaml` blueprint.

1. **Initialize Git & Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Prepare Django project for Render"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Create Web Service on Render**:
   - Sign in to [Render Dashboard](https://dashboard.render.com/).
   - Click **New +** $\rightarrow$ **Blueprint** (or **Web Service**).
   - Select your GitHub repository.
   - Render automatically reads `render.yaml`:
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py`
     - **Start Command**: `python manage.py migrate && python create_superuser.py && gunicorn myproject.wsgi:application`
   - Add environment variable `SECRET_KEY` in the Render dashboard if prompted.
   - Click **Deploy**!
