"""
Specifies how the admin interface for csv processor models
should work and look.
"""

from django.contrib import admin
from models import CsvFile, Dimension

class DimensionInline(admin.StackedInline):
    """
    Allows Dimension form to be inlined on the CsvFile admin form
    """
    model = Dimension
    extra = 1
    
class DimensionAdmin(admin.ModelAdmin):
    """
    Defines the admin interface for Dimension model.
    """
    list_display = ['label', 'type', 'csvFile']
    
    def save_related(self, request, form, formsets, change):
        obj = form.instance
        obj.save()
        super(CsvFileAdmin, self).save_related(request, form, formsets, change)
    
class CsvFileAdmin(admin.ModelAdmin):
    """
    Defines the admin interface for CsvFile model.
    """
    list_display = ['name']
    inlines = [ DimensionInline ]
    
    def save_related(self, request, form, formsets, change):
        obj = form.instance
        super(CsvFileAdmin, self).save_related(request, form, formsets, change)
        obj.createDashboardInfo()
    
    def save_model(self, request, obj, form, change):
        admin.ModelAdmin.save_model(self, request, obj, form, change)
    

admin.site.register(CsvFile, CsvFileAdmin)
admin.site.register(Dimension, DimensionAdmin)