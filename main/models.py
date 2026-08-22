from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Student(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    phone      = models.CharField(max_length=20)
    matric_no  = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.matric_no}'


class Agent(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    phone       = models.CharField(max_length=20)
    passport    = CloudinaryField('passport', blank=True, null=True)
    id_document = CloudinaryField('id_document (NIN)', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.get_full_name()} (Agent)'


class Hostel(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    agent           = models.ForeignKey(Agent, on_delete=models.CASCADE)
    hostel_name     = models.CharField(max_length=200)
    hostel_type     = models.CharField(max_length=100)
    description     = models.TextField()
    price_session   = models.DecimalField(max_digits=10, decimal_places=2)
    price_semester  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location        = models.CharField(max_length=255)
    distance        = models.CharField(max_length=100, blank=True)
    total_rooms     = models.IntegerField(default=0)
    has_electricity = models.BooleanField(default=False)
    has_water       = models.BooleanField(default=False)
    has_security    = models.BooleanField(default=False)
    has_wifi        = models.BooleanField(default=False)
    has_parking     = models.BooleanField(default=False)
    has_generator   = models.BooleanField(default=False)
    has_bathroom    = models.BooleanField(default=False)
    has_kitchen     = models.BooleanField(default=False)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostel_name
    
class HostelImage(models.Model):
    hostel      = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='images')
    image       = CloudinaryField('image')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.hostel.hostel_name}'    


class Review(models.Model):
    student    = models.ForeignKey(Student, on_delete=models.CASCADE)
    hostel     = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    rating     = models.IntegerField()
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.student} for {self.hostel}'


class SavedHostel(models.Model):
    student  = models.ForeignKey(Student, on_delete=models.CASCADE)
    hostel   = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'hostel')

    def __str__(self):
        return f'{self.student} saved {self.hostel}'