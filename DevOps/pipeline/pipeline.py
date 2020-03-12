#!/usr/bin/env python3

"""
pipeline -- Command-line tool for uploading releases to GitHub

References:
  * https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/
  * https://developer.github.com/v3/repos/releases/
"""

import base64
import datetime
import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.parse import urljoin
import re
from typing import Dict

import click
import github
import jwt

logging.basicConfig(format='[{asctime}][{levelname}]: {message}', style='{',
                    level=logging.INFO)

SOFTWARE_PAGE = 'software/index.html'
PR_COMMIT_TEMPLATE = 'Software Release "{tag}"'
PR_BODY_TEMPLATE = """
| Artifact Name | Size (KiB) | Content Type |
|-------------- | ---------- | ------------ |
""".strip()
ARTIFACTS = {
    'dawn': {
        re.compile(r'^dawn-win32'): 'dawn-win32-url',
        re.compile(r'^dawn-darwin'): 'dawn-macos-url',
        re.compile(r'^dawn-linux'): 'dawn-linux-url',
    },
    'runtime': {
        re.compile(r'^frankfurter-update'): 'runtime-url',
    }
}
TAG_PATTERN = re.compile(r'^(?P<project>[a-z]+)/(?P<version>[\d\.]+)')


class GitHubApp:
    api_base_url = 'https://api.github.com'
    token_lifetime = 10*60  # 10 minutes
    algorithm = 'RS256'
    default_accept = 'application/vnd.github.machine-man-preview+json'

    def __init__(self, app_id: str, key_file_path: str):
        self.app_id = app_id
        with open(key_file_path, 'rb') as key_file:
            self.key = key_file.read()

    def generate_client_token(self) -> str:
        now = int(datetime.datetime.now().timestamp())
        return jwt.encode({
            'iat': now,                         # 'Issued at' time
            'exp': now + self.token_lifetime,   # Expiry
            'iss': self.app_id,
        }, self.key, algorithm=self.algorithm).decode('utf-8')

    def make_request(self, url: str, data: Dict = None, headers: Dict = None,
                     method: str = 'GET'):
        headers, data = headers or {}, data or {}
        header_attrs = list(map(str.casefold, headers))
        if 'Accept'.casefold() not in header_attrs:
            headers['Accept'] = self.default_accept
        if 'Authorization'.casefold() not in header_attrs and hasattr(self, 'access_token'):
            headers['Authorization'] = self.access_token
        request = Request(url, method=method, data=data, headers=headers)
        with urlopen(request) as response:
            return json.load(response)

    def retrieve_access_token(self, owner: str, repo: str) -> str:
        install_url = urljoin(self.api_base_url, f'/repos/{owner}/{repo}/installation')
        headers = {'Authorization': f'Bearer {self.generate_client_token()}'}
        access_url = self.make_request(install_url, headers=headers)['access_tokens_url']
        return self.make_request(access_url, headers=headers, method='POST')['token']

    def get_repo(self, owner: str, repo: str) -> github.Repository:
        access_token = self.retrieve_access_token(owner, repo)
        return github.Github(access_token).get_repo(f'{owner}/{repo}')


def get_commit_from_tag(repo: github.Repository, target_tag: str) -> github.GitCommit:
    for tag in repo.get_tags():
        if tag.name == target_tag:
            return tag.commit


def branch_to_ref(branch: str) -> str:
    return 'refs/heads/' + branch


def artifact_label(name: str) -> str:
    return os.path.splitext(name)[0]


def create_release(repo: github.Repository, tag: str, artifacts_dir: str,
                   draft: bool = False, prerelease: bool = False):
    commit = get_commit_from_tag(repo, tag)
    if not commit:
        logging.warning(f'Unable to find tag "{tag}". Skipping release.')
        return None, []
    release = repo.create_git_release(tag, tag, commit.commit.message,
                                      draft=draft, prerelease=prerelease)
    artifacts = []
    for filename in os.listdir(artifacts_dir):
        artifact = os.path.join(artifacts_dir, filename)
        if os.path.isfile(artifact):
            artifact = release.upload_asset(artifact, label=artifact_label(filename))
            artifacts.append(artifact)
            logging.info(f'Uploading artifact "{artifact.name}" ...')
        else:
            logging.warning(f'Cannot upload directory "{artifact}". Skipping.')
    logging.info(f'Created release for tag "{tag}".')
    return release, artifacts


def replace_page_key(contents: str, key: str, value: str) -> str:
    return re.sub(r'({0}):\s*.*\n'.format(key), r'\1: {0}\n'.format(value), contents)


def make_pull_request(repo, tag, artifacts, src_branch='master'):
    branch = repo.get_branch(src_branch)
    page = repo.get_file_contents(SOFTWARE_PAGE, ref=branch_to_ref(src_branch))
    contents = old_contents = base64.b64decode(page.content.encode('utf-8')).decode('utf-8')

    tag_match, pr_body = TAG_PATTERN.match(tag), PR_BODY_TEMPLATE
    if not tag_match:
        logging.error('Tag does not match the expected pattern. Aborting pull request.')
        return
    project, version = tag_match.group('project'), tag_match.group('version')
    for label_pattern, page_key in ARTIFACTS.get(project, {}).items():
        for artifact in artifacts:
            label = artifact.label or artifact_label(artifact.name)
            if label_pattern.match(label):
                contents = replace_page_key(contents, page_key, artifact.browser_download_url)
                pr_body += (f'\n| [`{artifact.name}`]({artifact.browser_download_url}) '
                            f'| {round(artifact.size/1024, 1)} '
                            f'| `{artifact.content_type}` |')
                break
        else:
            logging.warning(f'Unable to find artifact for "{page_key}". Skipping.')

    today = datetime.date.today().strftime('%B %d, %Y')
    contents = replace_page_key(contents, f'{project}-latest-ver', version)
    contents = replace_page_key(contents, f'{project}-last-update', today)

    if contents != old_contents:
        ref = repo.create_git_ref(branch_to_ref(tag), sha=branch.commit.sha)
        message = PR_COMMIT_TEMPLATE.format(tag=tag)
        repo.update_file(SOFTWARE_PAGE, message, contents.encode('utf-8'), page.sha, branch=tag)
        pr = repo.create_pull(title=message, body=pr_body, base=src_branch, head=tag)
        logging.info(f'Created pull request #{pr.id} for "{repo.owner.login}/{repo.name}".')
        return pr


@click.command()
@click.option('-k', '--key-file', help='Path to GitHub Apps private key file', required=True)
@click.option('-a', '--app-id', envvar='APP_ID', help='GitHub App ID', required=True)
@click.option('-d', '--artifacts-dir', help='Artifacts directory', required=True,
              type=click.Path(file_okay=False, dir_okay=True, exists=True))
@click.option('-t', '--tag', help='Tag name', required=True)
@click.option('-p', '--prerelease', help='Prerelease', is_flag=True)
@click.option('-x', '--draft', help='Draft release', is_flag=True)
@click.option('-w', '--website', help='If set, submit a PR to update the website', is_flag=True)
def cli(key_file, app_id, artifacts_dir, tag, prerelease, draft, website):
    """ Command-line tool for uploading releases to GitHub and updating the software page links. """
    app = GitHubApp(app_id, key_file)
    piecentral_repo = app.get_repo('pioneers', 'PieCentral')
    release, artifacts = create_release(piecentral_repo, tag, artifacts_dir, draft=draft, prerelease=prerelease)
    if release and website:
        website_repo = app.get_repo('pioneers', 'website')
        make_pull_request(website_repo, tag, artifacts)


if __name__ == '__main__':
    cli()
