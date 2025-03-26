from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, uid, password=None, **extra_fields):
        if not uid:
            raise ValueError('Users must have a UID')
        user = self.model(uid=uid, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, uid, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(uid=uid, password=password, **extra_fields)

class CustomUser(AbstractBaseUser):
    uid = models.CharField(
        max_length=20,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.uid

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff