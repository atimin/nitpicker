# -*- coding: utf-8 -*-
from .cvs_adapter import CVSAdapter
import git.cmd
import git.exc
import os


class GitAdapter(CVSAdapter):
    """
    Implements a cvs adapter for git repository.
    """

    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    def __init__(self):
        self.__repo = git.Repo('.')

    def get_user_name(self):
        cfg_reader = self.__repo.config_reader()
        return cfg_reader.get_value("user", "name")

    def get_user_email(self):
        cfg_reader = self.__repo.config_reader()
        return cfg_reader.get_value("user", "email")

    def diff(self, branch, parent_branch):
        try:
            for commit in self.__repo.iter_commits(branch):

                parent = commit.parents[0] if commit.parents else self.EMPTY_TREE_SHA

                if parent == self.__repo.commit(parent_branch):
                    break

                diffs = {
                    diff.a_path: diff for diff in commit.diff(parent)
                }

                for objpath, stats in commit.stats.files.items():
                    diff = diffs.get(objpath)
                    if not diff:
                        for diff in diffs.values():
                            if diff.b_path == '.' and diff.renamed:
                                break

                    # Update the stats with the additional information
                    stats.update({
                        'object': os.path.join('.', objpath),
                        'commit': commit.hexsha,
                        'author': commit.author.email,
                        'timestamp': commit.authored_datetime,
                        'type': diff.change_type,
                    })

                    yield stats

        except git.exc.GitCommandError as e:
            print(e)

