from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message

@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a message is saved.
    Sends the message to the user's WebSocket channel.
    """
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.session.user.id}",
            {
                "type": "chat_message",
                "message": {
                    "content": instance.content,
                    "is_from_user": instance.is_from_user,
                    "created_at": instance.created_at.isoformat()
                }
            }
        ) 