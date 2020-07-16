# gitlab-migration
Migrate GitLab repositories to other GitLab server

## Requirements
* Python 3

## Configuration
Open `python-gitlab.cfg` file and change `src` and `dest` sections.

You can create private token at [Personal Access Tokens](https://gitlab.com/profile/personal_access_tokens) menu.

See [python-gitlab Configuration](https://python-gitlab.readthedocs.io/en/stable/cli.html#configuration) for detailed configuration description.


## Run 

### Run from source
```bash
# setup virtual environments
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# Run
$ GITLAB_SRC_GROUP_ID=1234 GITLAB_DEST_GROUP_ID=5678 python migrate.py
```

* `GITLAB_SRC_GROUP_ID`: source gitlab group id
* `GITLAB_DEST_GROUP_ID`: destination gitlab group id

You can find Group ID at 'group overview' page.

### Run with docker image
```bash
$ GITLAB_SRC_GROUP_ID={srcGroupId} GITLAB_DEST_GROUP_ID={destGroupId} \
  docker-compose run --rm lechuckroh/gitlab-migration
```


## Supported migration items
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
