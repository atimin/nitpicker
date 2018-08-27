
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
