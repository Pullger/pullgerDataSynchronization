from pullgerDataSynchronization import models
from pullgerInternalControl import pIC_pR


def registrate_sync_task(created, instance, sender):
    if created is True:
        try:
            models.ExecutionStackLinks.check_and_create_link(
                element=instance,
                model=sender.__module__ + '.' + sender.__qualname__,
                handler='sync'
            )
        except BaseException as e:
            raise pIC_pR.TT.LinkCreate(
                'Unexpected error on creating LINK',
                level=50,
                exeptation=e
            )