from django.db import models
import uuid
import drf_signal_simplejwt.base_functions as base_f


class QueuePublishHistory(models.Model):
    STATUS_CHOICES = (
                    ('pending', 'pending'),    # Auto requeued.
                    ('published', 'published'),
                    ('error', 'error'),    # Auto requeued.
                    ('expired', 'expired'),    # Auto requeued.
                )
    queue_name = models.TextField(null=True)
    exchange_name = models.TextField(null=True)
    deadletter_queue_name = models.TextField(null=True)
    deadletter_exchange_name = models.TextField(null=True)
    message_body_json = models.JSONField(encoder=base_f.ConvertObjsJSONEncoder, null=True)    # * Use this to save None in JSON: Value(None, JSONField()). This will save null in JSON.
    delivery_mode = models.IntegerField(default=2)
    expiration_secs = models.IntegerField(default=7*24*60*60)    # 604800 secs = 7 days
    message_id = models.UUIDField(default=uuid.uuid4, editable=False)    # * Non-Editable in django forms or django admin.

    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='pending')
    error_msg = models.TextField(default='')

    class Meta:
        db_table = 'queue_publish_history'

    def __str__(self):
        return str(self.message_id)

