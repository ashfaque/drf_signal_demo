To implement the logic of uploading a video file, giving an immediate response, and processing the video in the background in a Django REST Framework (DRF) backend, we can use a task queue like Celery. Celery allows us to handle background tasks efficiently.

Here's a step-by-step guide to achieve this:

1. **Set Up Celery in Django**:
   - Install Celery and a message broker like Redis.
   - Configure Celery in your Django project.

2. **Create a Django Model for Video Uploads**:
   - Create a model to store information about uploaded videos and their processing status.

3. **Create a Django REST Framework API for Video Upload**:
   - Create an API endpoint to handle video uploads.
   - Use a serializer to validate the video file.

4. **Create Celery Tasks for Video Processing**:
   - Define tasks in Celery to handle video processing in the background.

5. **Notify the User Upon Completion**:
   - Implement a mechanism to notify the user once the background processing is complete.

### Step 1: Set Up Celery in Django

1. **Install Celery and Redis**:
   ```sh
   pip install celery[redis] redis
   ```

2. **Configure Celery in your Django project**:
- Create a `celery.py` file in your project directory (same level as `settings.py`):

   ```python
   from __future__ import absolute_import, unicode_literals
   import os
   from celery import Celery

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

   app = Celery('your_project_name')

   app.config_from_object('django.conf:settings', namespace='CELERY')

   app.autodiscover_tasks()
   ```

- Update `settings.py` with Celery configuration:

   ```python
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   CELERY_ACCEPT_CONTENT = ['json']
   CELERY_TASK_SERIALIZER = 'json'
   CELERY_RESULT_SERIALIZER = 'json'
   CELERY_TIMEZONE = 'UTC'
   ```

   - In `__init__.py` of your project directory:

   ```python
   from __future__ import absolute_import, unicode_literals

   from .celery import app as celery_app

   __all__ = ('celery_app',)
   ```

### Step 2: Create a Django Model for Video Uploads

Create a model in `models.py`:

```python
from django.db import models

class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    resolution_480p = models.FileField(upload_to='videos/480p/', null=True, blank=True)
    resolution_720p = models.FileField(upload_to='videos/720p/', null=True, blank=True)
    resolution_1080p = models.FileField(upload_to='videos/1080p/', null=True, blank=True)
```

### Step 3: Create a Django REST Framework API for Video Upload

Create a serializer in `serializers.py`:

```python
from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video', 'uploaded_at', 'processed']
```

Create a view in `views.py`:

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Video
from .serializers import VideoSerializer
from .tasks import process_video

class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video_instance = serializer.save()
process_video.delay(video_instance.id)
            return Response({"message": "File successfully uploaded. Background processing started."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Update `urls.py`:

```python
from django.urls import path
from .views import VideoUploadView

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
]
```

### Step 4: Create Celery Tasks for Video Processing

Create a task in `tasks.py`:

```python
from celery import shared_task
from .models import Video

@shared_task
def process_video(video_id):
    video_instance = Video.objects.get(id=video_id)
    # Process video to generate different resolutions
    # This is a placeholder for the actual processing logic

    # Update the model fields after processing
    video_instance.processed = True
    video_instance.save()
```

### Step 5: Notify the User Upon Completion

You can use WebSockets, Django Channels, or polling to notify the user about the completion of video processing. Here is a basic example of using polling:

1. **Front-End Angular Polling**:
   - Periodically check the status of the uploaded video using an API endpoint.

2. **Add a Status Endpoint**:
   - Create an API endpoint to check the status of the video processing:

   ```python
   class VideoStatusView(APIView):
       def get(self, request, video_id, *args, **kwargs):
           try:
               video_instance = Video.objects.get(id=video_id)
               return Response({"processed": video_instance.processed})
           except Video.DoesNotExist:
               return Response(status=status.HTTP_404_NOT_FOUND)
   ```

Update `urls.py`:

   ```python
   urlpatterns = [
       path('upload/', VideoUploadView.as_view(), name='video-upload'),
       path('status/<int:video_id>/', VideoStatusView.as_view(), name='video-status'),
   ]
   ```

This setup ensures that the file upload API responds immediately while processing the video in the background. You can extend this example with actual video processing logic and a more sophisticated notification mechanism.

---
---
---

Certainly! Let's delve into Celery for Django REST Framework to efficiently handle background tasks. We'll cover the following aspects:

1. **Setting Up Celery in a Django Project**
2. **Creating Celery Tasks**
3. **Integrating Celery with Django REST Framework**
4. **Monitoring Celery Tasks**
5. **Handling Task Results**
6. **Retrying Failed Tasks**
7. **Periodic Tasks**

### 1. Setting Up Celery in a Django Project

**Install Celery and Redis:**
```sh
pip install celery[redis] redis
```

**Project Directory Structure:**
```plaintext
your_project/
    ├── your_project/
    │   ├── __init__.py
│ ├── celery.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
    ├── app/
    │   ├── __init__.py
│ ├── models.py
│ ├── tasks.py
│ ├── serializers.py
│ ├── views.py
│ └── urls.py
├── manage.py
```

**Configure Celery:**

Create `celery.py` in your project directory (same level as `settings.py`):

```python
# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
```

Update `__init__.py` to load Celery when Django starts:

```python
# your_project/__init__.py
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ('celery_app',)
```

**Update `settings.py`:**

```python
# your_project/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### 2. Creating Celery Tasks

Define your tasks in `tasks.py` within your app:

```python
# app/tasks.py
from celery import shared_task
from .models import Video

@shared_task
def process_video(video_id):
    video_instance = Video.objects.get(id=video_id)
    # Placeholder for actual video processing logic
    # For example, creating multiple resolutions of the video

    # Update the model after processing
    video_instance.processed = True
    video_instance.save()
```

### 3. Integrating Celery with Django REST Framework

**Model and Serializer:**

```python
# app/models.py
from django.db import models

class Video(models.Model):
    video = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    resolution_480p = models.FileField(upload_to='videos/480p/', null=True, blank=True)
    resolution_720p = models.FileField(upload_to='videos/720p/', null=True, blank=True)
    resolution_1080p = models.FileField(upload_to='videos/1080p/', null=True, blank=True)
```

```python
# app/serializers.py
from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video', 'uploaded_at', 'processed']
```

**View to Handle Video Upload:**

```python
# app/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Video
from .serializers import VideoSerializer
from .tasks import process_video

class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video_instance = serializer.save()
process_video.delay(video_instance.id)
            return Response({"message": "File successfully uploaded. Background processing started."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**Update URLs:**

```python
# app/urls.py
from django.urls import path
from .views import VideoUploadView

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
]
```

### 4. Monitoring Celery Tasks

**Flower** is a web-based tool for monitoring Celery. Install Flower:

```sh
pip install flower
```

Run Flower:

```sh
celery -A your_project flower
```

Visit `http://localhost:5555` to monitor tasks.

### 5. Handling Task Results

If you need to handle task results, you can use `celery.result.AsyncResult`.

Example:

```python
# app/views.py
from celery.result import AsyncResult

class VideoStatusView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            return Response({"status": "Pending"})
        elif result.state == 'SUCCESS':
            return Response({"status": "Completed", "result": result.result})
        elif result.state == 'FAILURE':
            return Response({"status": "Failed", "error": str(result.result)})
```

Update URLs:

```python
# app/urls.py
urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('status/<str:task_id>/', VideoStatusView.as_view(), name='video-status'),
]
```

### 6. Retrying Failed Tasks

You can configure task retries with the `retry` method.

Example:

```python
# app/tasks.py
@shared_task(bind=True, max_retries=3)
def process_video(self, video_id):
    try:
        video_instance = Video.objects.get(id=video_id)
        # Placeholder for actual video processing logic
    except Exception as exc:
        raise self.retry(exc=exc)
```

### 7. Periodic Tasks

Celery Beat can schedule periodic tasks.

**Configure Celery Beat:**

Add to `settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'example-task': {
        'task': 'app.tasks.example_task',
        'schedule': crontab(minute=0, hour=0),  # Executes daily at midnight
    },
}
```

Create a periodic task:

```python
# app/tasks.py
from celery import shared_task

@shared_task
def example_task():
    # Your periodic task logic here
    pass
```

Run Celery Beat:

```sh
celery -A your_project beat
```

### Running Celery

**Start Celery Worker:**

```sh
celery -A your_project worker --loglevel=info
```

**Start Celery Beat (for periodic tasks):**

```sh
celery -A your_project beat --loglevel=info
```

**Start Flower (for monitoring):**

```sh
celery -A your_project flower
```

### Summary

In this detailed guide, we've set up Celery with Django to handle background tasks, created tasks for video processing, integrated Celery with Django REST Framework, monitored tasks with Flower, handled task results, configured retries for failed tasks, and scheduled periodic tasks. This setup ensures your API can handle time-consuming tasks efficiently by offloading them to the background, providing a responsive user experience.

---
---
---

The `.delay` method is a shortcut provided by Celery to send a task to the queue for execution in the background. When you call a Celery task using `.delay`, it serializes the task and its arguments, sends them to the Celery worker, and immediately returns control to the caller without waiting for the task to complete.

Here's a breakdown of how it works:

1. **Task Definition**: You define a task in `tasks.py` using the `@shared_task` decorator.
2. **Calling the Task**: You use the `.delay` method to enqueue the task with the provided arguments.

### Example

Let's revisit the example from the guide:

**Task Definition:**

```python
# app/tasks.py
from celery import shared_task
from .models import Video

@shared_task
def process_video(video_id):
    video_instance = Video.objects.get(id=video_id)
    # Placeholder for actual video processing logic
    # For example, creating multiple resolutions of the video

    # Update the model after processing
    video_instance.processed = True
    video_instance.save()
```

**Calling the Task:**

```python
# app/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Video
from .serializers import VideoSerializer
from .tasks import process_video

class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video_instance = serializer.save()
            # Enqueue the task for background processing
process_video.delay(video_instance.id)
            return Response({"message": "File successfully uploaded. Background processing started."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Understanding `.delay`

1. **Asynchronous Execution**: By calling `process_video.delay(video_instance.id)`, the task `process_video` is sent to the Celery task queue. This call is non-blocking and returns immediately, allowing the API to respond quickly to the client.

2. **Serialization**: The arguments passed to `.delay` (in this case, `video_instance.id`) are serialized so they can be sent to the Celery worker process. The worker will then deserialize these arguments and execute the task.

3. **Task Enqueueing**: `.delay` is a convenient way to enqueue tasks. Under the hood, it’s equivalent to calling `process_video.apply_async(args=[video_instance.id])`.

4. **Result Handling**: `.delay` returns an `AsyncResult` object, which can be used to check the status of the task, retrieve its result, or handle errors.

### Alternatives to `.delay`

- **apply_async**: If you need more control over the task execution, such as setting a countdown or retry policy, you can use `apply_async`.

```python
# Using apply_async with additional options
process_video.apply_async(args=[video_instance.id], countdown=60)  # Delays task execution by 60 seconds
```

### Monitoring and Handling Task Status

If you need to track the status of the task, you can do so using the `AsyncResult` object:

```python
# app/views.py
from celery.result import AsyncResult

class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video_instance = serializer.save()
task = process_video.delay(video_instance.id)
return Response({"message": "File successfully uploaded. Background processing started.", "task_id": task.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**Checking Task Status:**

```python
# app/views.py
class VideoStatusView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            return Response({"status": "Pending"})
        elif result.state == 'SUCCESS':
            return Response({"status": "Completed", "result": result.result})
        elif result.state == 'FAILURE':
            return Response({"status": "Failed", "error": str(result.result)})
```

**Update URLs:**

```python
# app/urls.py
urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('status/<str:task_id>/', VideoStatusView.as_view(), name='video-status'),
]
```

### Summary

The `.delay` method is a powerful feature of Celery that enables you to offload long-running tasks to the background, ensuring that your web application's response time remains fast and responsive. This method allows tasks to be executed asynchronously, letting you handle complex operations without blocking the main execution flow.

---
---
---

Running Celery for Django applications, especially when incorporating periodic tasks and monitoring tools like Flower, can indeed seem confusing at first. Let's break down how Celery works, the role of Celery Beat, and how you can manage these processes efficiently. Here's a detailed guide to using Celery, including background tasks and periodic tasks:

### Understanding Celery Components

1. **Celery Worker**: Executes the tasks. This is the core component.
2. **Celery Beat**: Scheduler for periodic tasks. It sends tasks to the queue at specified intervals.
3. **Celery Flower**: A web-based tool for monitoring and administrating Celery clusters.

### Setting Up Celery with Django

#### 1. Install Celery and Redis

Install Celery and a message broker like Redis (you can also use RabbitMQ).

```bash
pip install celery redis
```

Install Redis server:

For Ubuntu:
```bash
sudo apt-get install redis-server
```

For macOS:
```bash
brew install redis
```

Start the Redis server:

```bash
redis-server
```

#### 2. Configure Celery in Django

Create a `celery.py` file in your Django project directory (same level as `settings.py`).

```python
# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

Add Celery settings to your `settings.py`:

```python
# your_project/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

#### 3. Create a Tasks File

Create a `tasks.py` file in one of your Django apps (e.g., `app/tasks.py`).

```python
# app/tasks.py
from celery import shared_task
import time

@shared_task
def add(x, y):
    return x + y

@shared_task
def long_running_task():
    time.sleep(10)
    return 'Task Completed'
```

#### 4. Run Celery Workers and Beat

You need to run Celery workers to execute tasks and Celery Beat to schedule periodic tasks. It's common to run these commands in separate terminal instances, but you can use a process manager like Supervisor, systemd, or Docker Compose to manage them more efficiently.

Run Celery Worker:

```bash
celery -A your_project worker --loglevel=info
```

Run Celery Beat:

```bash
celery -A your_project beat --loglevel=info
```

Run Flower for monitoring (optional):

```bash
celery -A your_project flower --port=5555
```

### Using Celery Beat for Periodic Tasks

Celery Beat schedules tasks at regular intervals. Add periodic tasks to your Celery configuration.

```python
# your_project/settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'app.tasks.add',
        'schedule': 30.0,
        'args': (16, 16)
    },
    'run-every-morning': {
        'task': 'app.tasks.long_running_task',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
    },
}
```

### Integrating with Django Views

Here’s how you might integrate a Celery task into a Django view:

```python
# app/views.py
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .tasks import long_running_task

class MyView(APIView):
    def post(self, request):
        # Trigger the Celery task
        result = long_running_task.delay()
return Response({"task_id": result.id, "status": "Task started"})
```

### Checking Task Status

You can check the status of a task using its ID.

```python
# app/views.py
from celery.result import AsyncResult

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            response = {'status': 'Pending'}
        elif result.state == 'SUCCESS':
            response = {'status': 'Success', 'result': result.result}
        elif result.state == 'FAILURE':
            response = {'status': 'Failure', 'error': str(result.result)}
        else:
            response = {'status': 'Unknown'}
        return Response(response)
```

### Managing Celery Processes Efficiently

While running multiple terminal instances works for development, it’s not practical for production. Here are a few alternatives:

#### Using Supervisor

Supervisor is a process control system that allows you to monitor and control Celery processes.

Install Supervisor:

```bash
sudo apt-get install supervisor
```

Create configuration files for Celery worker and Celery Beat:

**Celery Worker Config (e.g., `/etc/supervisor/conf.d/celery_worker.conf`):**

```ini
[program:celery_worker]
command=/path/to/your/env/bin/celery -A your_project worker --loglevel=info
directory=/path/to/your/project
user=your_user
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_err.log
```

**Celery Beat Config (e.g., `/etc/supervisor/conf.d/celery_beat.conf`):**

```ini
[program:celery_beat]
command=/path/to/your/env/bin/celery -A your_project beat --loglevel=info
directory=/path/to/your/project
user=your_user
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_err.log
```

Start Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

#### Using Docker Compose

Docker Compose is another way to manage Celery processes. Create a `docker-compose.yml` file to define your services.

```yaml
version: '3'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - redis

  celery_worker:
    build: .
    command: celery -A your_project worker --loglevel=info
    volumes:
      - .:/code
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A your_project beat --loglevel=info
    volumes:
      - .:/code
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A your_project flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

Start the services:

```bash
docker-compose up
```

### Summary

By following this guide, you should be able to:

1. Set up Celery with Django.
2. Run Celery workers and Beat for background and periodic tasks.
3. Use `.delay` for asynchronous task execution.
4. Monitor tasks with Flower.
5. Manage Celery processes efficiently using Supervisor or Docker Compose.

Using Celery can greatly improve the responsiveness and scalability of your Django application by offloading long-running tasks to the background.

---
---
---

I understand your confusion. Let's clarify the use of the `@shared_task` decorator and how to manage and track Celery tasks in Django REST Framework, including how to handle task IDs and monitor tasks.

### Understanding `@shared_task`

The `@shared_task` decorator is used to define a Celery task that can be shared across multiple Django apps. It allows you to register a task without the need to import the Celery app instance explicitly in your `tasks.py` file. This is particularly useful for modular applications where tasks are defined in different apps.

### Tracking Task IDs

When you enqueue a task using Celery, it returns an `AsyncResult` object, which includes a unique task ID. This ID is essential for tracking the status of the task. You need to store and manage this task ID on the client-side (e.g., in your Angular frontend) or in your database, so you can query the status later.

Here's how you can implement this in a Django REST Framework application:

### Example Implementation

#### 1. Create and Configure Celery Task

Let's create a simple task for demonstration purposes.

```python
# app/tasks.py
from celery import shared_task
import time

@shared_task
def process_video(video_id):
    # Simulate long-running task
    time.sleep(10)
    return f'Video {video_id} processed'
```

#### 2. Trigger Task from a Django View

Create a view that triggers the task and returns the task ID.

```python
# app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import process_video

class ProcessVideoView(APIView):
    def post(self, request):
        video_id = request.data.get('video_id')
        result = process_video.delay(video_id)
return Response({"task_id": result.id, "status": "Task started"})
```

#### 3. Check Task Status

Create another view to check the status of a task using its ID.

```python
# app/views.py
from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            response = {'status': 'Pending'}
        elif result.state == 'SUCCESS':
            response = {'status': 'Success', 'result': result.result}
        elif result.state == 'FAILURE':
            response = {'status': 'Failure', 'error': str(result.result)}
        else:
            response = {'status': 'Unknown'}
        return Response(response)
```

#### 4. Update URLs

Add the views to your `urls.py`.

```python
# app/urls.py
from django.urls import path
from .views import ProcessVideoView, TaskStatusView

urlpatterns = [
    path('process-video/', ProcessVideoView.as_view(), name='process_video'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
]
```

#### 5. Angular Frontend (Example)

Here’s how you might handle this in your Angular frontend.

1. **Trigger Task**: Call the `process-video` API to trigger the task and store the task ID.

```typescript
// process-video.component.ts
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-process-video',
  template: `
    <button (click)="processVideo()">Process Video</button>
    <p *ngIf="taskId">Task ID: {{ taskId }}</p>
  `
})
export class ProcessVideoComponent {
  taskId: string;

  constructor(private http: HttpClient) {}

  processVideo() {
this.http.post('/api/process-video/', { video_id: 123 }).subscribe((response: any) => {
      this.taskId = response.task_id;
    });
  }
}
```

2. **Check Task Status**: Periodically check the task status using the task ID.

```typescript
// task-status.component.ts
import { HttpClient } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-task-status',
  template: `
    <p>Task Status: {{ status }}</p>
  `
})
export class TaskStatusComponent implements OnInit {
  @Input() taskId: string;
  status: string;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.checkStatus();
  }

  checkStatus() {
    this.http.get(`/api/task-status/${this.taskId}/`).subscribe((response: any) => {
      this.status = response.status;
      if (response.status !== 'Success' && response.status !== 'Failure') {
        setTimeout(() => this.checkStatus(), 2000);  // Check every 2 seconds
      }
    });
  }
}
```

### Monitoring and Managing Tasks with Celery

#### Flower for Monitoring

Flower is a web-based tool for monitoring Celery tasks. It provides a real-time view of task progress, history, and other statistics.

1. **Install Flower**:

```bash
pip install flower
```

2. **Run Flower**:

```bash
celery -A your_project flower --port=5555
```

Visit `http://localhost:5555` in your web browser to view the Flower dashboard.

#### Using Celery Beat for Periodic Tasks

Celery Beat is used to schedule tasks periodically. These tasks are automatically added to the queue at specified intervals.

1. **Define Periodic Tasks** in `settings.py`:

```python
# your_project/settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'process-videos-every-hour': {
        'task': 'app.tasks.process_video',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (1,),  # Example argument
    },
}
```

2. **Run Celery Beat**:

```bash
celery -A your_project beat --loglevel=info
```

### Running Celery in Production

To avoid running multiple terminal commands manually, you can use a process manager like Supervisor or Docker Compose to manage Celery processes.

#### Using Supervisor

Supervisor allows you to manage and monitor Celery processes.

1. **Install Supervisor**:

```bash
sudo apt-get install supervisor
```

2. **Create Configuration Files** for Celery Worker and Beat.

**Celery Worker Config** (`/etc/supervisor/conf.d/celery_worker.conf`):

```ini
[program:celery_worker]
command=/path/to/your/env/bin/celery -A your_project worker --loglevel=info
directory=/path/to/your/project
user=your_user
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_err.log
```

**Celery Beat Config** (`/etc/supervisor/conf.d/celery_beat.conf`):

```ini
[program:celery_beat]
command=/path/to/your/env/bin/celery -A your_project beat --loglevel=info
directory=/path/to/your/project
user=your_user
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_err.log
```

3. **Start Supervisor**:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

#### Using Docker Compose

Docker Compose can manage Celery services efficiently.

1. **Create a `docker-compose.yml`**:

```yaml
version: '3'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - redis

  celery_worker:
    build: .
    command: celery -A your_project worker --loglevel=info
    volumes:
      - .:/code
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A your_project beat --loglevel=info
    volumes:
      - .:/code
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A your_project flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

2. **Start the Services**:

```bash
docker-compose up
```

### Summary

By following this guide, you should have a clear understanding of:

1. **How to create and manage Celery tasks**.
2. **How to trigger tasks and track their status using Django REST Framework**.
3. **How to use Celery Beat for periodic tasks**.
4. **How to monitor tasks using Flower**.
5. **How to manage Celery processes efficiently using Supervisor or Docker Compose**.

These steps should help you integrate Celery into your Django application effectively, making it easier to handle background and periodic tasks.

---
---
---

Celery task results are not stored indefinitely by default. How long task results are stored depends on the backend configuration for result storage. If you want to keep task results for a long period, you'll need to configure the result backend accordingly and manage the expiration of results.

### Configuring Celery Result Backend

Celery supports various backends for storing task results, such as Redis, RabbitMQ, and databases (e.g., PostgreSQL, MySQL).

#### Example with Redis

To use Redis as the result backend and configure result expiration:

1. **Install Redis**:

```bash
pip install celery[redis]
```

2. **Update Celery Configuration** in `settings.py`:

```python
# your_project/settings.py

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Keep task results for 1 year (in seconds)
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 * 365  # 1 year
```

With this configuration, task results will be stored in Redis and will expire after 1 year.

#### Example with Database Backend

If you prefer to use a database for storing task results, you can configure Celery to use a database backend.

1. **Install Database Backend** (PostgreSQL, for example):

```bash
pip install celery[sqlalchemy] psycopg2-binary
```

2. **Update Celery Configuration** in `settings.py`:

```python
# your_project/settings.py

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'db+postgresql://user:password@localhost/dbname'

# Keep task results for 1 year (in seconds)
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 * 365  # 1 year
```

3. **Run Migrations**:

You need to create the necessary tables in your database for storing Celery results.

```bash
celery -A your_project backend_cleanup
```

### Managing Task Results

You can manage task results by regularly cleaning up old results if you don't want them to persist indefinitely.

1. **Using Celery's Built-in Cleanup Task**:

Celery provides a built-in periodic task to clean up old results. Add this task to your periodic task schedule:

```python
# your_project/settings.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-results': {
        'task': 'celery.backend_cleanup',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}
```

2. **Custom Cleanup Task**:

If you need more control over the cleanup process, you can create a custom cleanup task:

```python
# app/tasks.py
from celery import shared_task
from datetime import timedelta
from celery.backends.database.models import Task
from celery.utils.time import maybe_timedelta
from celery import current_app

@shared_task
def cleanup_old_results():
    expires = current_app.conf.result_expires
    Task.query.filter(Task.date_done < (datetime.utcnow() - maybe_timedelta(expires))).delete()
```

Add this task to your periodic task schedule:

```python
# your_project/settings.py

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-results': {
        'task': 'app.tasks.cleanup_old_results',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}
```

### Retrieving Task Results

To retrieve the result of a task, use the task ID:

```python
# app/views.py
from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            response = {'status': 'Pending'}
        elif result.state == 'SUCCESS':
            response = {'status': 'Success', 'result': result.result}
        elif result.state == 'FAILURE':
            response = {'status': 'Failure', 'error': str(result.result)}
        else:
            response = {'status': 'Unknown'}
        return Response(response)
```

### Conclusion

By configuring the result backend and managing the task result expiration, you can control how long task results are stored and accessed. Whether using Redis, a database, or another backend, ensure your configuration aligns with your requirements for result persistence. If you need results for auditing or historical purposes, consider storing essential task information in your application's database.

---
---
---



