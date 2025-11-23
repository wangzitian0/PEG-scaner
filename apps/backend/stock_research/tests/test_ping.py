from django.test import TestCase
from rest_framework.test import APIClient

from stock_research.generated import ping_pb2
from stock_research.models import TrackingRecord


class PingPongViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_ping_returns_pong_payload(self):
        initial_count = TrackingRecord.objects.count()
        response = self.client.get('/api/ping/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/x-protobuf')

        payload = ping_pb2.PingResponse()
        payload.ParseFromString(response.content)
        self.assertEqual(payload.message, 'pong')
        self.assertEqual(payload.agent, 'pegscanner-backend')
        self.assertGreater(payload.timestamp_ms, 0)
        self.assertEqual(TrackingRecord.objects.count(), initial_count + 1)
