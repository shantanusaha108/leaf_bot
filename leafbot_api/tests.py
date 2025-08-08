from django.test import TestCase
from .models import ChatLog

class ChatLogModelTest(TestCase):
    def test_create_log(self):
        log = ChatLog.objects.create(user_text="Test", response_text="Response")
        self.assertEqual(str(log), f"Chat @ {log.timestamp}")
