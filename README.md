# 🎬 Edits_Hub — Premium Video Content Platform

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-%23000.svg?style=for-the-badge&logo=ffmpeg&logoColor=white)

Edits_Hub — это высокопроизводительная платформа для обмена видеоконтентом, объединяющая лучшие UI/UX решения современных соцсетей. Проект фокусируется на плавности интерфейса, стильном дизайне (glassmorphism) и надежной серверной архитектуре.

## ✨ Главные фичи

* **Pinterest-style Home:** Адаптивная модульная сетка для отображения контента с модальными окнами авторов.
* **TikTok-style Feed:** Бесконечная лента с автоматическим переключением видео и фокусом на активном элементе.
* **Smart Audio System:** Кастомный глобальный контроллер звука (z-index оптимизирован), который активирует звук только на текущем просматриваемом видео.
* **User Management:** Ролевая система (авторизованные пользователи могут публиковать/удалять свои видео и ставить лайки; гости — только просмотр).
* **Premium UI:** Реализованы тени текста, стеклянные блоки профилей авторов с градиентами, идеальное наложение слоев.

## 🛠 Технический стек

* **Backend:** Django
* **Frontend:** Tailwind CSS, Alpine.js / HTMX
* **Video Processing:** FFmpeg (для автоматического создания миниатюр и обработки медиа)
* **Database:** PostgreSQL (с автоматическим созданием профилей через сигналы Django)

## 🚀 Roadmap & Оптимизация
- [ ] Dark Mode by default
- [ ] Skeleton Screens для плавной загрузки
- [ ] Toast Notifications для действий пользователя
- [ ] Система подписок на авторов (Follow System)
- [ ] Open Graph мета-теги для шеринга ссылок
- [ ] Аналитика авторов (просмотры и лайки)

## 💻 Установка и локальный запуск

1. Клонируйте репозиторий:
   ```bash
   git clone [https://github.com/someone55interesting/Edits_Hub.git](https://github.com/someone55interesting/Edits_Hub.git)

2. Создайте и активируйте виртуальное окружение:
python -m venv venv
source venv/bin/activate  # для macOS/Linux

3. Установите зависимости:
   pip install -r requirements.txt

4. Примените миграции и запустите сервер:
python manage.py migrate
python manage.py runserver
 

