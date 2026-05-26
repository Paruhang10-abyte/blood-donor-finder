from django.db import models
from django.contrib.auth.models import User
import uuid

# Donor Model
class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5)
    district = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"

# Blood Request Model
class BloodRequest(models.Model):
    patient_name = models.CharField(max_length=100)
    blood_group_needed = models.CharField(max_length=5)
    district = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
    # links request to specific donor
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, null=True)
    
    # tracks request status
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=20, unique=True, blank=True, default='')  
    
    # smart blood request: tracks if patient changed blood group from search
    blood_group_changed = models.BooleanField(default=False)
    original_blood_group = models.CharField(max_length=5, blank=True, default='')

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group_needed}"