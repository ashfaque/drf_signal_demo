from copy import deepcopy
from pprint import pprint
from django.conf import settings
from django.db import transaction
from django.db.models.signals import (
    pre_save          # ? Before saving a model instance (create/update).
    , post_save       # ? After saving a model instance (create/update).
    , pre_delete      # ? Before deleting a model instance.
    , post_delete     # ? After deleting a model instance.
    , pre_migrate     # ? Before applying a migration.
    , post_migrate    # ? After applying a migration.
    , pre_init        # ? Before initializing a model instance. This signal is sent at the beginning of the __init__ method of a model.
    , post_init       # ? After initializing a model instance.This signal is sent at the beginning of the __init__ method of a model.
    , m2m_changed     # ? This signal is sent when a ManyToMany relationship is changed (added/removed).
    , class_prepared  # ? This signal is sent when a model's class is prepared by Django.
)
from django.dispatch import receiver
from .models import UserDetail, UserLog
from pubsub.utils import queue_msg_to_publish


# ! Signal (3/3) - Add this funciton. This function will be called when a UserDetail instance is created


@receiver(post_save, sender=UserDetail)
def create_entry_queue_publish_history_user_post_creation(sender, instance, created, **kwargs):
    '''
    sender: <class 'users.models.UserDetail'>
    instance: <UserDetail: UserDetail object (1)>
    created: True
    kwargs: {'signal': <django.db.models.signals.ModelSignal object at 0x0000012345678950>, 'update_fields': None, 'raw': False, 'using': 'default'}
    '''

    copied_user_instance_dict: dict = deepcopy(instance.__dict__)
    copied_user_instance_dict.pop('_state', None)
    copied_user_instance_dict.pop('_django_version', None)

    if created:    # ? User is created.
        # If a new UserDetail instance is created, create a new Log instance
        copied_user_instance_dict.update(is_created=True)
    else:          # ? User is updated.
        copied_user_instance_dict.update(is_created=False)

    with transaction.atomic():
        status: bool = queue_msg_to_publish(
                                queue_name=settings.RABBITMQ['USER_SYNC_QUEUE_NAME']
                                , exchange_name=settings.RABBITMQ['USER_SYNC_EXCHANGE_NAME']
                                , deadletter_queue_name=settings.RABBITMQ['USER_SYNC_QUEUE_NAME'] + '_DLQ'
                                , deadletter_exchange_name=settings.RABBITMQ['USER_SYNC_EXCHANGE_NAME'] + '_DLX'
                                , message_body_json=copied_user_instance_dict
                                # , expiration_secs=10    # * For testing purpose only.
                    )


"""

@receiver(pre_save, sender=UserDetail)
def create_log_on_user_pre_creation(sender, instance, **kwargs):
    # if not instance.pk:
    if instance._state.adding:    # ? User is being created.
        print("Pre-Save Signal: User is being created.")
    else:                         # ? User is being updated.
        print("Pre-Save Signal: User is being updated.")


@receiver(post_save, sender=UserDetail)
def create_log_on_user_post_creation(sender, instance, created, **kwargs):
    '''
    sender: <class 'users.models.UserDetail'>
    instance: <UserDetail: UserDetail object (1)>
    created: True
    kwargs: {'signal': <django.db.models.signals.ModelSignal object at 0x0000012345678950>, 'update_fields': None, 'raw': False, 'using': 'default'}
    '''
    if created:    # ? User is created.
        # If a new UserDetail instance is created, create a new Log instance
        UserLog.objects.create(user_details=instance, comment='New user Created')
    else:          # ? User is updated.
        UserLog.objects.filter(user_details=instance).update(comment='User Updated')


# pre_delete signal
@receiver(pre_delete, sender=UserDetail)
def pre_delete_user(sender, instance, **kwargs):
    print("Pre-Delete Signal: User instance is about to be deleted.")


# post_delete signal
@receiver(post_delete, sender=UserDetail)
def post_delete_user(sender, instance, **kwargs):
    print("Post-Delete Signal: User instance has been deleted.")


# pre_migrate signal
@receiver(pre_migrate)
def pre_migrate_handler(app_config, **kwargs):
    '''
    Use case: The pre_migrate signal is triggered just before the migration process starts. 
    It allows you to perform certain tasks or configurations that need to be done before any 
    migrations are applied. For example, you might use this signal to create temporary tables 
    or perform data backups before the migration begins.
        Note that pre_migrate is executed once per application, and it is triggered only once when 
        all migrations for that application are about to be applied. This makes it suitable for tasks 
        that should happen at the beginning of the migration process, regardless of the specific 
        migration being applied.
    '''
    print(f"Pre-Migrate Signal: Migrating app '{app_config.name}'.")


# post_migrate signal
@receiver(post_migrate)
def post_migrate_handler(app_config, **kwargs):
    '''
    Use case: The post_migrate signal is triggered after all migrations have been applied successfully. 
    It provides an opportunity to execute code that depends on the successful completion of migrations. 
    For example, you might use this signal to create default data, update schema-related information, 
    or trigger other actions that rely on the updated database schema.
        Similar to pre_migrate, post_migrate is executed once per application after all migrations 
        are applied. It's an appropriate place to perform actions that should happen at the end of the 
        migration process.
    '''
    print(f"Post-Migrate Signal: Migration completed for app '{app_config.name}'.")

"""

# #####################################################################################################
# ################################### LESS COMMONLY USED SIGNALS ######################################
# #####################################################################################################
"""

# pre_init signal
@receiver(pre_init, sender=UserDetail)
def pre_init_user(sender, instance, **kwargs):
    '''
    Use case: These signals are rarely used in practice, as most of the initialization logic 
    can be handled within the __init__ method of the model itself. However, in some rare situations, 
    you might want to perform some additional actions or validations before or after the model is 
    initialized. For example, you could use these signals to set default values for certain fields 
    or perform complex data validations when creating a new instance of the model.
    '''
    print("Pre-Init Signal: Initializing a User instance.")

# post_init signal
@receiver(post_init, sender=UserDetail)
def post_init_user(sender, instance, **kwargs):
    print("Post-Init Signal: User instance initialized.")

# m2m_changed signal
@receiver(m2m_changed, sender=UserDetail.class_teacher.through)
def m2m_changed_class_teacher(sender, instance, action, reverse, model, pk_set, **kwargs):
    '''
    Use case: This signal is particularly useful when you have a ManyToMany relationship between models 
    and you want to be notified when the relationship changes. For example, you might have a model 
    representing a playlist and another model representing songs. When a song is added or removed 
    from a playlist, you can use the m2m_changed signal to update some other related data or trigger 
    additional actions.
    '''
    print(f"M2M-Changed Signal: Class teachers changed for User {instance}.")

# class_prepared signal
@receiver(class_prepared)
def class_prepared_handler(sender, **kwargs):
    '''
    Use case: The class_prepared signal is not commonly used in typical application development. 
    It might be more relevant in advanced scenarios where you need to perform some global setup 
    or configuration based on the models present in your application. For example, you could use 
    this signal to dynamically modify the behavior of model fields or relations based on specific 
    conditions.
    '''
    print(f"Class-Prepared Signal: Model class '{sender.__name__}' prepared.")



"""

# #####################################################################################################

"""
# Signal to save log in a table.

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction
from .models import TMasterSubscriptionCompanyMapping, TMasterSubscriptionCompanyMappingHistory

'''
Author: Ashfaque Alam
Date: August 21, 2023
Purpose: Logging older data of TMasterSubscriptionCompanyMapping before updating.
'''
@receiver(pre_save, sender=TMasterSubscriptionCompanyMapping)
def create_log_on_user_pre_creation(sender, instance, **kwargs):
    with transaction.atomic():
        if not instance._state.adding:
            original_instance = TMasterSubscriptionCompanyMapping.objects.get(pk=instance.pk)
            # [original_instance.__dict__.pop(attr, None) for attr in ['_state', 'id']]
            remove_attrs = lambda instance, attrs: [instance.__dict__.pop(attr, None) for attr in attrs]
            remove_attrs(original_instance, ['_state', 'id'])
            _ = TMasterSubscriptionCompanyMappingHistory.objects.create(**original_instance.__dict__)


# In models.py
'''
    Author: Ashfaque Alam
    Date: August 16, 2023
    Purpose: Tagging company with subscriptions.
    NB: Whatever updation made in this table, the older data will be logged in a separate table.
'''
class TMasterSubscriptionCompanyMappingAbstract(models.Model):
    company = models.ForeignKey(TCoreCompany, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related_company')    # ? [MANDATORY] Only one company_id will be stored in this table when tagged with any subscription_id.
    subscription = models.ForeignKey(TCoreSubscription, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related_subscription')    # ? [MANDATORY] Same subscription_id can be tagged with multiple company_ids.
    users_limit = models.IntegerField(default=0)    # 0 means unlimited
    active_inactive_date = models.DateTimeField(blank=True, null=True)    # If subscription is mapped with a company for the first time, this will be null, but if `is_active` status is changed. Then that date will be inserted here.
    is_active = models.BooleanField(default=True)    # * If this field is false then the subscription/trial/grace time is expired. Otherwise if this field is true, and null in other datetime fields, then the subscription will be forever.
    active_inactive_reason = models.TextField(blank=True, null=True)

    subscription_valid_from = models.DateTimeField(blank=True, null=True)
    subscription_valid_until = models.DateTimeField(blank=True, null=True)
    grace_end_date = models.DateTimeField(blank=True, null=True)    # * If this field is `null` then no grace time is given. Also the `subscription_valid_until` will be treated as 'grace start date'.

    is_trial = models.BooleanField(default=False)
    trial_start_date = models.DateTimeField(blank=True, null=True)
    trial_end_date = models.DateTimeField(blank=True, null=True)

    is_cancelled = models.BooleanField(default=False)
    cancellation_status_change_date = models.DateTimeField(blank=True, null=True)
    cancellation_status_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related_created_by', blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_related_updated_by', blank=True, null=True)

    mac_address = models.TextField(blank=True, null=True)
    internal_ip_address = models.TextField(blank=True, null=True)
    external_ip_address = models.TextField(blank=True, null=True)

    # is_deleted = models.BooleanField(default=False)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msc_deleted_by', blank=True, null=True)

    class Meta:
        abstract = True


class TMasterSubscriptionCompanyMapping(TMasterSubscriptionCompanyMappingAbstract):

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('subscription', 'company')    # Combination of data stored in fields `subscription` and `company` will be unique.
        db_table = 't_master_subscription_company_mapping'


class TMasterSubscriptionCompanyMappingHistory(TMasterSubscriptionCompanyMappingAbstract):

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 't_master_subscription_company_mapping_history'

"""
