from django.contrib import admin
from .models import Edit, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Edit)
class EditAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'views_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('views_count',)