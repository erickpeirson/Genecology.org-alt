import datetime

from django.test import TestCase, RequestFactory
from texts.models import Text
from browser.views import list_texts, display_text

test_text_uri = 'http://test/testtext1'
test_text_filename = 'texttext.txt'
test_text_title = 'TestText1'
test_date = datetime.date(2013,01,01)
test_text = open('./networks/testdata/testnetwork.xgmml', 'rb').read()

def create_text():
    text = Text(uri=test_text_uri,
                filename=test_text_filename,
                title=test_text_title,
                dateCreated=test_date,
                dateDigitized=test_date,
                content = test_text,
                length = len(test_text))
    text.save()
    return text

class ListTextsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.text = create_text()

    def test_returns_200(self):
        request = self.factory.get('/browser/texts/')
        response = list_texts(request)
        self.assertEqual(response.status_code, 200)

class DisplayTextsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.text = create_text()

    def test_returns_200(self):
        request = self.factory.get('/browser/texts/')
        response = display_text(request, self.text.id)
        self.assertEqual(response.status_code, 200)
                         
                         
