# -*- coding: utf-8 -*-
class CVSAdapter:
    """
    Interface for getting information from CVS repo and settings
    """

    def get_user_name(self):
        """
        Get user's name from CVS settings
        :return:
        """
        raise NotImplementedError

    def get_user_email(self):
        """
        Get user's email from CVS settings
        :return:
        """
        raise NotImplementedError

    def diff(self, parent_branch):
        """
        Get difference between active branch and its parent

        :return: Returns a generator of dicts:
        {'insertions': 3,
            'deletions': 3,
            'lines': 6,
            'object': '.\\QA_REPORT.md',
            'commit': '8e3bacd9e6f333b92bc974844168b68acf95816e',
            'author': 'atimin@gmail.com',
            'timestamp': datetime.datetime(..),
            'type': 'M'
        }

        """
        raise NotImplementedError
