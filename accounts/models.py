from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from tinymce.models import HTMLField


class UserProfile(models.Model):
    """User Profile, one to one relationship with users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    email = models.CharField(max_length=64, blank=True)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    short_bio = HTMLField(blank=True)
    avatar = models.ImageField(blank=True)
    # Extra Credit
    city = models.CharField(max_length=64, blank=True)
    state = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=64, blank=True)
    favorite_animal = models.CharField(max_length=64, blank=True)
    hobby = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['user', ]

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


# Create an empty profile when the user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
