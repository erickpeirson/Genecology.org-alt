from django.contrib import admin, messages
from concepts.models import Concept, ConceptAuthority, ConceptType, \
                            Location, LocationAuthority
from concepts.forms import AddConceptForm
from concepts.managers import retrieve_concept
from texts.models import Text

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')



class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name','type','uri','location')
    
    def get_form(self, request, obj=None, **kwargs):
        """
        If creating an object (rather than editing), provide a custom form
        asking only for a URI and ConceptAuthority.
        """
        if obj is None:
            return AddConceptForm
        else:
            fields = ['name','type','uri','equalto','similarto','location']
            return super(ConceptAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Concepts are added from a known ConceptAuthority.
        """

        if change:  # Use built-in save_model when editing Concepts.
            return super(ConceptAdmin, self) \
                                         .save_model(request, obj, form, change)
        else:       # Retrieve the concept by URI from a ConceptAuthority.
            uri = form.cleaned_data['uri']
            try:
                concept = retrieve_concept(uri)
                
                logging.debug("Concept with uri {0} retrieved".format(uri))
                message = "Concept {0} retrieved successfully." \
                                                           .format(concept.name)
                self.message_user(request, message, level=messages.SUCCESS)
            except ValueError:
                logging.debug("Concept with uri {0} not found".format(uri))
                message = "No such concept in selected ConceptAuthority"
                self.message_user(request, message, level=messages.ERROR)
            except RuntimeError:
                logging.debug("No valid ConceptAuthority.")
                message = "No valid ConceptAuthority available."
                self.message_user(request, message, level=messages.ERROR)

    def response_add(self, request, obj, post_url_continue=None):
        """
        To avoid extraneous Success message.
        """
        
        return self.response_post_save_add(request, obj)

class ConceptAuthorityAdmin(admin.ModelAdmin):
    fields = ['name', 'namespace', 'host', 'queryformat', 'retrieveformat']
    list_display = ('name', 'namespace', 'host')

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

admin.site.register(ConceptType)