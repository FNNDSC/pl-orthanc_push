
from unittest import TestCase
from unittest import mock
from orthanc_push.orthanc_push import Orthanc_push


class Orthanc_pushTests(TestCase):
    """
    Test Orthanc_push.
    """
    def setUp(self):
        self.app = Orthanc_push()

    def test_run(self):
        """
        Test the run code.
        """
        args = []
        if self.app.TYPE == 'ds':
            args.append('inputdir') # you may want to change this inputdir mock
        args.append('outputdir')  # you may want to change this outputdir mock

        # you may want to add more of your custom defined optional arguments to test
        # your app with
        # eg.
        # args.append('--custom-int')
        # args.append(10)

        options = self.app.parse_args(args)
        self.app.run(options)

        # write your own assertions
        self.assertEqual(options.outputdir, 'outputdir')
