# models.py

from django.db import models
from django.forms import ValidationError

class Tawassut(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return self.name

class Kafeel(models.Model):
    number = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    tawassut = models.ForeignKey(Tawassut, on_delete=models.SET_NULL, null=True)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Student(models.Model):
    admission_number = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    kafeel = models.ForeignKey(Kafeel, on_delete=models.CASCADE)
    sponsoring_since = models.DateField(null=True)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ('Dropped Out', 'Dropped Out'),
        ('Course Complete', 'Course Complete'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.name

class Progress(models.Model):
    kafeel = models.ForeignKey(Kafeel, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=255, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    study_report = models.TextField()
    paid_date = models.DateTimeField()

    def clean(self):
        if self.kafeel and hasattr(self.kafeel, 'status') and self.kafeel.status == 'Deactive':
            raise ValidationError("Cannot accept payment for a deactivated Kafeel.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
# models.py

from django.db import models
from django.forms import ValidationError
from django.urls import reverse

class KafeelStatusUpdate(models.Model):
    kafeel_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('Activate', 'Activate'),
        ('Deactivate', 'Deactivate'),
    ])
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Validate Kafeel number
        try:
            kafeel = Kafeel.objects.get(number=self.kafeel_number)
        except Kafeel.DoesNotExist:
            raise ValidationError("Kafeel with the provided number does not exist.")

        # Update Kafeel status
        if self.status == 'Activate':
            kafeel.status = 'Active'
        elif self.status == 'Deactivate':
            kafeel.status = 'Deactive'

        kafeel.save()

        super().save(*args, **kwargs)


from django.db import models
from django.forms import ValidationError
from django.urls import reverse

class StudentStatusUpdate(models.Model):
    admission_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=[
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
    ])
    updated_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        try:
            student = Student.objects.get(admission_number=self.admission_number)
        except Student.DoesNotExist:
            raise ValidationError("Student with the provided admission number does not exist.")

        if student.status == self.status:
            raise ValidationError(f"The student is already {self.status}.")

    def save(self, *args, **kwargs):
        self.full_clean()

        # Update Student status
        student = Student.objects.get(admission_number=self.admission_number)
        student.status = self.status
        student.save()

        super().save(*args, **kwargs)
