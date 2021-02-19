# encoding: utf-8

"""Functions that make mocking with pytest easier and more readable."""

from unittest.mock import ANY, call  # noqa # isort:skip
from unittest.mock import patch, PropertyMock  # isort:skip


def method_mock(request, cls, method_name, autospec=True, **kwargs):
    """Return mock for method *method_name* on *cls*.

    The patch is reversed after pytest uses it.
    """
    _patch = patch.object(cls, method_name, autospec=autospec, **kwargs)
    request.addfinalizer(_patch.stop)
    return _patch.start()


def property_mock(request, cls, prop_name, **kwargs):
    """Return mock for property *prop_name* on class *cls*.

    The patch is reversed after pytest uses it.
    """
    _patch = patch.object(cls, prop_name, new_callable=PropertyMock, **kwargs)
    request.addfinalizer(_patch.stop)
    return _patch.start()
