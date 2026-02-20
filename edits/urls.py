from django.urls import path
from . import views

app_name = 'edits'  # если используете namespace — обязательно

urlpatterns = [
    # Профили
    path('profile/', views.profile_view, name='profile'),                     # свой профиль
    path('profile/<str:username>/', views.profile_view, name='user_public_profile'),  # чужой профиль
    path('profile/avatar/upload/', views.upload_avatar, name='upload_avatar'),  # загрузка аватара

    # Для обратной совместимости (если где-то используется)
    path('my-profile/', views.my_profile_redirect, name='my_profile'),

    # Эдиты
    path('create/', views.create_edit_view, name='create_edit'),
    path('delete/<int:edit_id>/', views.delete_edit_view, name='delete_edit'),

    # Лайки
    path('like/<int:edit_id>/', views.toggle_like, name='toggle_like'),

    # Подписки
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),

    # Другие страницы
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
]