from django.contrib import admin
from.models import Category, Comment, Tag, Post, Rating

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug":('name',)}

admin.site.register(Comment)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug":('name',)}

@admin.register(Post)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title', 'category' , 'author' , 'views']

admin.site.register (Rating)