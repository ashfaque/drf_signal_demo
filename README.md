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


### django-ipware
```python
from ipware import get_client_ip
local_ip, _ = get_client_ip(request)
```


### Sync User Creation / Updation from this project & it will be auto reflected in the [drf_RabbitMQ_2_proj_sync](https://github.com/ashfaque/drf_RabbitMQ_2_proj_sync) project.
- `pip install --no-cache-dir pika==1.3.2`
- Create an app called [pubsub](pubsub/).
- Register the newly created app in [settings.py](drf_signal_simplejwt/settings.py#INSTALLED_APPS) & [urls.py](drf_signal_simplejwt/urls.py#L26) of main app.
- Write the RabbitMQ server configurations in [settings.py](drf_signal_simplejwt/settings.py#RABBITMQ) and also in [.env](.env#RABBITMQ) file.
- Create model [QueuePublishHistory](pubsub/models.py) in pubsub app to save the queue publish history in RabbitMQ.
- Create calss [ConvertObjsJSONEncoder](drf_signal_simplejwt/base_functions.py) in `base_function.py` of main app to convert python objects to json serializable.
- In [utils.py](pubsub/utils.py) of pubsub app, create a funciton `queue_msg_to_publish` which will save the data in `QueuePublishHistory` model.
- Now create a [signal.py](users/signals.py) file in users app and create a signal so that whenever a user instance is either created or updated a signal is fired in post_save method and a log is saved in the `QueuePublishHistory` model using the `queue_msg_to_publish` function.
- Now create the [producer_service.py](producer_service.py) file in the project main dir, keep it running in the background in a new instance.
    + Have auto reconnection logic for both RabbitMQ and MySQL server if connection is lost.
    + Have transactions for both RabbitMQ and MySQL.
    + It will fetch all the rows in the `QueuePublishHistory` model, having status `('pending', 'error', 'expired')`.
    + Then it will publish the message in their specified queue in the RabbitMQ queue as per the data in the model `QueuePublishHistory`.
    + And then updates the status to `published` or `error` according to the situation.
    + Auto logs in a `.log` file inside the [logs](logs/producer_service.log) dir.
- Create a [deadletter_consumer.py](deadletter_consumer.py) file in the project main dir, keep it running in the background in a new instance.
    + `NB: RESTART THIS SCRIPT IF MYSQL CONNECTION WAS TEMPORARILY DOWN. OTHERWISE, IT WILL NOT BE ABLE TO FETCH THE QUEUE NAMES FROM THE DB.`
    + Fetches the list of all the deadletter queue names from the model `QueuePublishHistory`.
    + Have auto reconnection logic for RabbitMQ server if connection is lost.
    + Consumes all the deadletter queues at once and consumes from all of them.
    + After consuming the message it finds the message in the model `QueuePublishHistory` and updates its status to `'expired'`.
- In another project, [drf_RabbitMQ_2_proj_sync](https://github.com/ashfaque/drf_RabbitMQ_2_proj_sync)
    + A model is created with the name [ConflictingUserSyncLog](https://github.com/ashfaque/drf_RabbitMQ_2_proj_sync/blob/main/users/models.py), to save the message having some conflicts.
    + A [user_sync_consumer.py](https://github.com/ashfaque/drf_RabbitMQ_2_proj_sync/blob/main/user_sync_consumer.py) is ran.
    + It also have the RabbitMQ reconnection logic written due to connection lost.
    + It consumes from all the specified [QUEUE_NAMES_DEADLETTER_EXCHANGE_MAPPING](https://github.com/ashfaque/drf_RabbitMQ_2_proj_sync/blob/5453b4213d9677af9c942a4eb634193883655d03/user_sync_consumer.py#L35C30-L35C30) dict.
    + After receiving the message it converts the json to python dict.
    + It then checks if user was created / updated. According to that, it either creates the user or updates the user.
    + And if any conflicts arises, like username already exists, then it saves the message along with other details in a model [ConflictingUserSyncLog](https://github.com/ashfaque/drf_RabbitMQ_2_proj_sync/blob/main/users/models.py).


### SU
```sh
Username: admin
Password: admin
```
