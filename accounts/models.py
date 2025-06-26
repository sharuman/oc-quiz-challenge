from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    CREATOR = 'creator'
    PARTICIPANT = 'participant'

    USER_TYPE_CHOICES = [
        (CREATOR, 'Creator'),
        (PARTICIPANT, 'Participant'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=CREATOR)


class UserToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for {self.user.email}"
