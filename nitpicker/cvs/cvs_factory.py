# -*- coding: utf-8 -*-
from .git_adapter import GitAdapter
from .null_adapter import NullAdapter


class CVSFactory:
    """
    Factory of CVS adapters
    """

    SUPPORTED_CSV = ['git']

    def create_cvs_adapter(self, cvs='git'):
        """
        Creates the cvs adapter of the given CVS
        :param cvs: Type of CVS. Supported only git.
        :return: CVSAdapter
        :raise: Exception if foramt is not supported
        """
        if cvs not in self.SUPPORTED_CSV:
            raise 'CVS {} is not supported.'.format(cvs)

        try:
            return {
                'git': GitAdapter()
            }.get(cvs)
        except Exception:
            return NullAdapter()


