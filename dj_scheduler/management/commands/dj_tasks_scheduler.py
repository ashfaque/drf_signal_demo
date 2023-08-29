# from users.tasks import test_task
# test_task(repeat=5) # Repeat every 24 hours


from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run a script and another management command'

    def handle(self, *args, **options):
        # Your script logic here
        self.stdout.write(self.style.SUCCESS('Script executed'))

        # Run another management command
        try:
            from background_task.models import Task
            _ = Task.objects.all().delete()
            # ! delete all older tasks here, also import tasks files from all apps here and run from here with, `python manage.py schedulers`
            # ! better pick all the registered tasks from a file called, registered_tasks from main_app and run them here by importing.
            from drf_signal_simplejwt.registered_tasks import registered_tasks
            registered_tasks()
            call_command('process_tasks')    # This command (python manage.py process_tasks) will be executed after the script has finished.
            self.stdout.write(self.style.SUCCESS('process_tasks command executed'))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Error executing process_tasks command: {e}'))
