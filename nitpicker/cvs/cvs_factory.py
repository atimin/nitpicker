from .git_adapter import GitAdapter


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
        """
        if cvs not in self.SUPPORTED_CSV:
            raise 'CVS {} is not supported.'.format(cvs)

        return {
            'git': GitAdapter()
        }.get(cvs)
