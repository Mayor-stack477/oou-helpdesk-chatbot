from django.db import models
from django.contrib.auth.models import User


# ==========================
# STUDENT MODEL
# ==========================
class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    matric_number = models.CharField(max_length=30, unique=True)
    surname = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.matric_number} - {self.surname}"


# ==========================
# CHAT MODEL
# ==========================
class Chat(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message = models.TextField()
    response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    rating = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user} - {self.message[:50]}"


# ==========================
# DOCUMENT MODEL
# ==========================
class Document(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="student_uploads/%Y/%m/%d/"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    description = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.file.name}"


# ==========================
# RATING MODEL
# ==========================
class Rating(models.Model):

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} for chat {self.chat.id}"