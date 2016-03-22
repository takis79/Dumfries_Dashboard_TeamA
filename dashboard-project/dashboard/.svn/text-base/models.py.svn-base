"""
Specifies all the models used by dashboard app.
Some of the these models are used by other apps 
for convenience.
"""

from django.db import models
from django.contrib.auth.models import User
import json
from dataset_importer import util

from dataset_importer.models import Dataset, Datasource

class DashboardDatasource(Datasource):
    """
    A subclass of generic Datasource.
    
    Adds a method to get all the Visualisations for this Datasource.
    """
    
    def getAllWidgets(self):
        """
        Retrieves all visualisations related to this Datasource,
        calls the getWidget method to get a JS friendly-form.
        """
        
        visualisations = Visualisation.objects.filter(dataSource=self)
        widgets = []
        for vis in visualisations:
            widgets.append(vis.getWidget())
        return widgets
    
class Category(models.Model):
    """
    Provides a way of grouping similar Visualisations together.
    """
    
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Visualisation(models.Model):
    """
    Contains application specific information about how several datasets
    should be displayed together.
    """
    dataSource = models.ForeignKey(Datasource)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category)
    type = models.CharField(max_length=100)
    sizeX = models.IntegerField()
    sizeY = models.IntegerField()
    xLabel = models.CharField(max_length=100)
    yLabel = models.CharField(max_length=100)
    
    def getWidget(self):
        """
        Returns all the required info for displaying this visualisation.
        """
        
        firstDataset = DashboardDataset.objects.filter(visualisation=self)[0]
        
        widget = {'name': self.name,
                           'id': "vis" + str(self.pk),
                           'pk': self.pk,
                           'category': self.category.name,
                           'type': self.type,
                           'dataset': [json.loads(d.dataJSON, cls=util.DateTimeDecoder) for d in DashboardDataset.objects.filter(visualisation=self)],
                           'datasetLabels': [d.name for d in DashboardDataset.objects.filter(visualisation=self)],
                           'sourceName': self.dataSource.name,
                           'sourceLink': self.dataSource.link,
                           'datasetName': firstDataset.name,
                           'datasetLink': firstDataset.link,
                           'description': self.description,
                           'xLabel': self.xLabel,
                           'yLabel': self.yLabel,
                           'sizeX': self.sizeX,
                           'sizeY': self.sizeY}
        return widget
    
    def calculateTrendData(self):
        datasetObjects = DashboardDataset.objects.filter(visualisation=self)
        datasets = [json.loads(d.dataJSON, cls=util.DateTimeDecoder) for d in datasetObjects]
        maxYItem = max(max(d, key=lambda i:i['y']) for d in datasets)
        minYItem = min(min(d, key=lambda i:i['y']) for d in datasets)
        
        analysisResults = []
        #{"name":"blah", "lastMonth:":5, "last3Months":10, "last6Months":100, "lastYear":-5}
        for dataset in datasetObjects:
            datasetResult = {"name": str(dataset)}
            data = dataset.fromJSON()
            lastDateItem = data[len(data) - 1]
            
            if isinstance(lastDateItem["x"], basestring):
                continue
            
            # Identify percentage increases/decreases for the 4 time periods.
            for element in reversed(data):
                elapsedTime = lastDateItem["x"] - element["x"]
                days = elapsedTime.days
                percentageDiff = round(((lastDateItem["y"] - element["y"]) / float(element["y"])) * 100, 1)
                if days >= 28 and days < (1.5 * 31):
                    datasetResult["lastMonth"] = percentageDiff
                elif days >= (3 * 28) and days < (1.5 * 3 * 31):
                    datasetResult["last3Months"] = percentageDiff
                elif days >= (6 * 28) and days < (1.5 * 6 * 31):
                    datasetResult["last6Months"] = percentageDiff
                elif days >= (12 * 28) and days < (1.5 * 12 * 31):
                    datasetResult["lastYear"] = percentageDiff
                elif days >= (12 * 28 * 3) and days < (1.5 * 12 * 31 * 3):
                    datasetResult["last3Years"] = percentageDiff
                elif days >= (12 * 28 * 5) and days < (1.5 * 12 * 31 * 5):
                    datasetResult["last5Years"] = percentageDiff
                elif days >= (1.5 * 12 * 31 * 5):
                    break
            
            analysisResults.append(datasetResult)
            
        return {"maxY": maxYItem, "minY": minYItem, "analysis": analysisResults}
    
    def getTrendWidget(self):
        trendData = self.calculateTrendData()
        
        count = sum(len(v) for v in trendData["analysis"])
        
        if (count < 1):
            sizeY = 1
        elif (count < 5):
            sizeY = 2
        elif (count < 10):
            sizeY = 3
        else:
            sizeY = 4
            
        firstDataset = DashboardDataset.objects.filter(visualisation=self)[0]
        
        widget = {'name': self.name,
                           'id': "trend" + str(self.pk),
                           'pk': self.pk,
                           'category': self.category.name,
                           'type': self.type,
                           'trends': trendData,
                           'sourceName': self.dataSource.name,
                           'sourceLink': self.dataSource.link,
                           'datasetName': firstDataset.name,
                           'datasetLink': firstDataset.link,
                           'sizeX': self.sizeX,
                           'sizeY': sizeY}
        return widget
        
    
    def __str__(self):
        return self.name

class DashboardDataset(Dataset):
    """
    A subclass of Dataset that includes Dashboard-specific fields.
    """
    
    visualisation = models.ForeignKey(Visualisation)
    filename = models.CharField(max_length=300, blank=True, null=True)
    
    def __str__(self):
        if self.name:
            return self.name
        return "Dashboard Dataset " + str(self.pk)
    
class SavedConfig(models.Model):
    """
    Provides a umbrella to group several SavedGraphs together
    under one config.
    """
    
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    
    def __str__(self):
        return self.name

class SavedGraph(models.Model):
    """
    Stores the current size/position of a graph so that it can
    be reproduced later.
    """
    
    visualisation = models.ForeignKey(Visualisation)
    isTrendWidget = models.BooleanField(default=False)
    savedConfig = models.ForeignKey(SavedConfig)
    xPosition = models.IntegerField()
    yPosition = models.IntegerField()
    sizeX = models.IntegerField()
    sizeY = models.IntegerField()
    
    def __str__(self):
        return "Saved Graph " + str(self.pk)
    