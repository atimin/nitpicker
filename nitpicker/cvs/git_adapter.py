from .cvs_adapter import CVSAdapter
import git.cmd


class GitAdapter(CVSAdapter):

    def __init__(self):
        self.__repo = git.Repo('.')

    def get_user_name(self):
        cfg_reader = self.__repo.config_reader()
        return cfg_reader.get_value("user", "name")

    def get_user_email(self):
        cfg_reader = self.__repo.config_reader()
        return cfg_reader.get_value("user", "email")

