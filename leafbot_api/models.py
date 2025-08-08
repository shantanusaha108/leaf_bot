from django.db import models

class ChatLog(models.Model):
    user_text = models.TextField()
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)
    response_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat @ {self.timestamp}"
