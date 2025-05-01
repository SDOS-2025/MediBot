from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, uid, password=None, **extra_fields):
        if not uid:
            raise ValueError('The UID must be set')
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone', 'age', 'address']
        for field in required_fields:
            if field not in extra_fields:
                raise ValueError(f'{field} is required')
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(
            uid=uid,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, uid, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Set defaults for required fields if not provided
        extra_fields.setdefault('full_name', 'Admin User')
        extra_fields.setdefault('email', 'admin@example.com')
        extra_fields.setdefault('phone', '0000000000')
        extra_fields.setdefault('age', 30)
        extra_fields.setdefault('address', 'Admin Address')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(uid, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    uid = models.CharField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now)
    
    # Required fields for all users
    full_name = models.CharField(max_length=255)
    # email = models.EmailField(unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15)
    # Keep these definitions as they match your existing DB schema
    address = models.CharField(max_length=255)  # Matches current NOT NULL
    age = models.PositiveIntegerField()         # Matches current NOT NULL
    # address = models.CharField( 
    #     max_length=255,
    #     blank=True,            # allow the form to submit an empty string
    #     default='',            # any new or existing user gets '' if no address
    #     # OR: null=True if you want to store NULL instead of ''
    # )
    
    # Doctor-specific fields (optional)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = ['full_name', 'email', 'phone', 'age', 'address']

    def __str__(self):
        return f"{self.full_name} ({self.uid})"

    def save(self, *args, **kwargs):
        # Ensure email is lowercase for consistency
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    hospital_affiliation = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.full_name} ({self.specialization})"

class PatientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # in kg
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Patient {self.user.full_name}"

class Treatment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treatments',
        limit_choices_to={'is_staff': False}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treatments_assigned',
        limit_choices_to={'doctor_profile__isnull': False}
    )
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reqd = models.CharField(max_length=255, null=True, blank=True)
    diagnosis = models.TextField(blank=True, null=True)
    prescribed_medication = models.TextField(blank=True, null=True)

    def __str__(self):
        status = "Closed" if self.is_closed else "Open"
        return f"Treatment #{self.id} - {self.patient.uid} ({status})"