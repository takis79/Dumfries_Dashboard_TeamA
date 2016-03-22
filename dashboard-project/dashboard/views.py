# Python Library Imports
import json

# Django Imports
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q



# Local Imports
from models import Datasource, DashboardDataset, Visualisation, SavedConfig, SavedGraph, Category
from csv_processor import util
from dataset_importer import util as dateutil


def home(request):
    return render(request, "dashboard/index.djhtml")

def graphs(request):
    o = []
    cats = Category.objects.all()
    for cat in cats:
        visNames = Visualisation.objects.filter(category=cat).values_list("pk", "name").order_by("name")
        o.append({"categoryName":cat.name, "visualisations":visNames })
    return render(request, 'dashboard/pages/graphs.djhtml', { "catList":o })

def ajaxGetGraphs(request):
    visualisations = Visualisation.objects.all()
    widgets = [o.getWidget() for o in visualisations]
    return JsonResponse({"widgets": widgets})

def ajaxGetGraph(request):
    if request.GET.get("id") is None:
        return HttpResponse(status=400)
    id = request.GET["id"]
    widget = Visualisation.objects.get(pk=id).getWidget()
    widget["row"] = 0;
    widget["col"] = 0;
    
    return JsonResponse(widget)

def ajaxGetTrend(request):
    if request.GET.get("id") is None:
        return HttpResponse(status=400)
    id = request.GET["id"]
    widget = Visualisation.objects.get(pk=id).getTrendWidget()
    widget["row"] = 0;
    widget["col"] = 0;
    return JsonResponse(widget)

def ajaxSearch(request, searchTerm):
    if searchTerm is not None:
        # Search all datasource, categories, and visualisations.
        ds = Datasource.objects.filter(name__icontains=searchTerm);
        resultsAsVis = Visualisation.objects.filter(Q(dataSource=ds) |
                                                    Q(name__icontains=searchTerm) |
                                                    Q(category__name__icontains=searchTerm))
        
        widgets = [o.getWidget() for o in resultsAsVis]
        return render(request, 'dashboard/pages/searchResults.djhtml', { "searchTerm": searchTerm, "results": widgets, "widgetsJSON": json.dumps(widgets, cls=dateutil.DatetimeEncoder) })
    return render(request, 'dashboard/pages/searchResults.djhtml')

def categoryList(request):
    categories = Category.objects.all()
    return render(request, "dashboard/pages/categoryList.djhtml", {"categories": categories})

def category(request, categoryName):
    category = Category.objects.filter(name__iexact=categoryName)
    categoryVis = Visualisation.objects.filter(category=category)
    widgets = [];
    datasets = DashboardDataset.objects
    for v in categoryVis:
        widget = v.getWidget()
        widget["sizeX"] = v.sizeX
        widget["sizeY"] = v.sizeY
        widget["name"] = v.name
        widget["pk"] = v.pk
        widget["type"] = v.type
        widget["dataset"] = [json.loads(d.dataJSON) for d in datasets.filter(visualisation=v)]
        widget["trends"] = v.calculateTrendData()
        widgets.append(widget)
    
    if category.count() < 1:
        error = "Category '" + categoryName + "' name not found."
    else:
        error = None
        category = category[0]
    return render(request, "dashboard/pages/category.djhtml", {"category": category, "widgets": widgets, "widgetsJSON": json.dumps(widgets, cls=dateutil.DatetimeEncoder), "error": error})

@login_required
def savedConfigs(request):
    configs = SavedConfig.objects.filter(user=request.user)
    return render(request, "dashboard/pages/savedConfigs.djhtml", {"configurations": configs})

@login_required
def saveConfig(request):
    dataJSON = request.POST["data"]
    name = request.POST["name"]
    try:
        data = json.loads(dataJSON)
    except:
        return JsonResponse({'message':"Failed to add new Saved Config incorrect data format",'success':False})
    if name =='':
        return JsonResponse({'message':"Failed to add new Saved Config name must be specified",'success':False})
    savedConfig = SavedConfig.objects.create(user=request.user, name=name)
    savedConfig.save()
    for graph in data:
        vis = Visualisation.objects.filter(id=graph["visPK"])[0]
        
        savedGraph = SavedGraph.objects.create(visualisation=vis, 
                                               savedConfig=savedConfig, 
                                               isTrendWidget = graph["isTrendWidget"],
                                               xPosition=graph["xPosition"], 
                                               yPosition=graph["yPosition"], 
                                               sizeX=graph["sizeX"], 
                                               sizeY=graph["sizeY"])
        savedGraph.save()
    return JsonResponse({'message':'Added new Saved Configuration.', "success": True})
@login_required
def ajaxloadSavedConfig(request):
    scid = request.POST["id"]
    savedConfig = SavedConfig.objects.filter(id=scid)[0]
    savedGraphs = SavedGraph.objects.filter(savedConfig=savedConfig).select_related("visualisation")
    if savedConfig.user != request.user:
        return JsonResponse({'message':'Error: This Saved Configuration does not belong to you.', "success": False})
    
    widgets = [];
    datasets = DashboardDataset.objects
    for graph in savedGraphs:
        vis = graph.visualisation
        widget = vis.getWidget()
        widget["row"] = graph.yPosition
        widget["col"] = graph.xPosition
        widget["sizeX"] = graph.sizeX
        widget["sizeY"] = graph.sizeY
        widget["name"] = vis.name
        widget["id"] = "vis" + str(vis.pk)
        widget["pk"] = vis.pk
        widget["type"] = vis.type
        if graph.isTrendWidget:
            widget["trends"] = vis.calculateTrendData()
            del widget["dataset"]
        widgets.append(widget)
    return JsonResponse({"widgets": widgets})
@login_required
def ajaxDeleteSavedConfig(request):
    scid = request.POST["id"]
    savedConfig = SavedConfig.objects.filter(id=scid)[0]
    savedGraphs = SavedGraph.objects.filter(savedConfig=savedConfig).select_related("user")
    if savedConfig.user != request.user:
        return JsonResponse({'message':'Error: This Saved Configuration does not belong to you.', "success": False})
    savedGraphs.delete()
    savedConfig.delete()
    return JsonResponse({'message':'Deleted Saved Configuration.', "success": True})

def loginPage(request):
    return render(request, "dashboard/pages/login.djhtml")

def ajax_login(request):
    username = request.POST.get('email', "")
    password = request.POST.get('password', "")
    user = authenticate(username=username, password=password)
    if request.POST.get("remember", None) is None:
        request.session.set_expiry(0)
    if user is not None:
        if user.is_active:
            login(request, user)
            return JsonResponse({'message':'Successfully logged in.', "success": True})
        else:
            return JsonResponse({'message':'Error: Account disabled.', "success": False})
    else:
        return JsonResponse({'message':'Error: Invalid login details.', "success": False})

def ajax_isAuthenticated(request):
    return JsonResponse({"is_authenticated": request.user.is_authenticated()})

def logoutUser(request):
    logout(request)
    # Redirect to a success page.
    return redirect("/")

def ajax_register(request):
    username = request.POST['email']
    password = request.POST['password']
    repeatPass = request.POST['repeatPass']
    if User.objects.filter(username=username).exists():
        return JsonResponse({'message':'Error: Email address already used.', 'success': False})
    if password=='':
        return JsonResponse({'message':'Error: Password must be set.', 'success': False})
    if username=='':
        return JsonResponse({'message':'Error: Email address must be set.', 'success': False})
    if password != repeatPass:
        return JsonResponse({'message':'Error: Passwords do not match.', 'success': False})
    else:
        user = User.objects.create_user(username, username, password)
        user.save()
        user = authenticate(username=username, password=password)
        login(request,user)
    return JsonResponse({'message':'Successfully registered. You will now be logged in.', "success": True})

def registrationPage(request):
    return render(request, "dashboard/pages/register.djhtml")
