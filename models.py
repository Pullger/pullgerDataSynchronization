import uuid as uuid_class
from datetime import datetime

from django.dispatch import receiver
from django.db import models
from django.db.models import signals
from django.db import transaction
from django.db.models import Q

from pullgerDataSynchronization import commonDS


class ExecutionStackLinksManager(models.Manager):
    def get_count(self):
        return self.all().count()

    def get_finished_count(self):
        return self.filter(executed=True).count()

    def is_link_exist(self, uuid_link):
        obj_link = self.filter(uuid_link=uuid_link).first()
        if obj_link is None:
            return False
        else:
            return True

    def get_all_unprocessed_task(self):
        return self.filter(~Q(sent=True) & ~Q(executed=True))

    def get_by_uuid(self=None, uuid: (str, uuid_class) = None):
        if self is None:
            self = ExecutionStackLinks.objects

        return self.filter(uuid=str(uuid)).first()

    def initialization_clear(self):
        self.filter(Q(sent=True) & Q(executed=False)).update(sent=False)


class ExecutionStackLinks(models.Model):
    uuid = models.UUIDField(default=uuid_class.uuid4, editable=False, primary_key=True)
    uuid_link = models.CharField(max_length=36, null=False)
    table = models.CharField(max_length=250, null=False)
    model = models.CharField(max_length=1000, null=False)

    sent = models.BooleanField(default=False)
    sent_moment = models.DateTimeField(default=None, null=True)
    executed = models.BooleanField(default=False)
    executed_moment = models.DateTimeField(null=True)

    status_code = models.IntegerField(null=True)
    status_description = models.CharField(max_length=1000, null=True)

    handler = models.CharField(max_length=100, null=False)
    executor = models.CharField(max_length=120, default=None, null=True)

    description = models.CharField(max_length=500, default='', null=True)
    pull_data = models.TextField()

    objects = ExecutionStackLinksManager()

    def set_sent(self):
        self.sent = True
        self.sent_moment = datetime.now()
        self.save()

    def set_executed(self, status_code=None, status_description=None):
        self.executed = True
        self.executed_moment = datetime.now()
        self.status_code = status_code
        self.status_description = status_description
        self.save()

        issue_model = commonDS.get_model_class_by_name(self.model)
        element = issue_model.objects.get_by_uuid(uuid=self.uuid_link)
        element.moment_sync = datetime.now()
        if self.status_code == 200:
            element.sync_executed = True
        else:
            element.sync_executed = False
        element.sync_status = status_code
        element.save()
        pass

    def finalize(self=None, uuid=None, status_code=None, status_description=None):
        if self is None:
            self = ExecutionStackLinks.objects.get_by_uuid(uuid)

        self.set_executed(status_code=status_code, status_description=status_description)


    @classmethod
    def check_and_create_link(cls, element, model: str, handler: str):
        if cls.objects.is_link_exist(element.uuid) is False:
            newLink = cls()
            newLink.model = model
            newLink.handler = handler.lower()
            newLink.uuid_link = str(element.uuid)
            newLink.save()
