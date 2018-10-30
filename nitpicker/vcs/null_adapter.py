# -*- coding: utf-8 -*-
from .vcs_adapter import VCSAdapter


class NullAdapter(VCSAdapter):
    """
    Null implementation of CVSAdapter
    """

    def diff(self, parent_branch):
        pass

    def get_user_name(self):
        return "Unknown"

    def get_user_email(self):

        return "Unknown"
