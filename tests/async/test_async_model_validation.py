from asgiref.sync import sync_to_async
from django.db import connection, transaction
from django.test import TestCase, TransactionTestCase

from .models import SimpleModel


class AsyncModelValidationTests(TestCase):
    async def test_afull_clean_ok(self):
        obj = SimpleModel(field=1)
        await obj.afull_clean()

    async def test_avalidate_unique_ok(self):
        obj = SimpleModel(field=2)
        await obj.avalidate_unique()

    async def test_avalidate_constraints_ok(self):
        obj = SimpleModel(field=3)
        await obj.avalidate_constraints()

    def test_sync_full_clean_still_works(self):
        obj = SimpleModel(field=4)
        obj.full_clean()


class AsyncConnectionTests(TestCase):
    async def test_aensure_connection(self):
        await connection.aensure_connection()

        def _probe():
            connection.ensure_connection()
            with connection.cursor() as c:
                c.execute("SELECT 1")

        await sync_to_async(_probe)()


class AsyncOnCommitTests(TransactionTestCase):
    available_apps = ["async"]

    async def test_aon_commit_sync_callback(self):
        called = []

        def mark():
            called.append(True)

        def _run():
            with transaction.atomic():
                # Register from async API via event loop thread using sync bridge.
                from asgiref.sync import async_to_sync

                async_to_sync(transaction.aon_commit)(mark)
                assert called == []
            assert called == [True]

        await sync_to_async(_run)()
