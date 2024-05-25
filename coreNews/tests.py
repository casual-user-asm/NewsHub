from django.test import TestCase
from .models import News
from django.urls import reverse


class NewsTestCase(TestCase):
    def setUp(self):
        News.objects.create(publisher='TestPub', url='www.test.com', title='The Great Test', short_text='TGT')

    def test_model_creation(self):
        obj = News.objects.get(publisher='TestPub')
        self.assertEqual(obj.url, 'www.test.com')
        self.assertEqual(obj.title, 'The Great Test')
        self.assertEqual(obj.short_text, 'TGT')

    def test_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        item_arg = 'Test'
        url = reverse('detail', kwargs={'item': item_arg})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
