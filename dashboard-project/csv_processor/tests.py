# coding=UTF8
"""
Test classes for CSV Processor application.
"""

from django.test import TestCase
from django.core.files import File
from django.conf import settings
from csv_processor.models import CsvFile, Dimension
from dashboard.models import Category, Datasource, Visualisation, DashboardDataset
import os, json, shutil

class CSVImportTest(TestCase):
    def setUp(self):
        """
        Creates some entries in the database for use by tests.
        This is ran before every test in this class.
        """
        self.__old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, "TEST_MEDIA")
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, "static", "csv_processor", "test", "data", "test_real_monthly.csv"))
        f = File(open(filepath))
        category = Category.objects.get_or_create(name="test_category")[0]
        dataSource = Datasource.objects.get_or_create(name="test_datasource")[0]
        csvFile = CsvFile.objects.get_or_create(visualisationName="test_real_monthly_test",
                                      category = category,
                                      dataSource = dataSource,
                                      upload = f,
                                      source = "http://test.example.com"
                                      )[0]
        Dimension.objects.get_or_create(label="Dumfries and Galloway",
                                        indexForLabel = 1,
                                        type = Dimension.TYPE_CHOICES[0][0],
                                        dataStartIndex = 2,
                                        dataEndIndex = 151,
                                        dataType = Dimension.DATA_CHOICES[1][0],
                                        dataFormat = "£",
                                        makeXaxisOnGraph = False,
                                        csvFile = csvFile)
        Dimension.objects.get_or_create(label="Month-Year",
                                        index = 5,
                                        type = Dimension.TYPE_CHOICES[0][0],
                                        dataStartIndex = 2,
                                        dataEndIndex = 151,
                                        dataType = Dimension.DATA_CHOICES[0][0],
                                        dataFormat = "%b-%y",
                                        makeXaxisOnGraph = True,
                                        csvFile = csvFile)
        
        filepath = os.path.abspath(os.path.join(basepath, "static", "csv_processor", "test", "data", "council-stock-testing.csv"))
        f = File(open(filepath))
        csvFile = CsvFile.objects.get_or_create(visualisationName="council-stock-testing",
                                      category = category,
                                      dataSource = dataSource,
                                      upload = f,
                                      source = "http://test2.example.com"
                                      )[0]
        Dimension.objects.get_or_create(label="Dumfries",
                                        indexForLabel = 2,
                                        type = Dimension.TYPE_CHOICES[0][0],
                                        dataStartIndex = 3,
                                        dataEndIndex = 8,
                                        dataType = Dimension.DATA_CHOICES[2][0],
                                        dataFormat = "",
                                        makeXaxisOnGraph = False,
                                        csvFile = csvFile)
        Dimension.objects.get_or_create(label="Year",
                                        index = 8,
                                        type = Dimension.TYPE_CHOICES[0][0],
                                        dataStartIndex = 3,
                                        dataEndIndex = 8,
                                        dataType = Dimension.DATA_CHOICES[0][0],
                                        dataFormat = "%Y",
                                        makeXaxisOnGraph = True,
                                        csvFile = csvFile)
        
        filepath = os.path.abspath(os.path.join(basepath, "static", "csv_processor", "test", "data", "energy-consumption-testing.csv"))
        f = File(open(filepath))
        csvFile = CsvFile.objects.get_or_create(visualisationName="energy-consumption-testing",
                                      category = category,
                                      dataSource = dataSource,
                                      upload = f,
                                      source = "http://test3.example.com"
                                      )[0]
        Dimension.objects.get_or_create(label="Dumfries and Galloway",
                                        indexForLabel = 2,
                                        type = "row",
                                        dataStartIndex = 3,
                                        dataEndIndex = 11,
                                        dataType = "numeric",
                                        dataFormat = "",
                                        makeXaxisOnGraph = False,
                                        csvFile = csvFile)
        Dimension.objects.get_or_create(label="Year",
                                        index = 9,
                                        type = "row",
                                        dataStartIndex = 3,
                                        dataEndIndex = 11,
                                        dataType = "date",
                                        dataFormat = "%Y",
                                        makeXaxisOnGraph = True,
                                        csvFile = csvFile)

        filepath = os.path.abspath(os.path.join(basepath, "static", "csv_processor", "test", "data", "hospital-admissions.csv"))
        f = File(open(filepath))
        csvFile = CsvFile.objects.get_or_create(visualisationName="hospital-admissions",
                                      category = category,
                                      dataSource = dataSource,
                                      upload = f,
                                      source = "http://test4.example.com"
                                      )[0]
        Dimension.objects.get_or_create(label="Dumfries and Galloway",
                                        indexForLabel = 2,
                                        type = "row",
                                        dataStartIndex = 3,
                                        dataEndIndex = 13,
                                        dataType = "numeric",
                                        dataFormat = "",
                                        makeXaxisOnGraph = False,
                                        csvFile = csvFile)
        Dimension.objects.get_or_create(label="Year",
                                        index = 10,
                                        type = "row",
                                        dataStartIndex = 3,
                                        dataEndIndex = 13,
                                        dataType = "date",
                                        dataFormat = "%Y",
                                        makeXaxisOnGraph = True,
                                        csvFile = csvFile)
        
        filepath = os.path.abspath(os.path.join(basepath, "static", "csv_processor", "test", "data", "employment-quarters-testing.csv"))
        f = File(open(filepath))
        csvFile = CsvFile.objects.get_or_create(visualisationName="employment-quarters",
                                      category = category,
                                      dataSource = dataSource,
                                      upload = f,
                                      source = "http://test5.example.com"
                                      )[0]
        Dimension.objects.get_or_create(label="Dumfries and Galloway",
                                        indexForLabel = 2,
                                        type = "row",
                                        dataStartIndex = 3,
                                        dataEndIndex = 31,
                                        dataType = "numeric",
                                        dataFormat = "",
                                        makeXaxisOnGraph = False,
                                        csvFile = csvFile)
        Dimension.objects.get_or_create(label="Year-Quarter",
                                        index = 9,
                                        type = "row",
                                        dataStartIndex = 3,
                                        dataEndIndex = 31,
                                        dataType = "date",
                                        dataFormat = "%Y-%Q",
                                        makeXaxisOnGraph = True,
                                        csvFile = csvFile)
        
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        settings.MEDIA_ROOT = self.__old_media_root
        super(CSVImportTest, self).tearDown()
        
    def test_csv_import_data_not_none(self):
        csvFile = CsvFile.objects.get(visualisationName="test_real_monthly_test")
        data = csvFile.importData()
        self.assertIsNotNone(data, "Result from CsvFile.importData is null.")
        
    def test_csv_import_data_returns_one_dataset(self):
        csvFile = CsvFile.objects.get(visualisationName="test_real_monthly_test")
        data = csvFile.importData()
        self.assertTrue(len(data) == 1, "CsvFile.importData returned incorrect number of datasets for 2 Dimensions")
        
    def test_csv_import_data_returns_two_datasets(self):
        csvFile = CsvFile.objects.get(visualisationName="test_real_monthly_test")
        Dimension.objects.get_or_create(label="Scotland",
                                        indexForLabel = 1,
                                        type = "row",
                                        dataStartIndex = 2,
                                        dataEndIndex = 151,
                                        dataType = "currency",
                                        dataFormat = "£",
                                        makeXaxisOnGraph = False,
                                        csvFile = csvFile)
        data = csvFile.importData()
        self.assertTrue(len(data) == 2, "CsvFile.importData returned incorrect number of datasets for 3 Dimensions")
        
    def test_csv_import_json_data_returns_string(self):
        csvFile = CsvFile.objects.get(visualisationName="test_real_monthly_test")
        jsonData = csvFile.importJsonData()
        self.assertTrue(type(jsonData) is str, "CsvFile.importJsonData did not return a string")
        self.assertTrue(len(json.loads(jsonData)) == 1, "CsvFile.importJsonData returned incorrect number of datasets for 2 Dimensions")
        
    def test_csv_import_create_dashboard_info_works(self):
        csvFile = CsvFile.objects.get(visualisationName="test_real_monthly_test")
        csvFile.createDashboardInfo()
        vis = Visualisation.objects.get(name=csvFile.visualisationName)
        datasets = DashboardDataset.objects.filter(visualisation=vis)
        self.assertTrue(len(datasets) == 1, "CsvFile.createDashboardInfo created incorrect number of datasets for 2 Dimensions")
        self.assertTrue(len(json.loads(csvFile.dataJson)) == 1, "CsvFile.createDashboardInfo made dataJson incorrect for 2 Dimensions")
        
    def test_csv_import_numeric(self):
        csvFile = CsvFile.objects.get(visualisationName="council-stock-testing")
        csvFile.createDashboardInfo()
        self.assertTrue(len(json.loads(csvFile.dataJson)) == 1, "CsvFile.createDashboardInfo made dataJson incorrect for 2 Dimensions")
        
    def test_csv_row_out_of_range(self):
        """
        Tests that the following error is resolved:
        '   
            if row[dimension.indexForLabel - 1].lower() == dimension.label.lower():
            IndexError: list index out of range
        '
        """
        csvFile = CsvFile.objects.get(visualisationName="hospital-admissions")
        csvFile.createDashboardInfo()
        self.assertTrue(len(json.loads(csvFile.dataJson)) == 1, "CsvFile.createDashboardInfo made dataJson incorrect for 2 Dimensions")
        
    def test_csv_import_quarters_date_format(self):
        csvFile = CsvFile.objects.get(visualisationName="employment-quarters")
        csvFile.createDashboardInfo()
        self.assertTrue(len(json.loads(csvFile.dataJson)) == 1, "CsvFile.createDashboardInfo made dataJson incorrect for 2 Dimensions")