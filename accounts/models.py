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
