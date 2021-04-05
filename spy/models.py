from django.db import models


# Create your models here.
class TrailStep(models.Model):
    sequence = models.IntegerField(unique=True)
    directions = models.TextField()
    clue = models.TextField()
    image = models.BooleanField(default=False)
    answer = models.CharField(max_length=20)

    class Meta:
        ordering = ['sequence']
