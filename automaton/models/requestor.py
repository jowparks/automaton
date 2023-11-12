from django.contrib.auth.models import User
from django.db import models


class Requestor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=15, db_index=True, unique=True)
    objects = models.Manager()
    is_admin = models.BooleanField(default=False)
