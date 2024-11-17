# @Author  : tanzhenhua
# @Email   : tan_gscsd@163.com
# @Time    : 2024/10/28 18:10
import requests
import json
import time
import copy
import datetime
from loguru import logger
import pymongo
import redis
from requests.exceptions import ProxyError
import random


class KuaishouSearch:
    def __init__(self):
        self.url = 'https://www.kuaishou.com/graphql'
        self.short_video_url = 'https://www.kuaishou.com/short-video/'  # 拼接ID
        self.author_url = 'https://www.kuaishou.com/profile/'  # 拼接ID
        self.author_body = {
            "operationName": "visionProfilePhotoList",
            "variables": {
                "userId": "3xaxicn7uwnsft4",
                "pcursor": "",
                "page": "profile"
            },
            "query": "fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment feedContentWithLiveInfo on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    livingInfo\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContentWithLiveInfo\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n"}
        self.headers = {
            'Cookie': "用户自己的cookies",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }

    def get_author_data(self, user_id):
        index = 1
        pcursor = ''
        while True:
            logger.info(f'{user_id} : {index}')
            data = copy.deepcopy(self.author_body)
            data['variables']['pcursor'] = pcursor
            data['variables']['userId'] = user_id
            if pcursor == 'no_more':
                break
            response = self.retry_request(data)
            if response.status_code == 200:
                data_json = response.json()
                print(data_json)
                pcursor = data_json['data']['visionProfilePhotoList']['pcursor']
                results = data_json['data']['visionProfilePhotoList']['feeds']
                for result in results:
                    id = result['photo']['id']
                    description = result['photo']['caption']
                    video_url = result['photo']['photoUrl']
                    print(id, description, video_url)

            index += 1

    def retry_request(self, data, retries=5):
        """使用代理"""
        try:
            response = requests.post(self.url, json=data,  headers=self.headers, timeout=10)
            if response.status_code == 200:
                """响应码为200才给返回"""
                return response
            if retries > 0:
                return self.retry_request(data)
        except ProxyError as e:
            logger.error(f"代理异常: {e}")
            # self.proxy.delete_proxy_ip(proxy)
            logger.error(f'重试请求 {str(e)}')
            if retries > 0:
                return self.retry_request(data)
                # return self.retry_request(url,data, retries=retries-1)
            else:
                return None

        except Exception as e:
            logger.error(f'重试请求 {str(e)}')
            if retries > 0:
                return self.retry_request(data)
                # return self.retry_request(url, data, retries=retries-1)
            else:
                return None

    def task1(self):
        """单个视频"""
        url = 'https://www.kuaishou.com/short-video/3xijkzynsfkh5cw'
        response = requests.get(url)
        if response.status_code == 200:
            text = response.text

    def task2(self):
        """博主"""
        id = '3xaxicn7uwnsft4'
        data = copy.deepcopy(self.author_body)
        data['variables']['userId'] = id
        response = requests.post(self.url, json=data, headers=self.headers)
        print(response.status_code)
        print(response.json())


def main():
    """快手通过ID检索"""
    kuaishou = KuaishouSearch()
    kuaishou.get_author_data('3xaxicn7uwnsft4')


if __name__ == '__main__':
    main()
