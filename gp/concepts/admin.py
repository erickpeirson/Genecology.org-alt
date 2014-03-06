from django.contrib import admin
from concepts.models import Concept, ConceptAuthority, \
                            Location, LocationAuthority

class ConceptAdmin(admin.ModelAdmin):
    fields = ['name','type','uri','equalto','similarto','location']
    list_display = ('name','type','uri','location')

class ConceptAuthorityAdmin(admin.ModelAdmin):
    fields = ['name', 'namespace', 'host', 'queryformat', 'retrieveformat', 'selected']
    list_display = ('name', 'namespace', 'host', 'selected')

class LocationAdmin(admin.ModelAdmin):
    fields = ['name', 'uri', 'longitude', 'latitude']
    list_display = ('name', 'longitude', 'latitude')
    
class LocationAuthorityAdmin(admin.ModelAdmin):
    fields = ['name','namespace', 'host', 'queryformat', 'retrieveformat','id_pattern']
    list_display = ('name','namespace','host')

admin.site.register(Concept, ConceptAdmin)
admin.site.register(ConceptAuthority, ConceptAuthorityAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationAuthority, LocationAuthorityAdmin)