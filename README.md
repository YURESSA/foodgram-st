# 🍲 Фудграм

**Фудграм** — платформа для публикации и управления рецептами. Пользователи могут:

- публиковать рецепты,
- добавлять рецепты в избранное,
- формировать списки покупок,
- подписываться на других авторов.

---

## 🚀 Технологии

- **Django Rest Framework**
- **Djoser**
- **PostgreSQL**
- **Gunicorn**
- **Nginx**
- **Docker & Docker Compose**
- **GitHub Actions** (CI/CD)

---

## 📦 Быстрый старт

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/YURESSA/foodgram-st.git
   ```

---

2. **Создайте `.env` файл в директории `/backend/`**, используя код ниже как шаблон:
   ```ini
   DEBUG=True
   SECRET_KEY=django-insecure-41w890+xadf1bxiohf09c+4y*qj$j$@tjw_uqx)&imzr0bs^
   ALLOWED_HOSTS=127.0.0.1,localhost
   CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

   PG_DB_NAME=foodgram_backend
   PG_DB_USER=foodgram_user
   PG_DB_PASSWORD=6ghHIUNJBY87JBIO8jY
   PG_DB_HOST=postgres
   PG_DB_PORT=5432
   ```

---

3. **Перейдите в директорию `infra` и запустите проект:**
   ```bash
   cd infra
   docker-compose up
   ```
4. **При необходимости можно создать суперпользователя**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

   🛠️ При запуске:
    - frontend-контейнер соберёт статику и завершит работу,
    - backend выполнит миграции и загрузит тестовые данные (ингредиенты и т.п.).

---

## 🌐 Доступ к сервисам

- **Frontend:** [http://localhost](http://localhost)
- **API Docs:** [http://localhost/api/docs/](http://localhost/api/docs/)
- **Админка:** [http://localhost/admin/](http://localhost/admin/)

---

## ⚙️ CI/CD с GitHub Actions

Настроен процесс CI/CD с использованием **GitHub Actions**, включающий:

- Проверку кода с помощью `flake8`:
    - Проверяются файлы в директории `backend/`
    - Конфигурация берётся из `setup.cfg`
- Сборку и публикацию Docker-образов:
    - `backend` → `yuressa/foodgram-back:latest`
    - `frontend` → `yuressa/foodgram-front:latest`

Workflow `main.yml` содержит два задания:

### lint:

- Проверяет код на соответствие PEP8 с помощью `flake8`

### build:

- После успешной проверки кода:
    - Авторизуется на DockerHub
    - Собирает и пушит образы `backend` и `frontend`

- [Ссылка на DockerHub (backend)](https://hub.docker.com/r/yuressa/foodgram-back)
- [Ссылка на DockerHub (frontend)](https://hub.docker.com/r/yuressa/foodgram-front)

---

👨‍💻 **Автор:** Гошуренко Юрий Юрьевич  
🎓 **Институт:** УРФУ, ИРИТ-РТФ  
🧾 **Группа:** РИ-230948

---

## 🔐 Создание суперпользователя

Если необходимо вручную создать суперпользователя, выполните команду:

```bash
docker-compose exec backend python manage.py createsuperuser
```