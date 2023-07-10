import json
from datetime import datetime
from typing import Annotated

from google.cloud.tasks_v2 import CloudTasksClient, CreateTaskRequest, HttpMethod, HttpRequest, Task
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp

from utils.constants import LOCATION, PROJECT_ID


def create_http_task(
    url: str,
    queue: str,
    payload: dict,
    task_id: str | None = None,
    dispatch_deadline: int | None = None,
    schedule_time: datetime | None = None,
    http_method: Annotated[int, HttpMethod] = HttpMethod.POST,
) -> Task:
    """
    Create an HTTP POST task with a JSON payload.
    """
    client = CloudTasksClient()

    name = client.task_path(PROJECT_ID, LOCATION, queue, task_id) if task_id else None
    http_request = HttpRequest(
        url=url,
        http_method=http_method,
        body=json.dumps(payload).encode(),
        headers={"Content-type": "application/json"},
    )

    task = Task(name=name, http_request=http_request)

    if schedule_time is not None:
        timestamp = Timestamp()
        timestamp.FromDatetime(schedule_time)
        task.schedule_time = timestamp

    if dispatch_deadline is not None:
        duration = Duration()
        duration.FromSeconds(dispatch_deadline)
        task.dispatch_deadline = duration

    parent = client.queue_path(project=PROJECT_ID, location=LOCATION, queue=queue)
    task_request = CreateTaskRequest(parent=parent, task=task)
    return client.create_task(request=task_request)
