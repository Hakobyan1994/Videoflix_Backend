# 📺 Videoflix (Django + DRF + Postgres + Redis/RQ + FFmpeg + Docker)

Stream videos via HLS, convert uploads into 480p/720p/1080p with FFmpeg, serve media/static from Docker volumes, and expose a JSON API for your frontend. Includes JWT (cookies) auth, email activation, background jobs with RQ, and tests.

---

## ✨ Features

* Django 5 + DRF
* Postgres as DB
* Redis + RQ for async video conversion
* FFmpeg HLS (m3u8 + .ts) generation
* JWT via cookies (login/refresh/logout)
* Media/static mounted as Docker volumes
* Signals enqueue conversion jobs on Video create
* Tests with APITestCase

---

## 📌 1. Prerequisites

* Docker Desktop installed and running (Windows/Mac/Linux)
* Git installed
* FFmpeg globally installed:

**Windows (Chocolatey):**

```bash
choco install ffmpeg
```

**macOS (Homebrew):**

```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt update && sudo apt install ffmpeg
```

Verify installation:

```bash
ffmpeg -version
```

---

## 📌 2. Clone & Environment

Clone repository:

```bash
git clone https://github.com/Hakobyan1994/Videoflix_Backend.git
cd <your-repo>
```

Create your `.env` from the template:

**Linux/Mac:**

```bash
cp .env.template .env
```

**Windows PowerShell:**

```powershell
Copy-Item .env.template .env
```

### Configure `.env`:

* `SECRET_KEY`: use your own secret
* `DEBUG`: `True` in dev, `False` in prod
* `ALLOWED_HOSTS`: `localhost,127.0.0.1`
* `CSRF_TRUSTED_ORIGINS`: match your frontend origins (e.g., `http://127.0.0.1:5500`)
* `DB_*`: set DB name/user/password (used by `docker-compose.yml`)
* `REDIS_*`: keep defaults unless you know what you're doing
* Configure email settings for activation emails
* `DJANGO_SUPERUSER_*`: auto-create admin user

\*\*⚠️ Never commit \*\*\`\`. It is ignored via `.dockerignore` and `.gitignore`.

---

## 📌 3. Build & Run

Start Docker services:

```bash
docker compose up --build
# or detached mode:
docker compose up --build -d
```

This starts:

* **db** (Postgres)
* **redis** (Redis)
* **web** (Django app)

View logs:

```bash
docker compose logs -f web
```

Run migrations:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Common errors:

* **Docker not started:** Ensure Docker Desktop is running.
* **backend.entrypoint.sh LF issue:** Ensure file saved with LF (Unix).

---

### 📌 3.1 DB Migrations & Superuser

If not auto-handled by entrypoint:

```bash
docker compose exec web python manage.py migrate
# Create superuser manually:
docker compose exec web python manage.py createsuperuser
```

**⚠️ Ensure Superuser is active:**

```bash
docker compose exec web python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username="admin")  # or your superuser username
user.is_active = True
user.save()
exit()
```

Login at [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 📌 4. RQ Worker (Background Jobs)

Required for video conversions:

```bash
docker compose exec web python manage.py rqworker default
```

Optional RQ dashboard:

* Add to `urls.py`:

  ```python
  path('django-rq/', include('django_rq.urls'))
  ```
* Open [http://localhost:8000/django-rq/](http://localhost:8000/django-rq/)

---

## 📌 5. API Endpoints (Dev)

**Base URL:** `http://localhost:8000/api/`

### Auth

* `POST /api/login/` — sets cookies
* `POST /api/token/refresh/` — refresh access
* `POST /api/logout/` — delete cookies

### Users

* `POST /api/register/` — create inactive user & send activation email
* `GET /api/activate/<uidb64>/<token>/` — activate account

### Videos

* `GET /api/video/` — list videos
* `GET /api/video/<id>/` — video detail

### HLS Files:

```
/api/video/<id>/480p/index.m3u8
/api/video/<id>/720p/index.m3u8
/api/video/<id>/1080p/index.m3u8
```

Frontend plays HLS URLs:

```
http://localhost:8000/api/video/<id>/<resolution>/index.m3u8
```

---

## 📌 6. Video Conversion

On `Video` save, `post_save` signal enqueues:

```python
convert_video(path, id, 480, "480p")
convert_video(path, id, 720, "720p")
convert_video(path, id, 1080, "1080p")
```

Generated structure:

```
media/
  videos/
    <video_id>/
      480p/index.m3u8
      480p/index001.ts
      720p/...
      1080p/...
```

**Troubleshoot 404:**

* Check RQ worker is running.
* Check FFmpeg installation.
* View logs:

  ```bash
  docker compose logs -f web
  ```

---

## 📌 7. Tests

Run all tests:

```bash
docker compose exec web python manage.py test user_auth.tests
docker compose exec web python manage.py test videos.tests
```

Run specific module/file:

```bash
docker compose exec web python manage.py test user_auth.tests.test_registration_view
docker compose exec web python manage.py test user_auth.tests.test_login_view
```

---

## 📌 8. Environment Variables (Summary)

\`\`**:**

```dotenv
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200

DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=change-me
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=default_from_email
```

---

## 📌 9. Useful Docker Commands

```bash
docker compose up -d
docker compose down
docker compose build web
docker compose exec web bash
docker compose down -v # DANGER: deletes DB/media/static volumes
```
