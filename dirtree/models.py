from django.db import models

# Create your models here.


class Number_of_trees_generated(models.Model):
    notg = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Number of trees generated: {self.notg}"

class User_email(models.Model):
    email = models.EmailField(blank=True,unique=True)