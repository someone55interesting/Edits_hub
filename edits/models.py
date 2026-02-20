import os
import subprocess
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"#{self.name}"


class Edit(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    video = models.FileField(
        upload_to='edits/videos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'webm'])],
        verbose_name="Видео файл"
    )
    thumbnail = models.ImageField(
        upload_to='edits/thumbnails/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        verbose_name="Обложка"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='edits')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edits', verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='edits', verbose_name="Категория")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    likes = models.ManyToManyField(User, related_name='liked_edits', blank=True, verbose_name="Лайки")
    views_count = models.PositiveIntegerField(default=0) # Поле для просмотров

    def total_likes(self):
        return self.likes.count()
    
    # ВОТ ЭТИ ДВЕ СТРОЧКИ ДОЛЖНЫ БЫТЬ ТУТ:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # <-- БАЗА ТРЕБУЕТ ЭТУ СТРОКУ

    def save(self, *args, **kwargs):
        is_new_video = False
        if self.pk:
            old_edit = Edit.objects.get(pk=self.pk)
            if old_edit.video != self.video:
                is_new_video = True
        else:
            is_new_video = True

        super().save(*args, **kwargs)

        if is_new_video and self.video and not self.thumbnail:
            self.generate_thumbnail()

    def generate_thumbnail(self):
        video_path = self.video.path
        thumbnail_name = f"thumb_{os.path.basename(video_path).split('.')[0]}.jpg"
        temp_thumb_path = os.path.join(settings.MEDIA_ROOT, 'temp_thumb.jpg')

        try:
            command = [
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:01.000',
                '-vframes', '1',
                '-y',
                temp_thumb_path
            ]
            subprocess.run(command, capture_output=True, check=True)

            with open(temp_thumb_path, 'rb') as f:
                self.thumbnail.save(thumbnail_name, ContentFile(f.read()), save=False)
            
            if os.path.exists(temp_thumb_path):
                os.remove(temp_thumb_path)
            
            super().save(update_fields=['thumbnail'])
        except Exception as e:
            print(f"Ошибка FFmpeg: {e}")

    def __str__(self): return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Эдит"
        verbose_name_plural = "Эдиты"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # СИСТЕМА ПОДПИСОК
    # symmetrical=False значит: если я подписался на тебя, ты не подписываешься на меня автоматически
    following = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='followers', 
        blank=True
    )

    def _str_(self):
        return f"Профиль {self.user.username}"

    # Удобные методы для подсчета
    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

# Авто-создание профиля при регистрации юзера
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Мы проверяем, есть ли профиль, прежде чем сохранять его
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Если вдруг профиля нет (как в случае с твоим админом), создаем его
        Profile.objects.create(user=instance)