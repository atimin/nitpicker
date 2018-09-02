# -*- coding: utf-8 -*-
from .git_adapter import GitAdapter
from .null_adapter import NullAdapter


class CVSFactory:
    """
    Factory of CVS adapters
    """

    CVS_ADAPTERS = { 'git': GitAdapter}

    def create_cvs_adapter(self, cvs='git'):
        """
        Creates the cvs adapter of the given CVS
        :param cvs: Type of CVS. Supported only git.
        :return: CVSAdapter
        :raise: Exception if foramt is not supported
        """
        if cvs not in self.CVS_ADAPTERS:
            raise Exception('CVS {} is not supported.'.format(cvs))

        try:
            return self.CVS_ADAPTERS.get(cvs)()
        except Exception:
            return NullAdapter()


