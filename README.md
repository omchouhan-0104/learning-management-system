# 🎓 EduLearn LMS — Learning Management System

A full-featured Learning Management System built with **core Django only** (no DRF, no third-party auth packages). Every major Django topic is covered.

---

## 📋 Django Topics Covered

| Topic | Where Used |
|---|---|
| Custom User Model (AbstractUser) | `accounts/models.py` |
| Custom Manager | `accounts/models.py`, `courses/models.py` |
| AUTH_USER_MODEL | `settings.py` |
| Forms & ModelForms | All apps `forms.py` |
| Field Validation (`clean_email`) | `accounts/forms.py` |
| Multi-field Validation (`clean`) | `accounts/forms.py`, `courses/forms.py` |
| Model Validation (`full_clean`) | `courses/models.py` |
| Widgets | All `forms.py` files |
| FBV (Function-Based Views) | `accounts/views.py`, `courses/views.py` |
| CBV (CreateView, ListView, UpdateView, DeleteView, DetailView) | All apps `views.py` |
| LoginRequiredMixin | All CBVs |
| UserPassesTestMixin | Course, Assignment, Quiz views |
| PermissionRequiredMixin (via user_passes_test) | `accounts/views.py` |
| Authentication & Sessions | `accounts/views.py` |
| Cookies (remember me) | `accounts/views.py` |
| Password Hashing & Reset | `accounts/views.py`, `registration/` templates |
| Groups & Permissions | `accounts/signals.py`, `accounts/admin.py` |
| ForeignKey Relationships | `courses/models.py`, `assignments/models.py` |
| ManyToMany (through model) | `courses/models.py` — `Enrollment` |
| ORM — create, get, filter, update, delete | All views |
| Q Objects | `accounts/views.py`, `courses/views.py` |
| F Expressions | `courses/views.py` — view counter |
| Aggregation (Avg, Count, Sum, Max, Min) | `quizzes/views.py`, `dashboard/views.py` |
| Annotation | `courses/views.py`, `dashboard/views.py` |
| select_related | `courses/views.py`, `dashboard/views.py` |
| prefetch_related | `quizzes/views.py`, `assignments/views.py` |
| Custom Managers | `accounts/models.py`, `courses/models.py` |
| FileField & ImageField | `accounts/models.py`, `courses/models.py`, `assignments/models.py` |
| MEDIA_ROOT & MEDIA_URL | `settings.py`, `lms_project/urls.py` |
| FileResponse (file download) | `courses/views.py` |
| Signals (post_save, pre_save) | `accounts/signals.py` |
| Custom Middleware | `lms_project/middleware.py` |
| Context Processors | `lms_project/context_processors.py` |
| Pagination | `accounts/views.py`, `courses/views.py` |
| Search & Filtering | `courses/views.py`, `accounts/views.py` |
| Query Parameters (request.GET) | All list views |
| Admin Customization | All `admin.py` files |
| Admin Search & Filters | All `admin.py` files |
| Admin Actions | `accounts/admin.py`, `courses/admin.py` |
| URL Routing & Namespaces | All `urls.py` files |
| Static Files | `settings.py`, `static/` |
| Django Templates | All `templates/` |
| Template Tags & Filters | Throughout templates |
| Migrations | All apps `migrations/` |
| Management Commands | `accounts/management/commands/seed_data.py` |
| TestCase & Client | All `tests.py` files |
| Role-Based Access Control | All apps |
| Password Reset (built-in) | `lms_project/urls.py`, `registration/` templates |

---

## 🗂 Project Structure

```
lms_project/
├── accounts/           # Custom User, Auth, Registration
│   ├── management/commands/seed_data.py
│   ├── models.py       # AbstractUser, Custom Manager
│   ├── forms.py        # Forms, Validation
│   ├── views.py        # FBV + CBV, Auth views
│   ├── admin.py        # Custom Admin
│   ├── signals.py      # post_save, pre_save
│   └── urls.py
├── courses/            # Course CRUD, Notes, Enrollment
│   ├── models.py       # ForeignKey, ManyToMany, FileField
│   ├── forms.py
│   ├── views.py        # CBV, F expressions, Q objects, ORM
│   ├── admin.py
│   └── urls.py
├── assignments/        # Assignments, Submissions, Grading
├── quizzes/            # Quizzes, Questions, Results, Aggregation
├── dashboard/          # Role-based dashboards
├── lms_project/
│   ├── settings.py     # All Django settings
│   ├── urls.py         # Root URL conf
│   ├── middleware.py   # Request logging, Role middleware
│   └── context_processors.py
├── templates/          # All HTML templates
├── static/             # CSS, JS, Images
├── media/              # Uploaded files (runtime)
└── manage.py
```

---

## 👥 User Roles

| Role | Access |
|---|---|
| **Super Admin** | Full system control, Django Admin |
| **Admin** | Manage users, courses, view reports |
| **Teacher** | Create/manage courses, upload notes, create assignments & quizzes, grade |
| **Student** | Browse/enroll courses, download notes, submit assignments, take quizzes |

---

## 🚀 Setup & Run

```bash
# 1. Clone / unzip project
cd lms_project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Seed demo data
python manage.py seed_data

# 6. Run server
python manage.py runserver
```

Open **http://127.0.0.1:8000**

---

## 🔑 Demo Accounts (password: `admin123`)

| Username | Role | Access |
|---|---|---|
| `superadmin` | Super Admin | Django Admin + all features |
| `admin1` | Admin | User & course management |
| `teacher1` | Teacher | Create courses, assignments, quizzes |
| `teacher2` | Teacher | Create courses, assignments, quizzes |
| `student1` | Student | Enroll, learn, submit, quiz |
| `student2` | Student | Enroll, learn, submit, quiz |
| `student3` | Student | Enroll, learn, submit, quiz |

---

## 🧪 Run Tests

```bash
python manage.py test --verbosity=2
```

33 tests across all apps covering models, views, forms, and permissions.

---

## 📦 Key URLs

| URL | Description |
|---|---|
| `/accounts/login/` | Login |
| `/accounts/register/` | Register |
| `/dashboard/` | Role-based dashboard |
| `/courses/` | Browse all courses |
| `/courses/create/` | Create course (Teacher) |
| `/accounts/users/` | Manage users (Admin) |
| `/admin/` | Django Admin (Super Admin) |
| `/accounts/password_reset/` | Password reset |
# learning-management-system
