import os
import warnings
from unittest import mock

from asgiref.sync import async_to_sync
from django.dispatch import Signal
from django.test import SimpleTestCase
from django.utils.deprecation import RemovedInDjango71Warning


class AsyncSendWarningTests(SimpleTestCase):
    def test_send_from_running_loop_warns_when_enabled(self):
        sig = Signal()

        async def _call():
            with mock.patch.dict(os.environ, {"DJANGO_ASYNC_SIGNAL_WARN": "1"}):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    sig.send(sender=None)
                    self.assertTrue(
                        any(issubclass(x.category, RemovedInDjango71Warning) for x in w)
                    )

        async_to_sync(_call)()

    def test_send_silent_by_default(self):
        sig = Signal()

        async def _call():
            with mock.patch.dict(os.environ, {"DJANGO_ASYNC_SIGNAL_WARN": "0"}):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    sig.send(sender=None)
                    self.assertFalse(
                        any(issubclass(x.category, RemovedInDjango71Warning) for x in w)
                    )

        async_to_sync(_call)()
