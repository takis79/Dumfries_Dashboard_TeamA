from django.contrib import admin
from models import LinkedDataAPIEndpoint

class LinkedDataAPIEndpointAdmin(admin.ModelAdmin):
    list_display = LinkedDataAPIEndpoint._meta.get_all_field_names()

admin.site.register(LinkedDataAPIEndpoint, LinkedDataAPIEndpointAdmin)