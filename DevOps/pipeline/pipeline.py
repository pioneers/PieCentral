#!/usr/bin/env python3

"""
pipeline -- Command-line tool for uploading releases to GitHub

References:
  * https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/
  * https://developer.github.com/v3/repos/releases/
"""

import datetime
import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.parse import urljoin

import click
from github import Github
import jwt

logging.basicConfig(format='[{asctime}][{levelname}]: {message}', style='{',
                    level=logging.DEBUG)


class GitHubApp:
    """ A wrapper around the PyGithub API to support GitHub apps. """
    GITHUB_API_BASE_URL = 'https://api.github.com'
    TOKEN_LIFETIME = 10*60

    def __init__(self, owner, repo, key_file, app_id):
        self.owner, self.repo = owner, repo
        self.key_file, self.app_id = key_file, app_id

    def generate_token(self):
        now = int(datetime.datetime.now().timestamp())
        with open(self.key_file, 'rb') as key_file:
            key = key_file.read()
        return jwt.encode({
            'iat': now,                         # 'Issued at' time
            'exp': now + self.TOKEN_LIFETIME,   # Expires after 10 minutes
            'iss': self.app_id
        }, key, algorithm='RS256').decode('utf-8')

    def request_json(self, url, data=None, headers=None, method='GET'):
        header_keys = list(map(str.casefold, headers))
        if 'Accept'.casefold() not in header_keys:
            headers['Accept'] = 'application/vnd.github.machine-man-preview+json'
        if 'Authorization'.casefold() not in header_keys and hasattr(self, 'token'):
            headers['Authorization'] = self.token
        request = Request(url, method=method, data=(data or {}), headers=headers)
        logging.debug(f'{method} {url}')
        with urlopen(request) as response:
            return json.load(response)

    def retrieve_access_token(self):
        install_url = urljoin(
            self.GITHUB_API_BASE_URL,
            f'/repos/{self.owner}/{self.repo}/installation')
        headers = {'Authorization': f'Bearer {self.generate_token()}'}
        access_url = self.request_json(install_url, headers=headers)['access_tokens_url']
        self.token = self.request_json(access_url, headers=headers, method='POST')['token']
        self.client = Github(self.token).get_repo(f'{self.owner}/{self.repo}')
        return self.token

    def get_commit_from_tag(self, tag_name):
        for tag in self.client.get_tags():
            if tag.name == tag_name:
                return tag.commit

    def create_release(self, tag_name, artifacts_dir, draft=False, prerelease=False):
        assert hasattr(self, 'client')
        # Assumes tag already exists
        commit = self.get_commit_from_tag(tag_name)
        if not commit:
            raise ValueError(f'No such tag "{tag_name}"')
        release = self.client.create_git_release(tag_name, tag_name,
                                                 commit.commit.message,
                                                 draft=draft,
                                                 prerelease=prerelease)
        for filename in os.listdir(artifacts_dir):
            full_path = os.path.join(artifacts_dir, filename)
            if os.path.isfile(full_path):
                release.upload_asset(full_path)
        return release


@click.command()
@click.option('-o', '--owner', default='pioneers', help='GitHub owner')
@click.option('-r', '--repo', default='PieCentral', help='GitHub repository')
@click.option('-k', '--key-file', help='Path to GitHub Apps private key file', required=True)
@click.option('-a', '--app-id', help='GitHub App ID', required=True)
@click.option('-d', '--artifacts-dir', help='Artifacts directory', required=True)
@click.option('-t', '--tag', help='Tag name', required=True)
@click.option('-p', '--prerelease', help='Prerelease', is_flag=True)
@click.option('-x', '--draft', help='Draft release', is_flag=True)
def main(owner, repo, key_file, app_id, artifacts_dir, tag, prerelease, draft):
    app = GitHubApp(owner, repo, key_file, app_id)
    app.retrieve_access_token()
    app.create_release(tag, artifacts_dir, prerelease=prerelease, draft=draft)


if __name__ == '__main__':
    main()
