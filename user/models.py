from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100, null=True, blank=True)
    contact_information = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    # Add related_name to avoid clash with auth.User's groups and user_permissions fields
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
    )
