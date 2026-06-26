from datetime import datetime
from unittest import mock

from django.template import TemplateSyntaxError
from django.test import SimpleTestCase
from django.utils.formats import date_format

from ..utils import setup

# Fixed clock so template rendering and assertions cannot straddle midnight /
# month / year boundaries (pass locally on a fast machine, fail on slow CI).
_FROZEN_NOW = datetime(2024, 6, 15, 12, 0, 0)


class _FrozenDateTime(datetime):
    """datetime subclass with a fixed now() for deterministic template tests."""

    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return _FROZEN_NOW.replace(tzinfo=tz)
        return _FROZEN_NOW


class NowTagTests(SimpleTestCase):
    def _freeze_now(self):
        return mock.patch("django.template.defaulttags.datetime", _FrozenDateTime)

    @setup({"now01": '{% now "j n Y" %}'})
    def test_now01(self):
        """
        Simple case
        """
        with self._freeze_now():
            output = self.engine.render_to_string("now01")
        self.assertEqual(
            output,
            "%d %d %d"
            % (
                _FROZEN_NOW.day,
                _FROZEN_NOW.month,
                _FROZEN_NOW.year,
            ),
        )

    # Check parsing of locale strings
    @setup({"now02": '{% now "DATE_FORMAT" %}'})
    def test_now02(self):
        with self._freeze_now():
            output = self.engine.render_to_string("now02")
        self.assertEqual(output, date_format(_FROZEN_NOW))

    @setup({"now03": "{% now 'j n Y' %}"})
    def test_now03(self):
        """
        #15092 - Also accept simple quotes
        """
        with self._freeze_now():
            output = self.engine.render_to_string("now03")
        self.assertEqual(
            output,
            "%d %d %d"
            % (
                _FROZEN_NOW.day,
                _FROZEN_NOW.month,
                _FROZEN_NOW.year,
            ),
        )

    @setup({"now04": "{% now 'DATE_FORMAT' %}"})
    def test_now04(self):
        with self._freeze_now():
            output = self.engine.render_to_string("now04")
        self.assertEqual(output, date_format(_FROZEN_NOW))

    @setup({"now05": "{% now 'j \"n\" Y'%}"})
    def test_now05(self):
        with self._freeze_now():
            output = self.engine.render_to_string("now05")
        self.assertEqual(
            output,
            '%d "%d" %d'
            % (
                _FROZEN_NOW.day,
                _FROZEN_NOW.month,
                _FROZEN_NOW.year,
            ),
        )

    @setup({"now06": "{% now \"j 'n' Y\"%}"})
    def test_now06(self):
        with self._freeze_now():
            output = self.engine.render_to_string("now06")
        self.assertEqual(
            output,
            "%d '%d' %d"
            % (
                _FROZEN_NOW.day,
                _FROZEN_NOW.month,
                _FROZEN_NOW.year,
            ),
        )

    @setup({"now07": '{% now "j n Y" as N %}-{{N}}-'})
    def test_now07(self):
        with self._freeze_now():
            output = self.engine.render_to_string("now07")
        self.assertEqual(
            output,
            "-%d %d %d-"
            % (
                _FROZEN_NOW.day,
                _FROZEN_NOW.month,
                _FROZEN_NOW.year,
            ),
        )

    @setup({"no_args": "{% now %}"})
    def test_now_args(self):
        with self.assertRaisesMessage(
            TemplateSyntaxError, "'now' statement takes one argument"
        ):
            self.engine.render_to_string("no_args")
