"""
Contains models used by csv_processor.

Some methods use models from dashboard for convenient importing into the db.
"""

from django.db import models
from dataset_importer.models import Importer, Datasource
import os, csv, collections, json, util, locale
from datetime import datetime
from django.db.models.signals import pre_delete 
from django.dispatch import receiver
from dataset_importer import util as datasetUtil
import util
import itertools

from dashboard.models import Visualisation, DashboardDataset, Category

def convertCustomFormattingToStrpTime(dateString, formatString):
    if "%Q" in formatString:
        # %Q matches 'Q1', 'Q2', 'Q3', and 'Q4'.
        dateString = dateString.replace("Q1", "Mar")
        dateString = dateString.replace("Q2", "Jun")
        dateString = dateString.replace("Q3", "Sep")
        dateString = dateString.replace("Q4", "Dec")
    return dateString

def convertCustomFormattingToStrpTimeFormat(formatString):
    if "%Q" in formatString:
        formatString = formatString.replace("%Q", "%b")
    return formatString

class CsvFile(Importer):
    """
    A subclass of Importer.
    
    This specifies a type of Importer that uses CSV files.
    """
    
    visualisationName = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category)
    dataSource = models.ForeignKey(Datasource)
    upload = models.FileField()
    source = models.URLField()
    
    def importData(self):
        """
        Executes the import.
        
        Returns data in the form of a list containing multiple datasets.
        Each dataset is a list of dictionaries with x, y values.
        """
        
        def num(s):
            try:
                return int(s)
            except ValueError:
                return float(s)
        
        data = []
        xAxisData = []
        dimensions = self.dimensions.all()
        for dimension in dimensions:
            with open(self.upload.path) as csvfile:
                reader = util.UnicodeReader(csvfile, encoding="iso-8859-1")
                localData = []
                if dimension.type == "row":
                    if dimension.index != None:
                        i = dimension.index
                        for row in reader:
                            i -= 1
                            if i == 0:
                                localData = row[dimension.dataStartIndex - 1:dimension.dataEndIndex - 1:]
                                break
                    
                    else:
                        index = 0
                        for row in reader:
                            try:
                                if row[dimension.indexForLabel - 1].lower() == dimension.label.lower():
                                    localData = row[dimension.dataStartIndex:dimension.dataEndIndex:]
                                    break
                                else:
                                    index += 1
                            except IndexError:
                                continue
                        
                        if localData == []:
                            # Couldn't find exact match, lets check substrings.
                            csvfile.seek(0)
                            index = 0
                            for row in reader:
                                if row[dimension.indexForLabel - 1].lower() in dimension.label.lower() or dimension.label.lower() in row[dimension.indexForLabel - 1].lower():
                                    if row[dimension.indexForLabel - 1].lower() is None or row[dimension.indexForLabel - 1].lower() == "":
                                        continue
                                    
                                    localData = row[dimension.dataStartIndex:dimension.dataEndIndex:]
                                    break
                                else:
                                    index += 1
                else:
                    raise NotImplementedError("No support for Dimension.type of column yet.")
            
            #print "Pre-formatting {0}:".format(dimension.label)
            #print localData
            
            # Format data!
            locale.setlocale(locale.LC_ALL, 'en_GB.UTF8')
            if dimension.dataType == "date":
                # Custom Format Specifiers
                localData = [convertCustomFormattingToStrpTime(d.encode('utf-8'), dimension.dataFormat)  for d in localData]
                
                dimension.dataFormat = convertCustomFormattingToStrpTimeFormat(dimension.dataFormat)
                # Use dimension.format as a strptime to retrieve DateTime object
                #print "FORMAT: " + dimension.dataFormat
                localData = [datetime.strptime(d.encode('utf-8'), dimension.dataFormat) for d in localData]
            elif dimension.dataType == "currency":
                # Use dimension.format to remove currency markers ($)
                # and cast to float.
                localData = [locale.atoi(d.replace(dimension.dataFormat, "")) for d in localData]
            elif dimension.dataType == "numeric":
                # Cast data to int or float
                localData = [num(d.replace(",", "")) for d in localData]
            #...
            else:
                pass
            #print "Post formatting:"
            #print localData
            if dimension.makeXaxisOnGraph:
                xAxisData = localData[:]
            else:
                data.append(localData)
        new = []
        #print data
        # [ [ {"y": 48600.0, "x": 2008.0},  {"y": 48600.0, "x": 2008.0}], [] ]
        for yAxis in data:
            #print "found a yaxis"
            if len(yAxis) != len(xAxisData):
                #print len(yAxis)
                #print len(xAxisData)
                raise NotImplementedError("Axes of different lengths aren't supported yet.")
            l = []
            for y, x in zip(yAxis, xAxisData):
                val = {
                    "x": x,
                    "y": y
                }
                l.append(val)
            new.append(l)
            #print new
        data = new
        return data
    
    def importJsonData(self):
        """
        A shortcut method that imports data, saves it to the
        dataJson field, and returns the json.
        """
        self.dataJson = json.dumps(self.importData(), cls=datasetUtil.DatetimeEncoder)
        self.save()
        return self.dataJson
    
    def createDashboardInfo(self):
        """
        A shortcut method that creates all the required database entries
        for this data for use by the dashboard app.
        It imports the data, saves it to json, and creates the database entries.
        """
        vis = Visualisation.objects.get_or_create(name=self.visualisationName,
                                                  category=self.category,
                                                  description = self.description,
                                                  type="line",
                                                  dataSource=self.dataSource,
                                                  sizeX=2,
                                                  sizeY=2,
                                                  xLabel="Date",
                                                  yLabel="Placeholder")[0]
        
        # Delete any datasets associated with this visualisation already.
        DashboardDataset.objects.filter(visualisation=vis).delete()
        
        importedDatasets = self.importData()
        dimensions = self.dimensions.all()
        for dataset, dimension in itertools.izip(importedDatasets, dimensions):
            DashboardDataset.objects.create(name=dimension.label, visualisation=vis, dataJSON=json.dumps(dataset, cls=datasetUtil.DatetimeEncoder), link=self.source)
        self.dataJson = json.dumps(self.importData(), cls=datasetUtil.DatetimeEncoder)
        self.save()
        
@receiver(pre_delete)
def delete_csv_dashboard_related(sender, instance, **kwargs):
    """
    This functions runs before any deletes happen in the database.
    
    If we are deleting a CsvFile entry, then special logic is required to
    delete all associated Visualisations and DashboardDatasets.
    """
    if sender == CsvFile:
        vis = Visualisation.objects.get(name=instance.visualisationName)
        datasets = DashboardDataset.objects.filter(visualisation=vis).delete()
        vis.delete()
    
class Dimension(models.Model):
    """
    This model represents part of a row or column that the user
    is interested in retrieving from the CSV file.
    
    This model contains information on the exact location of the data,
    including labels, and which parts of the row or column we want.
    
    It also contains information on the type of that data, what
    format it is, and whether it should form the x-axis.
    
    This model contains no logic, but the values specified are used during
    the importData method of CsvFile.
    """
    TYPE_CHOICES = (
                        ("row", "Row"),
                        ("col", "Column")
    )
    
    DATA_CHOICES = (
                    ("date", "Date"),
                    ("currency", "Currency"),
                    ("numeric", "Numeric"),
                    ("percentage", "Percentage"),
                    ("fraction", "Fraction"),
                    ("text", "Text")
    )
    
    label = models.CharField("Data Label",
                            max_length=50,
                            help_text=u"The label that appears for this data series in the CSV file.")
    indexForLabel = models.PositiveIntegerField("Label Index",
                            null=True, blank=True,
                            help_text=u"The row or column index that the label appears in. If blank, you must specify 'index'. \
                            This is orthogonal to the type. E.g. If type is 'Row', then this field is the column index that the label appears in.")
    type = models.CharField("Label Type",
                            max_length=3,
                            choices=TYPE_CHOICES,
                            default=TYPE_CHOICES[0][0],
                            help_text=u"Whether these indices should be taken as row or column values.")
    index = models.PositiveIntegerField("Override label with index",
                            null=True, blank=True,
                            help_text=u"<OPTIONAL> If data series has no label, this field can specify the index.")
    dataStartIndex = models.PositiveIntegerField("Data Start",
                            help_text=u"The index of the first cell of interest for this data series.")
    dataEndIndex = models.PositiveIntegerField("Data End",
                            help_text=u"The index of the last cell of interest for this data series.")
    dataType = models.CharField("Data Type",
                            max_length=10,
                            choices=DATA_CHOICES,
                            default=DATA_CHOICES[0][0],
                            help_text=u"The type of data the CSV contains for this data series.")
    dataFormat = models.CharField("Data Format",
                            max_length=100,
                            help_text=u"ADVANCED: Specify the format of the data. If dataType is 'date', uses strptime formatting. Otherwise uses Python Regex formatting.")
    makeXaxisOnGraph = models.BooleanField("Make x-axis on graph",
                            help_text=u"Select ONE dimension to be used as the X axis.")
    csvFile = models.ForeignKey(CsvFile, related_name='dimensions')