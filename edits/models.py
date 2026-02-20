import os
import subprocess
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import imageio_ffmpeg


# ========== КАТЕГОРИИ ==========
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

# ========== ТЕГИ ==========
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"#{self.name}"

# ========== ЭДИТЫ (ОСНОВНАЯ МОДЕЛЬ) ==========
class Edit(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Видео улетает в Cloudinary
    video = models.FileField(
        upload_to='edits/videos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'webm'])],
        verbose_name="Видео файл"
    )
    
    # Обложка тоже в Cloudinary
    thumbnail = models.ImageField(
        upload_to='edits/thumbnails/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        verbose_name="Обложка"
    )
    
    tags = models.ManyToManyField(Tag, blank=True, related_name='edits')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edits', verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='edits', verbose_name="Категория")
    
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    likes = models.ManyToManyField(User, related_name='liked_edits', blank=True, verbose_name="Лайки")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Эдит"
        verbose_name_plural = "Эдиты"

    def total_likes(self):
        return self.likes.count()

    def __str__(self): return self.title

    # --- ЛОГИКА СОХРАНЕНИЯ И FFmpeg ---
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Сначала просто сохраняем, чтобы файл загрузился в облако и получил URL
        super().save(*args, **kwargs)

        # Если это новое видео и нет обложки — генерируем её
        if (is_new or not self.thumbnail) and self.video:
            # Вызываем генерацию, но не даем ей уронить весь процесс
            try:
                self.generate_thumbnail()
            except Exception as e:
                print(f"Ошибка при создании превью: {e}")

    def generate_thumbnail(self):
        """Создает превью, используя встроенный FFmpeg из библиотеки"""
        if not self.video:
            return

        video_url = self.video.url
        thumbnail_name = f"thumb_{self.pk}.jpg"
        temp_thumb_path = f"/tmp/thumb_{self.pk}.jpg"

        # Получаем 100% рабочий путь к встроенному FFmpeg!
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

        try:
            command = [
                ffmpeg_bin, '-i', video_url,
                '-ss', '00:00:01.000',
                '-vframes', '1',
                '-y',
                temp_thumb_path
            ]
            
            result = subprocess.run(command, capture_output=True, check=True)

            if os.path.exists(temp_thumb_path):
                with open(temp_thumb_path, 'rb') as f:
                    self.thumbnail.save(thumbnail_name, ContentFile(f.read()), save=False)
                os.remove(temp_thumb_path)
                super().save(update_fields=['thumbnail'])
                print(f"Превью успешно создано для эдита {self.pk}")
        
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg ошибка: {e.stderr.decode()}")
        except Exception as e:
            print(f"Общая ошибка генерации превью: {e}")
# ========== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ==========
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    following = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='followers', 
        blank=True
    )

    def __str__(self):
        return f"Профиль {self.user.username}"

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

# --- СИГНАЛЫ ДЛЯ АВТО-СОЗДАНИЯ ПРОФИЛЯ ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.get_or_create(user=instance)