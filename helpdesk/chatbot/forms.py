from django import forms
from .models import Student


class StudentSignupForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            "matric_number",
            "surname",
        ]

        widgets = {
            "matric_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Matric Number"
            }),

            "surname": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Surname"
            }),
        }