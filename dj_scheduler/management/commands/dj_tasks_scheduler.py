'''
    Author: Ashfaque Alam
    Date: August 29, 2023
    Usage: python manage.py dj_tasks_scheduler
'''

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    '''
        Usage: `python manage.py dj_tasks_scheduler`
    '''
    help = 'Run a script and another management command'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Script executed'))

        try:
            # Deleting older registered tasks from the table `background_task`.
            from background_task.models import Task
            _ = Task.objects.all().delete()

            # Registering new or updated tasks.
            from drf_signal_simplejwt.registered_tasks import registered_tasks
            registered_tasks()

            # Executing (python manage.py process_tasks) to register the tasks in the database and run them.
            call_command('process_tasks')

            self.stdout.write(self.style.SUCCESS('process_tasks command executed'))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Error executing process_tasks command: {e}'))
