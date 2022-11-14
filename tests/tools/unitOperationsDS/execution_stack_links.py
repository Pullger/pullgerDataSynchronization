from pullgerDataSynchronization import apiDS
from django.test import TestCase


def send_all_task_for_processing(self: TestCase):
    return apiDS.send_all_task_for_processing()
