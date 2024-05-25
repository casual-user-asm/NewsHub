from django.db import models


class News(models.Model):
    publisher = models.CharField(max_length=255)
    url = models.URLField()
    title = models.TextField()
    short_text = models.TextField()

    def __str__(self):
        return self.title
