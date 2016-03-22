"""
Test classes for Dataset_Importer models.
"""

from django.test import TestCase
from models import Dataset
import json, datetime, util


class ImporterTest(TestCase):
    def setUp(self):
        Dataset.objects.get_or_create(name="test_dataset",
                                      dataJSON="""[{"x":"test"}]""")
        Dataset.objects.get_or_create(dataJSON="""[{"y":"test"}]""")

    def test_dataset_json(self):
        dataset = Dataset.objects.get(name="test_dataset")
        self.assertEqual(json.loads(dataset.dataJSON), [{"x":"test"}], "Dataset JSON did not load correctly.")
        self.assertEqual(dataset.fromJSON(), [{"x":"test"}], "Dataset.fromJSON did not load correctly.")

    def test_dataset_str(self):
        dataset = Dataset.objects.get(name="test_dataset")
        self.assertTrue(str(dataset) == dataset.name, "Dataset did not return correct name from __str__")
        dataset = Dataset.objects.get(pk=2)
        self.assertTrue(str(dataset) == "Imported Dataset " + str(dataset.pk), "Dataset without name did not return correct name from __str__")

class UtilTest(TestCase):
    def test_date_json(self):
        startingDate = datetime.date(2000, 1, 1)
        dateJSON = json.dumps(startingDate, cls=util.DatetimeEncoder)
        self.assertTrue(isinstance(dateJSON, basestring), "date JSON isn't a string.")
        self.assertTrue(dateJSON == '"2000-01-01"', "date JSON isn't correct.")
        
    def test_datetime_json(self):
        startingDate = datetime.datetime(2000, 1, 1, 1, 1)
        dateJSON = json.dumps(startingDate, cls=util.DatetimeEncoder)
        self.assertTrue(isinstance(dateJSON, basestring), "datetime JSON isn't a string.")
        self.assertTrue(dateJSON == '"2000-01-01T01:01:00Z"', "datetime JSON isn't correct.")
        
        itemJSON = json.dumps({"y": 5, "x": dateJSON[1:-2:]})
        # TODO: Find out why there's extra quotes around results from DatetimeEncoder
        endDate = json.loads(itemJSON, cls=util.DateTimeDecoder)["x"]
        self.assertTrue(startingDate == endDate, "Datetime has changed after encoding and decoding to JSON.")