from django.contrib import admin
from locations.models import Location, LocationAuthority


class LocationAdmin(admin.ModelAdmin):
    fields = ['name', 'uri', 'longitude', 'latitude']
    list_display = ('name', 'longitude', 'latitude')
    
class LocationAuthorityAdmin(admin.ModelAdmin):
    fields = ['name','namespace', 'host', 'queryformat', 'retrieveformat']
    list_display = ('name','namespace','host')
    
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationAuthority, LocationAuthorityAdmin)