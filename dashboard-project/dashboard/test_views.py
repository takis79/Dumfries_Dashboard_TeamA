import json, datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import SESSION_KEY
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from csv_processor import util
from dataset_importer import util as dateutil
from dateutil.tz import *
from django.db.models import Q

from models import Datasource, DashboardDataset, Visualisation, SavedConfig, SavedGraph, Category

class TestAuthViews(TestCase):
    def setUp(self):
        User.objects.create_user("user@example.com", password="test1234")
        User.objects.create_user('user2@example.com', password='test1234')

    def test_login_view_loads_anonymous(self):
        """Check login page loads when user is anonymous."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/pages/login.djhtml')
        
    def test_login_view_loads_logged_in(self):
        """Check login page loads when user is logged in."""
        self.client.login(username='user@example.com', password='test1234')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/pages/login.djhtml')
        response = self.client.get(reverse('savedConfigs'))
        self.assertTemplateUsed(response, 'dashboard/pages/savedConfigs.djhtml')
        self.assertTrue(not response.context['configurations'])

    def test_ajax_login_view_fails_blank(self):
        """Check AJAX login handles blank data dictionary."""
        response = self.client.post(reverse('ajax_login'), {})
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_ajax_login_view_fails_invalid(self):
        """Check AJAX login handles invalid login details."""
        response = self.client.post(reverse('ajax_login'), {"email":"tester@wrong.com", "password":"wrongPass"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'], False)

    def test_ajax_login_view_pass_valid(self):
        """Check AJAX login works with correct details."""
        response = self.client.post(reverse('ajax_login'), {"email":"user@example.com", "password":"test1234"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'], True)
        self.assertTrue(SESSION_KEY in self.client.session)

    def test_ajax_login_view_user_inactive(self):
        response = self.client.post(reverse('ajax_login'), {"email":"user23@example.com", "password":"test1234"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'], False)

        
    def test_logout_view_pass_valid(self):
        """Check logout works when user is logged in."""
        self.client.login(username='user@example.com', password='test1234')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(SESSION_KEY not in self.client.session)

    def test_ajax_register(self):
        response = self.client.post(reverse('ajax_register'),{'email':"test@test.com", "password":"test", "repeatPass":"test"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'],True)

    def test_ajax_register_existing_user(self):
        response = self.client.post(reverse('ajax_register'),{'email':"user@example.com", "password":"test1234", "repeatPass":"test1234"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'],False)

    def test_ajax_register_emptyEmail(self):
        response = self.client.post(reverse('ajax_register'),{'email':"", "password":"test", "repeatPass":"test"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'],False)

    def test_ajax_register_emptyPassword(self):
        response = self.client.post(reverse('ajax_register'),{'email':"test@test.com", "password":"", "repeatPass":""})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'],False)

    def test_ajax_register_emptyRepeatPassword(self):
        response = self.client.post(reverse('ajax_register'),{'email':"test@test.com", "password":"test", "repeatPass":""})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'],False)

    def test_ajax_register_passwordMismatch(self):
        response = self.client.post(reverse('ajax_register'),{'email':"test@test.com", "password":"test", "repeatPass":"tester"})
        jsonResponse = json.loads(response.content)
        self.assertEqual(jsonResponse['success'],False)

    def test_registrationPage(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/pages/register.djhtml')

    def test_ajax_isAuthenticated(self):
        self.client.login(username='user@example.com', password='test1234')
        response = self.client.get(reverse('ajax_checkAuthenticated'))
        r = json.loads(response.content)
        self.assertEqual(r['is_authenticated'], True)
        
class TestSavedConfigView(TestCase):
    def setUp(self):
        User.objects.create_user("test@example.com", password="test")
        User.objects.create_user("test2@example.com", password="test2")
        ds1 = Datasource.objects.create(name="test")
        ds2 = Datasource.objects.create(name="STUFF")
        cat = Category.objects.create(name="CategoryTest")
        cat2 = Category.objects.create(name="STUFF")
        vis1 = Visualisation.objects.create(dataSource=ds1, category=cat, name="TestVis", sizeX=2, sizeY=2, yLabel="Y-Label", xLabel="X-Label")
        DashboardDataset.objects.create(visualisation=vis1, dataJSON=json.dumps([{"x":datetime.datetime(2000,1,1),"y":34},{"x":datetime.datetime(2002,1,1),"y":532}],cls=dateutil.DatetimeEncoder))
        vis2 = Visualisation.objects.create(dataSource=ds2, category=cat2, name="STUFF", sizeX=2, sizeY=2, yLabel="Y-Label", xLabel="X-Label")
        DashboardDataset.objects.create(visualisation=vis2, dataJSON=json.dumps([{"x":datetime.datetime(2000,1,1),"y":152},{"x":datetime.datetime(2002,1,1),"y":185}],cls=dateutil.DatetimeEncoder))
        testingData=[{u'yPosition': 0, u'sizeX': 2, u'sizeY': 1, u'xPosition': 0, u'isTrendWidget': False, u'visPK': 1}]
        user1=User.objects.get(username='test@example.com')
        savedConfig=SavedConfig.objects.create(name='test',user = user1)
        for graph in testingData:
            vis = Visualisation.objects.filter(id=graph["visPK"])[0]

            savedGraph = SavedGraph.objects.create(visualisation=vis,
                                               savedConfig=savedConfig,
                                               isTrendWidget = graph["isTrendWidget"],
                                               xPosition=graph["xPosition"],
                                               yPosition=graph["yPosition"],
                                               sizeX=graph["sizeX"],
                                               sizeY=graph["sizeY"])
            savedGraph.save()
        testingData2=[{u'yPosition': 1, u'sizeX': 2, u'sizeY': 1, u'xPosition': 1, u'isTrendWidget': True, u'visPK': 2}]
        savedConfig2=SavedConfig.objects.create(name='test2',user = user1)
        for graph in testingData2:
            vis = Visualisation.objects.filter(id=graph["visPK"])[0]

            savedGraph = SavedGraph.objects.create(visualisation=vis,
                                               savedConfig=savedConfig2,
                                               isTrendWidget = graph["isTrendWidget"],
                                               xPosition=graph["xPosition"],
                                               yPosition=graph["yPosition"],
                                               sizeX=graph["sizeX"],
                                               sizeY=graph["sizeY"])
            savedGraph.save()

    def test_save_config(self):
        vis1 = Visualisation.objects.get(name='STUFF')
        vis2 = Visualisation.objects.get(name='TestVis')
        user = User.objects.get(username='test@example.com')
        data = [{"visPK":1,"xPosition":0,"yPosition":0,"sizeX":2,"sizeY":1,"isTrendWidget":False},
                {"visPK":2,"xPosition":2,"yPosition":0,"sizeX":2,"sizeY":1,"isTrendWidget":False}]
        jsondata=json.dumps(data)
        self.client.login(username='test@example.com', password='test')
        response = self.client.post(reverse('saveConfig'),{'name':'test1',"data":jsondata})
        savedConfig = SavedConfig.objects.get(name="test1")
        testSaved = SavedGraph.objects.filter(savedConfig=savedConfig)
        self.assertEqual(testSaved.count()>0,True)
        self.assertEqual(json.loads(response.content)['message'],'Added new Saved Configuration.')
        self.assertEqual(json.loads(response.content)['success'],True)

    def test_save_config_empty_name(self):
        self.client.login(username='test@example.com', password='test')
        data = [{"visPK":1,"xPosition":0,"yPosition":0,"sizeX":2,"sizeY":1,"isTrendWidget":False},
                {"visPK":2,"xPosition":2,"yPosition":0,"sizeX":2,"sizeY":1,"isTrendWidget":False}]
        jsondata=json.dumps(data)
        response = self.client.post(reverse('saveConfig'),{'name':'','data':jsondata})
        self.assertEqual(json.loads(response.content)['message'],"Failed to add new Saved Config name must be specified")
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_save_config_not_list(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.post(reverse('saveConfig'),{'name':'test2','data':'sdsfdsfs'})
        self.assertEqual(json.loads(response.content)['message'],"Failed to add new Saved Config incorrect data format")
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_save_config_not_dict_in_list(self):
        self.client.login(username='test@example.com', password='test')
        response = self.client.post(reverse('saveConfig'),{'name':'test3','data':'[sdsfdsfs,fsdfsdfsd]'})
        self.assertEqual(json.loads(response.content)['message'],"Failed to add new Saved Config incorrect data format")
        self.assertEqual(json.loads(response.content)['success'], False)
    
    def test_savedConfig_view_denies_anonymous(self):
        """Check that savedConfigs denies anonymous users and redirects to login page."""
        response = self.client.get(reverse('savedConfigs'), follow=True)
        self.assertRedirects(response, reverse('login') + "/?next=" + reverse('savedConfigs'))
        response = self.client.post(reverse('ajax_login'), follow=True)
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_ajaxLoadSavedConfig_isTrend_False(self):
        testing = [{'sourceName': u'test', 'sizeX': 2, 'sizeY': 1,
                    'dataset': [[{u'y': 34, u'x': u'2000-01-01T00:00:00Z'},
                                 {u'y': 532, u'x': u'2002-01-01T00:00:00Z'}]],
                    'datasetLink': u'', 'xLabel': u'X-Label', 'yLabel': u'Y-Label', 'id': 'vis1', 'row': 0, 'category': u'CategoryTest',
                    'datasetName': None, 'name': u'TestVis', 'sourceLink': u'',
                    'datasetLabels': [None], 'pk': 1, 'type': u'', 'col': 0, "description": ""}]
        self.client.login(username='test@example.com', password='test')
        response=self.client.post(reverse('ajax_loadSavedConfig'),{'id':1})
        jsonResponse = json.loads(response.content)
        def deep_sort(obj):
            """
            Recursively sort list or dict nested lists
            """

            if isinstance(obj, dict):
                _sorted = {}
                for key in sorted(obj):
                    _sorted[key] = deep_sort(obj[key])

            elif isinstance(obj, list):
                new_list = []
                for val in obj:
                    new_list.append(deep_sort(val))
                _sorted = sorted(new_list)

            else:
                _sorted = obj

            return _sorted
        testDict = deep_sort(testing[0])
        testDict2=deep_sort(jsonResponse['widgets'][0])
        from unittest import TestCase
        TestCase.maxDiff = None
        self.assertDictEqual(testDict, testDict2)

    def test_ajaxLoadSavedConfig_isTrend_True(self):
        self.client.login(username='test@example.com',password = 'test')
        response = self.client.post(reverse('ajax_loadSavedConfig'),{'id':2})
        testing = [{'sourceName': u'STUFF', 'sizeX': 2, 'sizeY': 1,
                    'trends': {'minY': {'y': 152, 'x': u'2000-01-01T00:00:00Z'},
                               'maxY': {'y': 185, 'x': u'2002-01-01T00:00:00Z'},
                               'analysis': [{'name': 'Dashboard Dataset 2'}]}, 'datasetLink': u'', 'xLabel': u'X-Label',
                    'yLabel': u'Y-Label', 'id': 'vis2', 'row': 1, 'category': u'STUFF', 'datasetName': None, 'name': u'STUFF',
                    'sourceLink': u'', 'datasetLabels': [None], 'pk': 2, 'type': u'', 'col': 1, "description":""}]
        jsonResponse = json.loads(response.content)
        def deep_sort(obj):
            """
            Recursively sort list or dict nested lists
            """

            if isinstance(obj, dict):
                _sorted = {}
                for key in sorted(obj):
                    _sorted[key] = deep_sort(obj[key])

            elif isinstance(obj, list):
                new_list = []
                for val in obj:
                    new_list.append(deep_sort(val))
                _sorted = sorted(new_list)

            else:
                _sorted = obj

            return _sorted
        testDict = deep_sort(testing[0])
        testDict2= deep_sort(jsonResponse['widgets'][0])
        self.assertDictEqual(testDict,testDict2)

    def test_ajaxLoadSaved_different_User(self):
        self.client.login(username='test2@example.com', password='test2')
        response = self.client.post(reverse('ajax_loadSavedConfig'),{'id':1})
        self.assertEqual(json.loads(response.content)['message'],'Error: This Saved Configuration does not belong to you.')
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_ajax_DeleteSaved_differentUser(self):
        self.client.login(username='test2@example.com', password = 'test2')
        response=self.client.post(reverse('ajax_deleteSavedConfig'),{'id':1})
        self.assertEqual(json.loads(response.content)['message'],'Error: This Saved Configuration does not belong to you.')
        self.assertEqual(json.loads(response.content)['success'], False)

    def test_ajax_DeleteSaved(self):
        self.client.login(username='test@example.com', password = 'test')
        response=self.client.post(reverse('ajax_deleteSavedConfig'),{'id':1})
        self.assertEqual(json.loads(response.content)['message'],'Deleted Saved Configuration.')
        self.assertEqual(json.loads(response.content)['success'], True)
        self.assertEqual(SavedConfig.objects.filter(name="test1").exists(),False)


        
class TestGraphsView(TestCase):
    def setUp(self):
        ds1 = Datasource.objects.create(name="test")
        cat = Category.objects.create(name="CategoryTest")
        vis1 = Visualisation.objects.create(dataSource=ds1, category=cat, name="TestVis", sizeX=2, sizeY=2, yLabel="Y-Label", xLabel="X-Label")
        DashboardDataset.objects.create(visualisation=vis1, dataJSON=json.dumps([{"x":5,"y":10},{"x":7,"y":15}]))

    def test_ajax_getGraph(self):
        vis1 = Visualisation.objects.get(name = 'TestVis')
        response = self.client.get(reverse('ajax_getGraph'), {"id": vis1.pk})
        jsonResponse=json.loads(response.content)
        self.assertEqual(jsonResponse["pk"],vis1.pk)

    def test_ajax_getGraph_noID(self):
        vis1 = Visualisation.objects.get(name='TestVis')
        response = self.client.get(reverse('ajax_getGraph'))
        self.assertEqual(response.status_code, 400)

    def test_graphs_view_loads(self):
        response = self.client.get(reverse('graphs'))
        self.assertTrue(response, "Graph view returned a falsy object.")
        
    def test_ajax_getGraphs_view_loads(self):
        """Check AJAX getGraphs returns all graphs"""
        response = self.client.get(reverse('ajax_getGraphs'))
        jsonResponse = json.loads(response.content)
        self.assertTrue(len(jsonResponse['widgets']) > 0, "Widget list should be not empty.")
        
class TestSearchView(TestCase):
    def setUp(self):
        ds1 = Datasource.objects.create(name="test")
        ds2 = Datasource.objects.create(name="STUFF")
        cat = Category.objects.create(name="CategoryTest")
        cat2 = Category.objects.create(name="STUFF")
        vis1 = Visualisation.objects.create(dataSource=ds1, category=cat, name="TestVis", sizeX=2, sizeY=2, yLabel="Y-Label", xLabel="X-Label")
        DashboardDataset.objects.create(visualisation=vis1, dataJSON=json.dumps([{"x":20,"y":152},{"x":20,"y":185}]))
        vis2 = Visualisation.objects.create(dataSource=ds2, category=cat2, name="STUFF", sizeX=2, sizeY=2, yLabel="Y-Label", xLabel="X-Label")
        DashboardDataset.objects.create(visualisation=vis2, name="dataset", link="http://example.com", dataJSON=json.dumps([{"x":datetime.datetime(2000,1,1),"y":152},{"x":datetime.datetime(2002,1,1),"y":185}],cls=dateutil.DatetimeEncoder))

    def test_search_returns_result(self):
        response = self.client.get(reverse('search', kwargs={"searchTerm": "test" }))
        self.assertTrue(len(response.context["results"]) == 1, "Search test returned incorrect number of results.")
        self.assertTrue(response.context["results"][0]["name"] == "TestVis", "Search result has incorrect name")
        self.assertTemplateUsed(response,'dashboard/pages/searchResults.djhtml')

    def test_searchTerm_is_None(self):
        response = self.client.get(reverse('search',kwargs={"searchTerm":None }))
        self.assertTemplateUsed(response, 'dashboard/pages/searchResults.djhtml')

    def test_category_list(self):
        testcategories = Category.objects.all()
        response = self.client.get(reverse('categoryList'))
        testing = response.context['categories']
        self.assertTemplateUsed(response, 'dashboard/pages/categoryList.djhtml')
        for f,b in zip(testing,testcategories):
            self.assertEqual(f,b)

    def test_category_view(self):
         response = self.client.get(reverse('category', kwargs={"categoryName" : "STUFF" }))
         self.assertTemplateUsed(response, 'dashboard/pages/category.djhtml')
         self.assertTrue(response.context['error'] is None)
         testList = [{'sourceName': u'STUFF', 'sizeX': 2, 'sizeY': 2,
                      'dataset': [[{u'y': 152, u'x': u'2000-01-01T00:00:00Z'}, {u'y': 185, u'x': u'2002-01-01T00:00:00Z'}]],
                      'trends': {'minY': {'y': 152, 'x': datetime.datetime(2000, 1, 1, 0, 0, tzinfo=tzutc())},
                                 'maxY': {'y': 185, 'x': datetime.datetime(2002, 1, 1, 0, 0, tzinfo=tzutc())},
                                 'analysis': [{'name': 'dataset'}]},
                      'xLabel': u'X-Label', 'yLabel': u'Y-Label', 'id': 'vis2', 'category': u'STUFF',
                      'name': u'STUFF', 'sourceLink': u'', "datasetName":"dataset", "datasetLink":"http://example.com",
                      'datasetLabels': ["dataset"], 'pk': 2, 'type': u'', 'description':""}]
         self.assertTrue(response.context['category'].name == "STUFF")
         def deep_sort(obj):
            """
            Recursively sort list or dict nested lists
            """

            if isinstance(obj, dict):
                _sorted = {}
                for key in sorted(obj):
                    _sorted[key] = deep_sort(obj[key])

            elif isinstance(obj, list):
                new_list = []
                for val in obj:
                    new_list.append(deep_sort(val))
                _sorted = sorted(new_list)

            else:
                _sorted = obj

            return _sorted
         testDict = deep_sort(testList[0])
         testDict2=deep_sort(response.context['widgets'][0])
         self.assertDictEqual(testDict, testDict2, "getWidget() did not return the correct widget.")

    def test_category_view_less_than_one_category(self):
        response = self.client.get(reverse('category', kwargs={"categoryName" : "NONETest" }))
        self.assertTrue(response.context['error']=="Category 'NONETest' name not found.")

    def test_ajax_GetTrend(self):
        vis1 = Visualisation.objects.get(name='STUFF')
        response = self.client.get(reverse('ajax_getTrend'),{"id": vis1.pk})
        jsonResponse=json.loads(response.content)
        self.assertEqual(jsonResponse["pk"],vis1.pk)

    def test_ajax_getTrend_noID(self):
        vis1 = Visualisation.objects.get(name='STUFF')
        response = self.client.get(reverse('ajax_getTrend'))
        self.assertEqual(response.status_code, 400)









        
        