from pullgerDataSynchronization import models
from pullgerMultiSessionManager import apiMSM


def get_all_count():
    return models.ExecutionStackLinks.objects.get_count()


def get_finished_count():
    return models.ExecutionStackLinks.objects.get_finished_count()


def send_all_task_for_processing(limit=None):
    try:
        request_limit = int(limit)
    except:
        request_limit = None

    count = 0
    unprocessed_tasks = models.ExecutionStackLinks.objects.get_all_unprocessed_task()
    for task_for_processing in unprocessed_tasks:
        apiMSM.add_sync_task(task_for_processing)
        count += 1
        if request_limit is not None and request_limit <= count:
            break
    return count
