import datetime

import requests
from loguru import logger
import json
import pymongo
import redis
import time
import yt_dlp
import copy
import threading


class TiktokAuthor:
    def __init__(self):
        self.base_author_url = 'https://www.tiktok.com/@'
        self.downlaod_url = 'https://www.tikwm.com/video/media/play/{id}.mp4'  # tiktok下载链接
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Don't download videos, just get info
            'dump_single_json': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.tiktok.com/'
            }
        }

    def get_author_videos(self):
        """获取博主视频"""
        author_name = 'mysticwild'
        author_url = self.base_author_url + author_name

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                result = ydl.extract_info(author_url, download=False)
                if result and 'entries' in result:
                    videos = result['entries']
                    logger.info(f"{author_name} 共有 {len(videos)} 个视频")
                    for idx, video in enumerate(videos, 1):
                        id = video['id']
                        download_url = self.downlaod_url.format(id=id)
                        logger.info(f'id 为 {id}， {download_url}')

        except Exception as e:
            logger.error(f"Error getting user videos: {str(e)}")


def main():
    """tiktok根据博主抓取"""
    tiktok = TiktokAuthor()
    tiktok.get_author_videos()


if __name__ == '__main__':
    main()
