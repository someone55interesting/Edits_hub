from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, F, Sum

from .models import Edit, Tag
from .forms import RegisterForm, EditForm, UserUpdateForm, ProfileUpdateForm

# ========== ГЛАВНЫЕ СТРАНИЦЫ ==========

def home(request):
    """Главная страница со всеми эдитами (Pinterest Style)"""
    edits = Edit.objects.all().order_by('-created_at')
    return render(request, 'edits/home.html', {'edits': edits})

def feed(request):
    """Лента эдитов (TikTok Style)"""
    edits = Edit.objects.all().order_by('-created_at')
    return render(request, 'edits/feed.html', {'edits': edits})

# ========== ПРОФИЛЬ (ГЛАВНАЯ ЛОГИКА) ==========

@login_required
def profile_view(request, username=None):
    """Универсальный профиль: свой, чужой и редактирование"""
    
    # 1. Если username не указан, редиректим на свой профиль
    if username is None:
        return redirect('profile', username=request.user.username)

    # 2. Ищем пользователя, чей профиль смотрим
    profile_user = get_object_or_404(User, username=username)
    
    # 3. Обработка формы редактирования (только если это твой профиль)
    u_form = None
    p_form = None
    if request.user == profile_user:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                return redirect('profile', username=request.user.username)
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)

    # 4. Контент и статистика
    user_edits = Edit.objects.filter(author=profile_user).order_by('-created_at')
    liked_edits = Edit.objects.filter(likes=profile_user).order_by('-created_at')
    
    total_views = user_edits.aggregate(Sum('views_count'))['views_count__sum'] or 0
    # Считаем сумму всех лайков на всех видео автора
    total_likes = sum(edit.likes.count() for edit in user_edits)

    # 5. Статус подписки
    is_followed = False
    if request.user.is_authenticated and request.user != profile_user:
        is_followed = request.user.profile.following.filter(user=profile_user).exists()

    context = {
        'profile_user': profile_user,
        'user_edits': user_edits,
        'liked_edits': liked_edits,
        'total_views': total_views,
        'total_likes': total_likes,
        'is_followed': is_followed,
        'followers_count': profile_user.profile.followers.count(),
        'following_count': profile_user.profile.following.count(),
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'edits/profile.html', context)

# ========== ЛОГИКА ВЗАИМОДЕЙСТВИЯ (JSON/AJAX) ==========

@login_required
def increment_views(request, edit_id):
    """Увеличение просмотров при открытии модалки"""
    if request.method == 'POST':
        Edit.objects.filter(id=edit_id).update(views_count=F('views_count') + 1)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_like(request, edit_id):
    """Лайк / дизлайк"""
    if request.method == 'POST':
        edit = get_object_or_404(Edit, id=edit_id)
        if edit.likes.filter(id=request.user.id).exists():
            edit.likes.remove(request.user)
            liked = False
        else:
            edit.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'count': edit.likes.count()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def toggle_follow(request, username):
    """Подписка / отписка"""
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Self-follow'}, status=400)

    me = request.user.profile
    them = target_user.profile

    if me.following.filter(user=target_user).exists():
        me.following.remove(them)
        is_followed = False
    else:
        me.following.add(them)
        is_followed = True

    return JsonResponse({
        'is_followed': is_followed,
        'followers_count': them.followers.count(),
        'following_count': them.following.count(),
    })

# ========== ПОИСК ==========

def search_view(request):
    query = request.GET.get('q', '')
    results = Edit.objects.none()
    if query:
        results = Edit.objects.filter(
            Q(title__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()

    popular_tags = Tag.objects.all()[:10] 
    return render(request, 'edits/search.html', {
        'results': results, 'query': query, 'popular_tags': popular_tags
    })

# ========== СОЗДАНИЕ И УДАЛЕНИЕ ==========

@login_required
def create_edit_view(request):
    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES)
        if form.is_valid():
            new_edit = form.save(commit=False)
            new_edit.author = request.user
            new_edit.save()
            
            tags_data = request.POST.get('tags', '')
            if tags_data:
                tag_list = [t.strip().lower() for t in tags_data.split(',') if t.strip()]
                for tag_name in tag_list:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    new_edit.tags.add(tag_obj)
            form.save_m2m() 
            return redirect('profile', username=request.user.username)
    else:
        form = EditForm()
    return render(request, 'edits/create_edit.html', {'form': form})

@login_required
def delete_edit_view(request, edit_id):
    edit = get_object_or_404(Edit, pk=edit_id)
    if request.user != edit.author:
        return HttpResponseForbidden()
    edit.delete()
    return redirect('profile', username=request.user.username)

# ========== АУТЕНТИФИКАЦИЯ ==========

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')