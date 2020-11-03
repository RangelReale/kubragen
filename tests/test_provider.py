import unittest

from kubragen.provider import Provider_Generic


class TestProvider(unittest.TestCase):

    def test_secret_encode(self):
        provider = Provider_Generic()
        self.assertEqual(provider.secret_data_encode('kubragen'), 'a3VicmFnZW4=')
