from django.test import TestCase
from django.urls import reverse

from .models import Server


class TrackerTests (TestCase):

    def test_tracker_listing(self):
        url = reverse('api-v1-tracker')
        data = {
            'players': ['Vertigo', 'silverfox', 'povertio', 'croc'],
            'description': 'Welcome to Avara!',
        }
        r = self.client.post(url, data, content_type='application/json', REMOTE_ADDR='24.3.3.11')
        self.assertEqual(r.status_code, 200)
        posted = r.json()
        for key in data:
            self.assertEqual(data[key], posted[key])
        self.assertEqual(posted['address'], '24.3.3.11')
        self.assertEqual(posted['port'], 19567)
        self.assertEqual(Server.objects.count(), 1)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        servers = r.json()['servers']
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0], Server.objects.get().to_dict())
