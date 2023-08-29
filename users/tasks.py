# ? User can create tasks.py file per app. Then register their tasks in a file called registered_tasks.py in the main app. And running `python manage.py dj_tasks_scheduler` will run all the tasks registered in the registered_tasks.py file.
# https://github.com/arteria/django-background-tasks/tree/master/background_task

from datetime import datetime
from django.utils import timezone
from background_task import background
from background_task.models import Task

# def get_caller_task_name():
#     from django.apps import apps
#     import os
#     import inspect

#     # current_app_name = apps.get_containing_app_config(__name__).name    # Get the current app's name dynamically
#     # current_file_name = os.path.splitext(os.path.basename(__file__))[0]    # Get the current file's name dynamically
#     # current_function_name = inspect.currentframe().f_code.co_name    # Get the current function's name dynamically
#     # formatted_result = f"{current_app_name}.{current_file_name}.{current_function_name}"    # Combine the parts to create the desired format

#     calling_frame = inspect.currentframe().f_back    # Get the calling frame
#     caller_app_name = apps.get_containing_app_config(calling_frame.f_globals['__name__']).name    # Get the app name of the calling function
#     caller_file_name = os.path.splitext(os.path.basename(calling_frame.f_globals['__file__']))[0]    # Get the file name of the calling function without extension
#     caller_function_name = calling_frame.f_code.co_name    # # Get the calling function's name
#     formatted_result = f"{caller_app_name}.{caller_file_name}.{caller_function_name}"    # Combine the parts to create the desired format

#     return formatted_result


# @background(schedule=timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0))
# @background(schedule=5)
@background(schedule=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0))
def test_task():
    # _ = Task.objects.filter(task_name=get_caller_task_name()).delete()
    # _ = Task.objects.filter(task_name=get_caller_task_name()).exclude(id=Task.objects.filter(task_name=get_caller_task_name()).latest('id').id).delete()

    # print(_)

    today = datetime.utcnow()
    print('Today ---> ', today)

# test_task(repeat=24*60*60)
# test_task(repeat=10)
# test_task.schedule(repeat=Task.DAILY, time=datetime.time(hour=8, minute=0))
