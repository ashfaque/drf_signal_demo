import os
from django.conf import settings

def get_directory_path(instance, filename):
    file_extension = os.path.splitext(filename)
    if file_extension[1] in ['.jpg', '.png', '.jpeg']:
        dir = 'images'
    elif file_extension[1] in ['.csv', '.pdf', '.doc', '.docx', '.xlsx', '.xls']:
        dir = 'documents'
    elif file_extension[1] in ['.mp4']:
        dir = 'videos'
    else:
        dir = "others"
    app_name = instance._meta.app_label
    model_name = instance._meta.object_name

    # Fetching current user Roll Number:-
    from users.models import UserDetail
    user_user_type_obj = UserDetail.objects.filter(id=instance.id).order_by('id').last()
    user_user_type = user_user_type_obj.user_type

    path = '{0}/{1}/{2}/{3}/{4}'.format(app_name, model_name, dir, user_user_type, filename)
    return path