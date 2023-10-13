from .models import QueuePublishHistory


def queue_msg_to_publish(
        queue_name: str = None
        , exchange_name: str = None
        , deadletter_queue_name: str = None
        , deadletter_exchange_name: str = None
        , message_body_json: dict = None
        , delivery_mode: int = None
        , expiration_secs: int = None
) -> bool:
    # try:
        create_kwargs = {}
        if delivery_mode:
            create_kwargs['delivery_mode'] = delivery_mode
        if expiration_secs:
            create_kwargs['expiration_secs'] = expiration_secs

        _ = QueuePublishHistory.objects.create(
                                        queue_name=queue_name
                                        , exchange_name=exchange_name
                                        , deadletter_queue_name=deadletter_queue_name
                                        , deadletter_exchange_name=deadletter_exchange_name
                                        , message_body_json=message_body_json
                                        , **create_kwargs
                                    )
        return True
    # except Exception as e:
    #     # print(e)
    #     return False
