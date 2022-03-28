from django.contrib import admin
from .models import Tag

# Register your models here.


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['type', 'color', 'tag_name', 'user']
    list_filter = ['type', 'color', 'user']
    search_fields = ['tag_name']
