from django.contrib import admin
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)  # Make the created field read-only in the admin interface (by default it does not show up)


# Register your models here.
admin.site.register(Task, TaskAdmin)