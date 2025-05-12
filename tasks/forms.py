from django.forms import ModelForm
from .models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task    # model created in models.py
        fields = ['title', 'description', 'important']