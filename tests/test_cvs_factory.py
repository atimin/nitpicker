import unittest
from nitpicker.cvs.cvs_factory import CVSFactory
from nitpicker.cvs.null_adapter import NullAdapter
from nitpicker.cvs.cvs_adapter import CVSAdapter


class WrongAdapter(CVSAdapter):

    def get_user_name(self):
        pass

    def get_user_email(self):
        pass

    def __init__(self):
        raise Exception('I cannot be created!')


class TestCVSFactory(unittest.TestCase):

    def setUp(self):
        self.__factory = CVSFactory()

    def test_create_null_adapter(self):
        self.__factory.CVS_ADAPTERS['raise_exception'] = WrongAdapter
        self.assertEqual(NullAdapter, type(self.__factory.create_cvs_adapter('raise_exception')))

    def test_unsupported_adapter_type(self):
        with self.assertRaises(Exception):
            self.__factory.create_cvs_adapter('not_supported_type')