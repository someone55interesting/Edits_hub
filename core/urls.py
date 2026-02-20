from django.contrib import admin
from django.urls import path
from edits import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главные страницы
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('search/', views.search_view, name='search'),

    # Профиль (Универсальный)
    # Теперь и свой профиль, и чужой, и загрузка аватара идут через одну функцию
    path('profile/', views.profile_view, name='my_profile'), 
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('user/<str:username>/', views.profile_view, name='user_public_profile'), # Алиас для совместимости
    
    # Видео / Эдиты
    path('create/', views.create_edit_view, name='create_edit'),
    path('delete/<int:edit_id>/', views.delete_edit_view, name='delete_edit'),
    
    # AJAX / Взаимодействие
    path('toggle-like/<int:edit_id>/', views.toggle_like, name='toggle_like'),
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('increment-views/<int:edit_id>/', views.increment_views, name='increment_views'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)