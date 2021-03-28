from django.forms import ModelForm
from .models import Quiz, Question, Answers


class NewQuizForm(ModelForm):
    class Meta:
        model = Quiz
        fields = '__all__'