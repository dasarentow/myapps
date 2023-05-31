from django.db import models




class DsApps(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    in_production = models.BooleanField(default=False)
    app_pic = models.ImageField(upload_to='app_pics/')

    def __str__(self):
        return self.name