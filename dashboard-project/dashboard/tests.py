from django.test import TestCase

class BasicTestCase(TestCase):
    def test_tester(self):
        """Test to identify that unit tests are running"""
        self.assertEqual(True, 5 == 5)
        self.assertEqual(False, 5 == 6)