# -*- coding: utf-8 -*-

import os
import re
import json
import time
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup, SoupStrainer
from urllib import parse



def _dumpDict(aDict, filePath):
    with open(filePath, mode='w+') as f:
        json.dump(aDict, f, indent=4)


def _loadDict(filePath):
    with open(filePath, mode='r') as f:
        return json.load(f)


class EPFDownloader(object):

    EPF_FILE_PATERN = r'.*\d{8}\.tbz$'
    EPF_APPLICATION_FILE_PATERN = r'application.*\.tbz$'
    EPF_APPLICATION_DIR_PATERN = r'itunes\d{8}\/'
    EPF_DATE_FORMAT = "%d-%b-%Y %H:%M"

    def __init__(self, username, password, target_dir):
        self.username = username
        self.password = password
        self.target_dir = target_dir
        self.config_path = "%s/epf_downloader_config.json" % self.target_dir

        if not os.path.exists(self.config_path):
            self.options = dict(downloads=[])
            _dumpDict(self.options, self.config_path)
        else:
            self.options = _loadDict(self.config_path)

    def perform_download(self):
        raise NotImplementedError()

    def download_files(self):
        self.perform_download()


    def files_available(self, epf_url):
        directory_list = requests.get(epf_url, auth=HTTPBasicAuth(self.username, self.password)).text
        path = self._get_dir_name(directory_list)
        epf_url = parse.urljoin(epf_url, path[0][0])

        directory_list = requests.get(epf_url, auth=HTTPBasicAuth(self.username, self.password)).text
        return path, self._get_filenames(directory_list)

    def _get_dir_name(self, html):
        dirs = []
        for table_line in BeautifulSoup(html, parseOnlyThese=SoupStrainer('tr')):
            line = table_line.findAll("td")
            if line:
                dirs.append((line[1].a.get('href'), time.strptime(line[2].text.strip(), self.EPF_DATE_FORMAT)))
        return [dirname for dirname in dirs if self._match_dirname(dirname[0])]

    def _match_dirname(self, dirname):
        pattern = re.compile(self.EPF_APPLICATION_DIR_PATERN)
        return pattern.match(dirname)

    def _get_filenames(self, html):
        files = []
        for table_line in BeautifulSoup(html, parseOnlyThese=SoupStrainer('tr')):
            line = table_line.findAll("td")
            if line:
                files.append((line[1].a.get('href'), time.strptime(line[2].text.strip(), self.EPF_DATE_FORMAT)))
        return [filename for filename in files if self._match_filename(filename[0])]

    def _match_filename(self, filename):
        pattern = re.compile(self.EPF_APPLICATION_FILE_PATERN)
        return pattern.match(filename)
