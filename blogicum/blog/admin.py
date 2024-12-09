from django.contrib import admin

from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'description',
                    'slug',
                    'is_published',
                    'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_published', 'created_at')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'author',
                    'pub_date',
                    'is_published',
                    'category',
                    'location')
    search_fields = (
        'title',
        'text',
        'author__username',
        'category__title',
        'location__name'
    )
    list_filter = ('is_published',
                   'pub_date',
                   'category',
                   'location',
                   'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created_at')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('created_at', 'post', 'author')