# 💊 MyMedicine — Online Pharmacy Platform

A professional Django pharmacy with **Medical Blue** theme, rich animations, promotional image management, prescription system, AI chatbot, and full admin dashboard.

---

## ✨ Key Features

| Feature | Details |
|---------|---------|
| 🎨 Medical Blue Theme | CSS animations, scroll reveal, parallax, typing effect, counters |
| 📸 Promo Image Manager | Upload promotional images → auto-display on homepage |
| 💊 Prescription System | Upload Rx → pharmacist review → auto-add to cart |
| 🤖 MediBot AI Chatbot | Groq LLaMA3 + FAQ + rule-based fallback |
| 🌙 Dark/Light Mode | Smooth theme toggle, persisted in localStorage |
| 📊 Admin Dashboard | Products, orders, prescriptions, banners, promo images, users |
| 🛒 Full Cart & Checkout | AJAX cart, quantity controls, free-delivery progress bar |
| 📱 Fully Responsive | Mobile, tablet, desktop optimized |

---

## 🚀 Local Setup (5 Steps)

**Step 1 — Virtual Environment**
```bash
cd MyMedicine
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

**Step 2 — Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Configure Environment**
Edit `.env` file:
```
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=True
GROQ_API_KEY=your_groq_key_here   # optional, get free at console.groq.com
```

**Step 4 — Migrate & Load Data**
```bash
python manage.py migrate
python manage.py loaddata core/fixtures/initial_data.json
python manage.py createsuperuser
```

**Step 5 — Run**
```bash
python manage.py runserver
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Homepage |
| http://127.0.0.1:8000/dashboard/ | Admin Dashboard |
| http://127.0.0.1:8000/admin/ | Django Admin |

---

## 📸 How to Add Promotional Images

1. Go to **Dashboard → Promo Images → Add Promo Image**
2. Upload your image (recommended sizes below)
3. Set position: Full Width, Half Left/Right, or One Third
4. Set overlay color, text color, badge, button
5. Toggle **Active** and save
6. Images appear automatically on the homepage!

**Recommended image sizes:**
- Full Width Banner: **1200 × 500 px**
- Half Width: **600 × 500 px**
- One Third: **400 × 500 px**

---

## 🌐 PythonAnywhere Deployment (FREE)

**Step 1** — Sign up at [pythonanywhere.com](https://pythonanywhere.com)

**Step 2** — Open Bash console and run:
```bash
git clone your-repo-url MyMedicine
# OR upload ZIP via Files tab and extract

cd ~/MyMedicine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata core/fixtures/initial_data.json
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

**Step 3** — Web tab → Add new web app → Manual config → Python 3.10

**Step 4** — Set paths:
- Source code: `/home/yourusername/MyMedicine`
- Working directory: `/home/yourusername/MyMedicine`
- Virtualenv: `/home/yourusername/venv`

**Step 5** — WSGI file → replace all content with:
```python
import sys, os
sys.path.insert(0, '/home/yourusername/MyMedicine')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mymedicine.settings'
os.environ['DEBUG'] = 'False'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Step 6** — Static files in Web tab:
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/MyMedicine/staticfiles` |
| `/media/` | `/home/yourusername/MyMedicine/media` |

**Step 7** — Edit `.env`:
```
SECRET_KEY=your-production-secret-key
DEBUG=False
```

**Step 8** — Add your domain to `settings.py`:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
```

**Step 9** — Click **Reload** 🎉

---

## 🔧 Common Fixes

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: django` | Activate venv: `source venv/bin/activate` |
| `no such table` error | Run `python manage.py migrate` |
| Static files not loading | Run `python manage.py collectstatic --noinput` |
| `DisallowedHost` error | Add domain to `ALLOWED_HOSTS` in settings.py |
| Images not uploading | Check `media/` folder exists and is writable |
| 500 error on PythonAnywhere | Check error log in Web tab |

---

## 📁 Project Structure
```
MyMedicine/
├── mymedicine/          # Django project config (settings, urls, wsgi)
├── core/                # Products, categories, prescriptions, promo images, banners
├── accounts/            # Auth — login, register, profile
├── cart/                # Shopping cart (AJAX-powered)
├── orders/              # Checkout, order tracking
├── admin_panel/         # Custom dashboard (products, orders, Rx, banners, promos)
├── chatbot/             # MediBot (Groq AI + FAQ + rule-based)
├── articles/            # Health articles and blog
├── templates/           # All HTML templates
├── static/
│   ├── css/theme.css    # Medical Blue theme (1030+ lines)
│   └── js/main.js       # Animations, scroll reveal, cart, chatbot (448 lines)
├── media/               # Uploaded files (products, prescriptions, promos)
├── core/fixtures/       # Sample data (categories, FAQs, banners)
├── requirements.txt
├── .env
└── manage.py
```

---

## 🎨 Customization

**Change colors** → Edit `:root` in `static/css/theme.css`
```css
--primary: #1565c0;      /* Main blue */
--primary-dark: #0d47a1; /* Dark blue */
--primary-light: #42a5f5; /* Light blue */
```

**Change site name** → Edit `mymedicine/settings.py`
```python
SITE_NAME = 'MyMedicine'
```

**Add products** → `/dashboard/products/add/`
**Add promo images** → `/dashboard/promo-images/add/`
**Add FAQs for chatbot** → `/admin/chatbot/faq/`

---

*MyMedicine © 2024 — Built with Django 4.2 · Bootstrap 5.3 · Medical Blue*
