from django.db import models

# Create your models here.

class Query(models.Model):
    query = models.CharField(max_length=100)
    results = models.CharField(max_length=1000)
    weburl = models.CharField(max_length=100,  default='')

    def __str__(self):
        return self.query
