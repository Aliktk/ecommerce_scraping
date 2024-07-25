from django.db import models

class Website(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=50)
    reviews = models.CharField(max_length=50)
    product_url = models.URLField()
    image_url = models.URLField()
    website = models.ForeignKey(Website, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reviews = models.TextField()
    product_url = models.URLField()
    image_url = models.URLField()
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    sentiment_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Review for {self.product.name}"
