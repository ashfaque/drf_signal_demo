from django.contrib import admin
from .models import QueuePublishHistory    #, ExpiredRejectedLog


@admin.register(QueuePublishHistory)
class QueuePublishHistory(admin.ModelAdmin):
    list_display = [field.name for field in QueuePublishHistory._meta.fields]
    search_fields = ('queue_name', 'exchange_name', 'deadletter_queue_name', 'deadletter_exchange_name', 'status', 'message_id', 'error_msg')
    readonly_fields = ['message_id', 'timestamp']

