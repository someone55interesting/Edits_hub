import os
import subprocess
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
import imageio_ffmpeg

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return f"#{self.name}"

class Edit(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video = models.FileField(
        upload_to='edits/videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'webm'])]
    )
    thumbnail = models.ImageField(upload_to='edits/thumbnails/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edits')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    views_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_edits', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Сохраняем видео на диск сервера
        super().save(*args, **kwargs)
        
        # Если превью нет, запускаем генерацию по локальному пути
        if not self.thumbnail and self.video:
            try:
                self.generate_thumbnail()
            except Exception as e:
                print(f"Ошибка превью: {e}")

    def generate_thumbnail(self):
        # ВАЖНО: теперь берем .path (путь на диске), а не .url
        video_path = self.video.path 
        thumb_name = f"thumb_{self.pk}.jpg"
        temp_thumb = f"/tmp/{thumb_name}"
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

        command = [
            ffmpeg_bin, '-ss', '00:00:01', '-i', video_path,
            '-vframes', '1', '-q:v', '2', '-y', temp_thumb
        ]
        
        try:
            # Запускаем FFmpeg локально
            subprocess.run(command, capture_output=True, timeout=15, check=True)
            
            if os.path.exists(temp_thumb):
                with open(temp_thumb, 'rb') as f:
                    # Сохраняем картинку в поле
                    self.thumbnail.save(thumb_name, ContentFile(f.read()), save=False)
                
                # Чистим временный файл
                if os.path.exists(temp_thumb):
                    os.remove(temp_thumb)
                
                # Обновляем только колонку thumbnail, чтобы не зациклить save()
                Edit.objects.filter(pk=self.pk).update(thumbnail=self.thumbnail.name)
        except Exception as e:
            print(f"FFmpeg fail: {e}")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self): return self.user.username

# Сигналы оставляем как есть — они бронебойные
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
    try:
        instance.profile.save()
    except Exception:
        pass