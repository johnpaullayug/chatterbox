# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Post, Comment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_spammer', 'last_post_time')
    list_filter = ('is_spammer', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Spam Protection', {'fields': ('is_spammer', 'last_post_time')}),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'vote_score')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__username')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)