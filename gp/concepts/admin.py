from django.contrib import admin
from concepts.models import Concept, ConceptAuthority

class ConceptAdmin(admin.ModelAdmin):
    fields = ['name','type','uri','equalto','similarto','location']
    list_display = ('name','type','uri','location')

class ConceptAuthorityAdmin(admin.ModelAdmin):
    fields = ['name', 'namespace', 'host', 'queryformat', 'retrieveformat', 'selected']
    list_display = ('name', 'namespace', 'host', 'selected')

admin.site.register(Concept, ConceptAdmin)
admin.site.register(ConceptAuthority, ConceptAuthorityAdmin)
