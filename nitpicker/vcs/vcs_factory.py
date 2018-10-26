# -*- coding: utf-8 -*-
from .git_adapter import GitAdapter
from .null_adapter import NullAdapter


class VCSFactory:
    """
    Factory of МСЫ adapters
    """

    VCS_ADAPTERS = {'git': GitAdapter}

    def create_cvs_adapter(self, vcs='git'):
        """
        Creates the vcs adapter of the given VCS
        :param vcs: Type of VCS. Supported only git.
        :return: CVSAdapter
        :raise: Exception if foramt is not supported
        """
        if vcs not in self.VCS_ADAPTERS:
            raise Exception('VCS {} is not supported.'.format(vcs))

        try:
            return self.VCS_ADAPTERS.get(vcs)()
        except Exception:
            return NullAdapter()


