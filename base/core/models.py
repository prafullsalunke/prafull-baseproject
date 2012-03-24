from django.db import models
from django.contrib.auth.models import User
from customdb.uuidfield import UUIDField
from django.core import serializers

LANGUAGE_CHOICES = (
    ('Hindi,','Hindi'),
    ('English','English'),
    ('Marathi','Marathi'),
    ('Tamil','Tamil'),
    ('Gujrati','Gujrati'),
    ('Telugu','Telugu'),
    ('Malayalam','Malayalam'),
    ('Punjabi','Punjabi'),
    ('Bengali', 'Bengali')
)

NUMBER_CHOICES = [(i,i) for i in range(0,11)]
NUMBER_CHOICES.append((" ","--"))

class State(models.Model):
    name = models.CharField(max_length=100)
    is_enabled = models.BooleanField()
    def __str__(self):
        return self.name
        
class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey('State')
    is_major = models.BooleanField()
    is_enabled = models.BooleanField()
    is_approved = models.BooleanField()

    def __str__(self):
        return "%s" % (self.name)

class SampleModel(models.Model):
    name = models.CharField(max_length=150)
    email = models.IntegerField(max_length=150, blank=True)
    age = models.IntegerField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name
