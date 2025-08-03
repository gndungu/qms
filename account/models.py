from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from account.modelmixin import TimeStampMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name_plural = "User"


    class AccountType(models.TextChoices):
        ADMINISTRATOR = 'ADMINISTRATOR', 'Administrator'
        CUSTOMER = 'CUSTOMER', 'Customer'

    class Role(models.TextChoices):
        MANAGEMENT = 'MANAGEMENT', 'MANAGEMENT'
        REPRESENTATIVE = 'REPRESENTATIVE', 'REPRESENTATIVE'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    use_two_factor_authentication = models.BooleanField(default=True, verbose_name="Two Factor Authentication")
    account_type = models.CharField(max_length=32, choices=AccountType.choices, default=AccountType.CUSTOMER , verbose_name="Account Type")
    signature = models.ImageField(upload_to="signatures/", null=True, blank=True)
    role = models.CharField(max_length=35, choices=Role.choices, null=True, blank=True)
    department_head = models.BooleanField(default=False, verbose_name="Department Head")
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Optional fields during createsuperuser

    def __str__(self):
        return f"{self.full_name} - {self.email}"


class Organisation(TimeStampMixin):

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'PENDING'
        ACTIVE = 'ACTIVE', 'ACTIVE'

    class Meta:
        verbose_name_plural = "Organisation"
        db_table = "Organisation"

    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    tin_number = models.CharField(max_length=255, null=True, blank=True)
    region = models.ForeignKey("conf.Region", on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    sector = models.ForeignKey("conf.Sector", on_delete=models.SET_NULL, null=True, blank=True)
    representative = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="organisation_representative")
    evaluation_level = models.ForeignKey("conf.EvaluationLevel", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=120, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    notes = models.TextField(null=True, blank=True)
    # user = models.OneToOneField('account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name="organisation_user")

    def __str__(self):
        return f"{self.name}"


class OrganisationLocation(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Organisation Location"
        db_table = "organisation_location"

    organisation = models.ForeignKey("account.Organisation", on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.ForeignKey('conf.District', on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey('conf.Region', on_delete=models.CASCADE, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)


class Department(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Departments"
        db_table = "department"

    organisation = models.ForeignKey("account.Organisation", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    coordinator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="department_coordinator")

    def __str__(self):
        return f"{self.name}"


class OrganisationStandard(TimeStampMixin):
    class Meta:
        verbose_name_plural = "Organisation Standards"
        db_table = "organisation_standard"
        unique_together = ['organisation', 'standard']

    organisation = models.ForeignKey("account.Organisation", on_delete=models.CASCADE)
    standard = models.ForeignKey("conf.Standards", on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.standard}"


class Notification(TimeStampMixin):
    user = models.ForeignKey(CustomUser, related_name="user_notification", on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=120)
    message = models.TextField()
    is_seen = models.BooleanField(default=False)