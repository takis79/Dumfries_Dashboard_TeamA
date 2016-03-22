from django.db import models
from dataset_importer.models import Importer

# Create your models here.
class APIEndpoint(Importer):
    url = models.URLField()
    
    def Consume(self):
        pass
    
    class Meta:
        abstract = True