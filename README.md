# gitlab-migration

![docker image](https://github.com/lechuckroh/gitlab-migration/workflows/docker%20image/badge.svg)

Migrate GitLab repositories to other GitLab server

## Requirements
* Python 3

## Configuration
Open `python-gitlab.cfg` file and change `src` and `dest` sections.

You can create private token at [Personal Access Tokens](https://gitlab.com/profile/personal_access_tokens) menu.

See [python-gitlab Configuration](https://python-gitlab.readthedocs.io/en/stable/cli.html#configuration) for detailed configuration description.

* `default`: source gitlab connection
* `ssl_verify`: verify the SSL certificate
* `timeout`: Number of seconds to wait for an answer before failing.

### Override with env
Tou can override existing configurations using environment variables.

variable name prefix:
* `GITLAB_SRC_`: `src` group variables 
* `GITLAB_DEST_`: `dest` group variables 

variable name and configuration mapping:

| env name        | configuration   |
|:---------------:|:---------------:|
| `SSL_VERIFY`    | `ssl_verify`    |
| `TIMEOUT`       | `timeout`       |
| `PRIVATE_TOKEN` | `private_token` |
| `HTTP_USERNAME` | `http_username` |
| `HTTP_PASSWORD` | `http_password` |
| `OAUTH_TOKEN`   | `oauth_token`   |
| `JOB_TOKEN`     | `job_token`     |

## Run 

### Run from source
```bash
# setup virtual environments
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# Migrate
$ GITLAB_SRC_GROUP_ID=1234 \
  GITLAB_DEST_GROUP_ID=5678 \
  python migrate.py

# Migrate using export/import
$ GITLAB_EXPORT_IMPORT=True \
  GITLAB_SRC_GROUP_ID=1234 \
  GITLAB_DEST_GROUP_ID=5678 \
  python migrate.py

# Migrate using export/import. overwrite existing project if exists.
$ GITLAB_EXPORT_IMPORT=True \
  GITLAB_IMPORT_OVERWRITE=True \
  GITLAB_SRC_GROUP_ID=1234 \
  GITLAB_DEST_GROUP_ID=5678 \
  python migrate.py
```

Environments:
* `GITLAB_SRC_GROUP_ID`: source gitlab group id (required)
* `GITLAB_DEST_GROUP_ID`: destination gitlab group id (required)
* `GITLAB_EXPORT_IMPORT`: default value is `False`
    * `True`: migrate projects using export/import. See [Project import/export API](https://docs.gitlab.com/ce/api/project_import_export.html) for detail limitations.
    * `False`: migrate projects item by item. See [Limitations](#limitations) for detail limitations.
* `GITLAB_IMPORT_OVERWRITE`: default value is `False`
    * `True`: overwrite existing dest project. 
    * `False`: throws exception if dest project exists.

You can find Group ID at 'group overview' page.

### Run with docker image
```bash
$ GITLAB_SRC_GROUP_ID={srcGroupId} GITLAB_DEST_GROUP_ID={destGroupId} \
  docker-compose run --rm lechuckroh/gitlab-migration
```

## Limitations

### migration items
The following items are migrated if `use_export` is `False`.

|    item   |support|
|:---------:|:-----:|
| git       |   O   |
| issues    |       |
| labels    |       |
| pipelines |       |
| runners   |       |
| settings  |       |
| snippets  |       |
| wiki      |       |
