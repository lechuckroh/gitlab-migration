import os
import pathlib
import re
import sys
import tempfile

import gitlab
from git import Repo


class GitLabMigration:
    def __init__(self, gl_src, gl_dest):
        self.gl_src = gl_src
        self.gl_dest = gl_dest

    def migrate(self, src_group_id, dest_group_id):
        self._migrate_groups(src_group_id, dest_group_id)
        print("migration finished.")

    def _migrate_groups(self, src_group_id, dest_group_id):
        """
        Migrate a group
        """
        src_group = self.gl_src.groups.get(src_group_id)
        src_dict = self._get_subgroups_by_name(src_group)

        dest_group = self.gl_dest.groups.get(dest_group_id)
        dest_dict = self._get_subgroups_by_name(dest_group)

        # migrate subgroups
        for subgroup_name, src_subgroup in src_dict.items():
            # create dest subgroup if not exists
            dest_subgroup = dest_dict.get(subgroup_name)
            if dest_subgroup is None:
                print(f"[+ GROUP] {dest_group.name} / {subgroup_name}")
                dest_subgroup = self._create_subgroup(dest_group, subgroup_name)

            self._migrate_groups(src_subgroup.id, dest_subgroup.id)

        # migrate projects
        src_project_dict = self._get_projects_by_name(src_group)
        dest_project_dict = self._get_projects_by_name(dest_group)
        for project_name, src_project in src_project_dict.items():
            # create dest project if not exists
            dest_project = dest_project_dict.get(project_name)
            if dest_project is None:
                print(f"[+ PROJECT] {dest_group.path} / {project_name}")
                dest_project = self._create_project(dest_group, project_name)

            self._migrate_project(src_project, dest_project)

    def _create_subgroup(self, group, name):
        """
        Create subgroup under 'group_id' group (destination gitlab)
        """
        return self.gl_dest.groups.create({'name': name, 'path': name, 'parent_id': group.id})

    def _create_project(self, group, name):
        """
        Create project under 'group_id' group (destination gitlab)
        """
        return self.gl_dest.projects.create({'name': name, 'namespace_id': group.id})

    def _migrate_project(self, src_project, dest_project):
        """
        Migrate a project
        """
        def get_url(gl, p):
            if gl.http_username:
                regex = r"(http[s]?:\/\/)(.+)"
                matches = re.findall(regex, p.http_url_to_repo)
                m = matches[0]
                return f"{m[0]}{gl.http_username}:{gl.http_password}@{m[1]}"
            return p.ssh_url_to_repo

        src_url = get_url(self.gl_src, src_project)
        dest_url = get_url(self.gl_dest, dest_project)

        # temp directory context
        with tempfile.TemporaryDirectory() as wd:
            # clone src_url to local disk
            print(f"[clone] {src_url} ---> {wd}")
            repo = Repo.clone_from(src_url, wd)

            # add remote url
            remote_dest = repo.create_remote('dest', dest_url)

            # push all branches to dest server
            print(f"[push] {wd} ---> {dest_url}")
            remote_dest.push("--all")
            remote_dest.push("--tags")

        print(f"[done] {src_project.path_with_namespace}")

    @staticmethod
    def _get_subgroups_by_name(group):
        result = dict()
        for subgroup in group.subgroups.list(per_page=100):
            result[subgroup.name] = subgroup
        return result

    @staticmethod
    def _get_projects_by_name(group):
        result = dict()
        for project in group.projects.list(per_page=100):
            result[project.name] = project
        return result


def get_cfg_file(candidates):
    for f in candidates:
        if pathlib.Path(f).is_file():
            return f
    return None


def get_env(name):
    return os.environ.get(name)


def new_gitlab(name, cfg_file, env_prefix):
    gl = gitlab.Gitlab.from_config(name, [cfg_file])

    def override_config(env_name, var_name):
        env_full_name = f"{env_prefix}{env_name}"
        env_value = get_env(env_full_name)
        if env_value:
            setattr(gl, var_name, env_value)

    env_dict = {
        'SSL_VERIFY': 'ssl_verify',
        'TIMEOUT': 'timeout',
        'PRIVATE_TOKEN': 'private_token',
        'HTTP_USERNAME': 'http_username',
        'HTTP_PASSWORD': 'http_password',
        'OAUTH_TOKEN': 'oauth_token',
        'JOB_TOKEN': 'job_token',
    }

    for k, v in env_dict.items():
        override_config(k, v)

    return gl


def migrate():
    cfg_file = get_cfg_file(['./gitlab-migration-local.cfg', './gitlab-migration.cfg'])
    if cfg_file is None:
        sys.exit("cfg file not found")

    src_group_id = get_env('GITLAB_SRC_GROUP_ID')
    if not src_group_id:
        sys.exit("GITLAB_SRC_GROUP_ID env is not set")

    dest_group_id = get_env('GITLAB_DEST_GROUP_ID')
    if not dest_group_id:
        sys.exit("GITLAB_DEST_GROUP_ID env is not set")

    # src gitlab
    gl_src = new_gitlab('src', cfg_file, 'GITLAB_SRC_')
    # dest gitlab
    gl_dest = new_gitlab('dest', cfg_file, 'GITLAB_DEST_')

    # run migration
    GitLabMigration(gl_src, gl_dest).migrate(src_group_id, dest_group_id)


if __name__ == "__main__":
    migrate()
