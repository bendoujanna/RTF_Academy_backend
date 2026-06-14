from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserProfileManager(BaseUserManager):
    def create_user(self, uid, email, full_name, role='Student', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(uid=uid, email=email, full_name=full_name, role=role, **extra_fields)
        user.set_unusable_password()  # Passwords live in Firebase
        user.save(using=self._db)
        return user

    def create_superuser(self, uid, email, full_name, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(uid, email, full_name, role='Admin', **extra_fields)


class UserProfile(AbstractBaseUser):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Admin', 'Admin'),
    ]
    uid = models.CharField(max_length=128, primary_key=True, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Student')
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'uid']

    def __str__(self):
        return f"{self.full_name} - {self.role}"

    @property
    def is_staff(self):
        return self.is_admin