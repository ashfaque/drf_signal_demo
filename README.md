## Features List
- drf
- [SimpleJWT](#simplejwt)
- [Signal](/users/signals.py)
- [Indexing](/users/models.py)
- [Middleware](/drf_signal_simplejwt/middleware.py)
- [django4-background-tasks](#django4-background-tasks)



### Run with
`uvicorn drf_signal_simplejwt.asgi:application --reload --host 0.0.0.0 --port 8000 --workers 9 --use-colors --log-level info`


### SimpleJWT
Location of token_blacklist_outstandingtoken & token_blacklist_blacklistedtoken
```
Under rest_framework_simplejwt -> token_blacklist -> models.py -> OutstandingToken, BlacklistedToken
```
**OutstandingToken**: Saves Refresh Token (`token`) mapped for which `user_id`. Also, `created_at` and `expires_at` datetime is stored. A field named `jti` is also there holding a unique UUID for each token. Which helps track and identify individual tokens during token validation and revocation.

**BlacklistedToken**: Has `token_id` which is a foreign key of OutstandingToken and a `blacklisted_at` datetime field. Whenever a refresh token is blacklisted. It is stored in this table.


### django4-background-tasks

- `pip install django4-background-tasks==1.2.8`, register `background_task` in INSTALLED_APPS also `python manage.py migrate` is needed.
- Create app called [dj_scheduler](/dj_scheduler/), add in INSTALLED_APPS of [settings.py](/drf_signal_simplejwt/settings.py), also create [_\_init__.py](/dj_scheduler/__init__.py) file in it.
- Under [dj_scheduler/management/commands](/dj_scheduler/management/commands/) create a file with any name like [dj_tasks_scheduler.py](/dj_scheduler/management/commands/dj_tasks_scheduler.py), which you can use with `python manage.py dj_tasks_scheduler`.
- Create [tasks.py](/users/tasks.py) file in each app where you want to schedule tasks.
- Register all the tasks in a file called [registered_tasks.py](/drf_signal_simplejwt/registered_tasks.py) in the main app. (This [registered_tasks.py](/drf_signal_simplejwt/registered_tasks.py) file is imported in that [dj_tasks_scheduler.py](/dj_scheduler/management/commands/dj_tasks_scheduler.py) file of [dj_scheduler](/dj_scheduler/) app. Where the `python manage.py process_tasks` command is auto ran at the end to activate and register all the tasks in [registered_tasks.py](/drf_signal_simplejwt/registered_tasks.py) file in the DB table `background_task`.)
- And running `python manage.py dj_tasks_scheduler` will run all the tasks registered in the [registered_tasks.py](/drf_signal_simplejwt/registered_tasks.py) file. (Make a launcher for it.)
- NB: In [dj_tasks_scheduler.py](/dj_scheduler/management/commands/dj_tasks_scheduler.py) file, older tasks are auto deleted form the database and new tasks are added to the database.

* Table: `background_task` contains all the active tasks list.
* Table: `background_task_completedtask` contains all the completed / failed tasks log.
* Model: `Task` can be used with Django ORM to fetch/modify the data in `background_task` table.


### django-auditlog
- add 'auditlog' to your project’s INSTALLED_APPS setting and run `python manage.py migrate`.
```python
# models.py
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
# Add field `history = AuditlogHistoryField()` in a model which needs to be logged.
auditlog.register(ModelName)    # * Register model just below the model definition for audit log. Keep in mind, to only register it once. Else multiple entries will be created in the audit log table.
```
- An entry in the django admin with the name `Log entries` will be auto generated as soon as 'auditlog' was registered in INSTALLED_APPS and migrations were done. Having database table name, `auditlog_logentry`.
```
# Example of using the `history` field in the main model.
MainModel.objects.filter(is_superuser=True).first().history.latest().__dict__
MainModel.objects.filter(is_superuser=True).first().history.all().order_by('-timestamp')
MainModel.objects.filter(is_superuser=True).first().history.latest().changes
MainModel.objects.filter(is_superuser=True).first().history.latest().action    # CREATE = 0, UPDATE = 1, DELETE = 2, ACCESS = 3
MainModel.objects.filter(is_superuser=True).first().history.latest().changes_dict
MainModel.objects.filter(is_superuser=True).first().history.latest().changes_display_dict
MainModel.objects.filter(is_superuser=True).first().history.latest().changes_str
```


### django-user-agents
Register this middleware [APIHitLoggerMiddleware](drf_signal_simplejwt/middleware.py) in [settings.py](drf_signal_simplejwt/settings.py) file.


### SU
```sh
Username: admin
Password: admin
```
