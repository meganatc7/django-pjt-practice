from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class Expense(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.category
    
    class Meta:
        ordering: ['-date']
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta: #Category 이름이지만 admin서버에선 Categories로 보이도록
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name