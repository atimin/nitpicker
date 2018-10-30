# -*- coding: utf-8 -*-
from .vcs_adapter import VCSAdapter
import git.cmd
import git.exc
import os


class GitAdapter(VCSAdapter):
    """
    Implements a VCS adapter for git repository.
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

    def diff(self, parent_branch):
        try:
            branch = self.__repo.active_branch
            if branch.commit == self.__repo.commit(parent_branch):
                return list()

            for commit in self.__repo.iter_commits(branch):
                if commit.parents:
                    parent = commit.parents[0]
                else:
                    break

                if parent == self.__repo.commit(parent_branch):
                    break

                diffs = {
                    diff.a_path: diff for diff in parent.diff(commit)
                }

                for objpath, stats in commit.stats.files.items():
                    diff = diffs.get(objpath)
                    if not diff:
                        for diff in diffs.values():
                            if diff.b_path == '.' and diff.renamed:
                                break

                    # Update the stats with the additional information
                    stats.update({
                        'object': os.path.join(objpath),
                        'commit': commit.hexsha,
                        'author': commit.author.email,
                        'timestamp': commit.authored_datetime,
                        'type': diff.change_type,
                    })

                    yield stats

        except git.exc.GitCommandError as e:
            print(e)

