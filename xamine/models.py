from django.contrib.auth.models import User, AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


from xamine.validators import validate_file_size, check_past_date


class Level(models.Model):
    """ Model to define different points in order workflow """
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class AppSetting(models.Model):
    """ Defines settings that can be set dynamically """
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=256)

    @staticmethod
    def get_setting(name):
        return AppSetting.objects.get(name=name).value

    def __str__(self):
        return self.name


class Patient(AbstractBaseUser, models.Model):
    """ Model to track the patient and their history """

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='user_obj')
    username = None

    # Personal information
    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128)
    email_info = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    birth_date = models.DateField(validators=[check_past_date])
    phone_number = models.CharField(max_length=32)

    USERNAME_FIELD = 'email_info'
    REQUIRED_FIELDS = []

    # Medical information
    allergy_asthma = models.BooleanField()
    allergy_xraydye = models.BooleanField()
    allergy_mridye = models.BooleanField()
    allergy_latex = models.BooleanField()

    notes = models.TextField(null=True, blank=True, max_length=1000)

    doctor = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    # Related fields:
    # -- orders = Order query set

    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        else:
            return f"{self.first_name} {self.last_name}"
            
    def __str__(self):
        return f"{self.full_name} ({self.id})"


class ModalityOption(models.Model):
    """ List of available modality options """

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Team(models.Model):
    """ Model for all technician/radiologist teams """

    name = models.CharField(max_length=64)
    technicians = models.ManyToManyField(User, blank=True, related_name='tech_teams')
    radiologists = models.ManyToManyField(User, blank=True, related_name='radiol_teams')

    # Related fields:
    # -- orders = Order query set

    def __str__(self):
        return self.name


class Order(models.Model):
    """ Model for each individual imaging order placed by doctors """

    # Receptionist Logged
    receptionist = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    # Patient Info
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="orders")
    appointment = models.DateTimeField(null=True, blank=True,)
    survey = models.ForeignKey('Survey', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_survey')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=False, related_name='orders')

    # Automatically record timestamp info
    added_on = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)

    # Level tracking
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING, null=True, blank=True)

    # Order information
    visit_reason = models.CharField(max_length=128)
    imaging_needed = models.CharField(max_length=128) 
    modality = models.ForeignKey(ModalityOption, on_delete=models.DO_NOTHING)
    notes = models.TextField(null=True, blank=True, max_length=1000)

    # Radiology information
    imaged = models.CharField(max_length=64, null=True, blank=True)
    imaged_time = models.DateTimeField(null=True, blank=True)

    # Analysis information
    report = models.TextField(null=True, blank=True, max_length=5000)
    completed = models.CharField(max_length=64, null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)

    # Related fields:
    # -- images: ImageAttachment query set
    # -- secret_keys: OrderKey query set

    # Return as string
    def __str__(self):
        return f"#{self.id} - {self.patient.full_name}"


def image_path(instance, filename):
    """ Determines where to save image attachment files """
    return f"ris/{instance.order_id}/{timezone.now().strftime('%f')}-{filename}"


class Image(models.Model):
    """ Model for the actual Image to be associated with an Order """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images', null=True)
    label = models.CharField(max_length=30)
    image = models.FileField(upload_to=image_path, validators=[validate_file_size])
    user = models.CharField(max_length=30)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} for order # {self.order.id}"


class OrderKey(models.Model):
    """ Secret Key for authenticating patient viewing of orders """
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='secret_keys')
    secret_key = models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.order.patient.email_info} on {self.date_created}"


@receiver(pre_delete, sender=Image)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.

    if instance.image:
        instance.image.delete(False)

class Survey(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, related_name='survey_order')
    completed_time = models.DateTimeField(null=True, blank=True)
    
    visit_rating = models.IntegerField(validators=[MaxValueValidator(10),MinValueValidator(1)])
    visit_notes = models.CharField(max_length=1000, null=True, blank=True)
    
    team_rating = models.IntegerField(validators=[MaxValueValidator(10),MinValueValidator(1)])
    team_notes = models.CharField(max_length=1000, null=True, blank=True)

class WeeklyHours(models.Model):
    # employee_id = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, related_name='survey_order')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee')
    week_of = models.DateField(null=True, blank=True)
    patient_count = models.IntegerField(default=0, validators=[MaxValueValidator(255),MinValueValidator(0)])

class TimeCategory(models.Model):
    week = models.ForeignKey(WeeklyHours, on_delete=models.CASCADE, related_name='week')
    name = models.CharField(max_length=30)
    mon_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
    tues_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
    wed_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
    thur_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
    fri_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
    sat_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
    sun_hours = models.DecimalField(max_digits = 4, decimal_places = 2, validators=[MaxValueValidator(24),MinValueValidator(0)])
