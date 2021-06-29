# -*- coding: utf-8 -*-

import argparse

import EPFDownloader.epf_downloader as epf_downloader
from urlgrabber import urlgrab
from urlgrabber.progress import text_progress_meter
from urllib import parse


class EPFDowloaderFull(epf_downloader.EPFDownloader):

#    EPF_FULL_URL = "https://%s:%s@feeds.itunes.apple.com/feeds/epf/v3/full/current/"
    EPF_FULL_URL_V4 = "https://%s:%s@feeds.itunes.apple.com/feeds/epf/v4/current/current/"

    def perform_download(self):
        to_download = set()
        path, epf_file_infos = self.files_available(self.EPF_FULL_URL_V4)
        if path[0][0] not in self.options["downloads"]:
            for epf_file_info in epf_file_infos:
                epf_file, epf_file_date = epf_file_info
                to_download.add(epf_file)
            self.options["downloads"].append(path[0][0])

        for file_to_download in to_download:
            print("find new instance")
            print("download de %s" % file_to_download)
            try:
                self._download_file(path[0][0], file_to_download)
                epf_downloader._dumpDict(self.options, self.config_path)
            except Exception as e:
                print(e)
                print("error no download %s" % file_to_download)

    def _download_file(self, path, filename):
        url = "%s%s%s" % (self.EPF_FULL_URL_V4 % (self.username, self.password), path, filename)
        urlgrab(url, "%s/%s" % (self.target_dir, filename), progress_obj=text_progress_meter(), reget="simple", retry=0)


def main():

    parser = argparse.ArgumentParser(description='Import iTunes database into elasticsearch.')
    parser.add_argument('--user', required=True, help='EPF username.')
    parser.add_argument('--password', required=True, help='EPF password.')
    parser.add_argument('--target_dir', required=True, help='Download target directory.')

    args = parser.parse_args()
    username = args.user
    password = args.password
    target_dir = args.target_dir

    EPFDowloaderFull(username=username, password=password, target_dir=target_dir).download_files()

if __name__ == "__main__":
    main()
