''' Author: Ashfaque Alam
    Date: August 29, 2023
    Purpose: # ? Register all the tasks from different apps here
    Usage: Run this command after modifying this file, `python manage.py dj_tasks_scheduler`
    NB: # ? After running this command, all the tasks will run once instantly. After that it will run after the interval specified.
'''

from django.utils import timezone
import datetime
from datetime import timedelta
from background_task.models import Task

# Import the tasks functions here and register them in the function registered_tasks().
from users.tasks import test_task


def registered_tasks():
    # * Please Note: From today midnight i.e., 00:00:00 onwards we can schedule tasks. For example, Let say today is August 1, 2023. Then we can schedule tasks from Augusst 2, 2023 00:00:00 onwards.
    # ? The following constants are provided for `repeat`: Task.NEVER (default), Task.HOURLY, Task.DAILY, Task.WEEKLY, Task.EVERY_2_WEEKS, Task.EVERY_4_WEEKS.
    midnight_time = timezone.now() + timezone.timedelta(days=1)    # Adding one day from today is important because if we don't d this, the task will run as soon as it is registered in the database. Let say, a task is for firing emails to users at 9pm, but it is registered at 6 pm then those emails will be fored at 6 pm when it was registered and at 9 pm as well. To avoid this we are adding 1 day to stop the instant trigger of task when registering.

    # test_task(repeat=10)
    test_task(schedule=midnight_time.replace(hour=0, minute=0, second=0, microsecond=0), repeat=Task.DAILY)    # Runs daily at 00:00:00.

