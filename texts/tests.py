"""
Tests for Texts app.
"""

from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.http import HttpResponse, HttpRequest, Http404
from django.core.files.uploadedfile import UploadedFile
from django.db import IntegrityError
from texts.admin import TextAdmin
from texts.models import Text
from concepts.models import Concept
from texts.forms import get_text_form_list, AddTextForm
import autocomplete_light
autocomplete_light.autodiscover()

from forms import TextFormBase

def create_concept():
    concept = Concept(  name = 'namestring',
                        uri = 'uristring',
                        type = 'E21 Person'   )
    concept.save()
    return concept

add_path = '/admin/texts/text/add/'

class TestTextFormWizard(TestCase):
    """
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/admin/texts/text/add/')
        self.client = Client()

    def test_get_first_step(self):
        response = self.client.get(add_path)
        self.assertEqual(response.status_code, 200)

    def test_post_first_step(self):
        valid_data = {  'text_wizard-current_step': 0,
                        '0-method': 'local' }
        response = self.client.post(add_path, valid_data)
        self.assertEqual(response.status_code, 200)
        
        observed_error = response.context['form']._errors
        expected_error = {}
        self.assertEqual(expected_error, observed_error)

    def test_post_first_step_invalid(self):
        """
        method field is required
        """
        invalid_data = {  'text_wizard-current_step': 0 }
        response = self.client.post(add_path, invalid_data)
        self.assertEqual(response.status_code, 200)

        observed_error = response.context['form']._errors
        expected_error = {'method': ['This field is required.']}
        self.assertEqual(expected_error, observed_error)

    def test_post_second_step_local(self):
       with open('./texts/test_input/test_upload.txt','rb') as file:
            uf = UploadedFile(file=file,
                              name='namestring')
                              
            valid_data = {      '4-uri':            'uristring',
                                '4-dateCreated':    '2013-01-02',
                                '4-dateDigitized':  '2013-01-02',
                                '4-title':          'stringtitle',
                                '4-upload':         file,
                                '4-creator':        [create_concept().id],
                                '0-method':         'local',
                                'text_wizard-current_step': 4   }
            response = self.client.post(add_path, valid_data)
            print response

            observed_error = response.context['form']._errors
            expected_error = {}
            self.assertEqual(expected_error, observed_error)

    def test_post_second_step_local_invalid(self):
       with open('./texts/test_input/test_upload.txt','rb') as file:
            uf = UploadedFile(file=file,
                              name='namestring')
                              
            valid_data = {      '1-uri':            'uristring',

                                '0-method':         'local',
                                'text_wizard-current_step': 4   }
            response = self.client.post(add_path, valid_data)
            observed_error = response.context['form']._errors
            expected_error = {}
            self.assertEqual(expected_error, observed_error)

#        text_admin = TextAdmin(Text, self.request)
#        print text_admin.__dict__
#        print retrieve(self.request, '')

#class TestAddTextForm(TestCase):
#    def setUp(self):
#        self.AddTextForm = AddTextForm
#
#    def test_valid(self):
#
#        with open('./texts/test_input/test_upload.txt','rb') as file:
#            uf = UploadedFile(file=file,
#                              name='namestring')
#            valid_data = {      'uri':  'uristring',
#                                'dateCreated':  '2013-01-02',
#                                'dateDigitized':    '2013-01-02',
#                                'title':    'stringtitle',
#                                'upload': 'asdf.txt',
#                                'creator': [create_concept().id] }
#            
##            print type(uf)
##    
#            print self.AddTextForm(data=valid_data).is_valid()
#            print self.AddTextForm(data=valid_data).errors
