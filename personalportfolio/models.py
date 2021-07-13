"""
Module for models
"""

from django.db import models

class File(models.Model):
    """
    Class for file model
    """
    name = models.CharField(max_length=500)
    filepath = models.FileField(upload_to='files/', null=True, verbose_name="")

    def __str__(self):
        return self.name + ": " + str(self.filepath)
