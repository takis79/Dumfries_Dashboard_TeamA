from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.home', name='home'),
    url(r'^pages/home', 'dashboard.views.graphs', name='graphs'),
    url(r'^pages/category/(?P<categoryName>.*)', 'dashboard.views.category', name='category'),
    url(r'^pages/category$', 'dashboard.views.categoryList', name='categoryList'),
    url(r'^pages/savedConfigs', 'dashboard.views.savedConfigs', name='savedConfigs'),
    url(r'^pages/login', 'dashboard.views.loginPage', name='login'),
    url(r'^pages/register', 'dashboard.views.registrationPage', name='register'),
    url(r'^pages/searchResult/(?P<searchTerm>.*)', 'dashboard.views.ajaxSearch', name='search'),
    url(r'^saveConfig', 'dashboard.views.saveConfig', name='saveConfig'),
    url(r'^deleteSavedConfig', 'dashboard.views.ajaxDeleteSavedConfig', name='ajax_deleteSavedConfig'),
    url(r'^loadSavedConfig', 'dashboard.views.ajaxloadSavedConfig', name='ajax_loadSavedConfig'),
    url(r'^getGraphs', 'dashboard.views.ajaxGetGraphs', name='ajax_getGraphs'),
    url(r'^getGraph', 'dashboard.views.ajaxGetGraph', name='ajax_getGraph'),
    url(r'^getTrend', 'dashboard.views.ajaxGetTrend', name='ajax_getTrend'),
    url(r'^logout', 'dashboard.views.logoutUser', name='logout'),
    url(r'^account/checkAuthenticated', 'dashboard.views.ajax_isAuthenticated', name='ajax_checkAuthenticated'),
    url(r'^account/login', 'dashboard.views.ajax_login', name='ajax_login'),
    url(r'^account/register', 'dashboard.views.ajax_register', name='ajax_register'),
    
    url(r'^pages/help', TemplateView.as_view(template_name="dashboard/docs/public/index.djhtml"), name='docs_index'),
    
    url(r'^admin/help/csvprocessor', TemplateView.as_view(template_name="dashboard/docs/admin/csvprocessor.djhtml"), name='admin_docs_csvprocessor'),
    url(r'^admin/help/dashboard', TemplateView.as_view(template_name="dashboard/docs/admin/dashboard.djhtml"), name='admin_docs_csvprocessor'),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
