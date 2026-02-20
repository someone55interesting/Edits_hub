import os
import subprocess
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

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
        # Сохраняем сначала само видео
        super().save(*args, **kwargs)
        
        # Пробуем сделать превью только если его нет
        if not self.thumbnail and self.video:
            try:
                self.generate_thumbnail()
            except Exception as e:
                print(f"Thumbnail error ignored: {e}")

    def generate_thumbnail(self):
        import imageio_ffmpeg
        # Берем URL видео (Cloudinary)
        video_url = self.video.url
        temp_thumb = f"/tmp/thumb_{self.pk}.jpg"
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

        # Команда с жестким таймаутом, чтобы не вешать сервер
        command = [
            ffmpeg_bin, '-ss', '00:00:01', '-i', video_url,
            '-vframes', '1', '-q:v', '2', '-y', temp_thumb
        ]
        
        try:
            # Даем FFmpeg всего 10 секунд. Если не успел - отмена.
            subprocess.run(command, capture_output=True, timeout=10)
            if os.path.exists(temp_thumb):
                with open(temp_thumb, 'rb') as f:
                    self.thumbnail.save(f"thumb_{self.pk}.jpg", ContentFile(f.read()), save=False)
                os.remove(temp_thumb)
                # Сохраняем только одно поле, чтобы не вызвать save() снова
                Edit.objects.filter(pk=self.pk).update(thumbnail=self.thumbnail.name)
        except Exception:
            pass 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self): return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance) # Форсированное создание если пропал
    instance.profile.save()
