import requests
import time

from loguru import logger

from requests.exceptions import ProxyError


class KuaiShou:
    def __init__(self):
        self.url = 'https://www.kuaishou.com/graphql'
        self.base_url = 'https://www.kuaishou.com/short-video/'  # 加上id
        self.data = {
            "operationName": "brilliantTypeDataQuery",
            "variables": {
                "hotChannelId": "00",
                "page": "brilliant",
                "pcursor": "1"

            },
          "query": "fragment photoContent on PhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment recoPhotoFragment on recoPhotoEntity {\n  __typename\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  riskTagContent\n  riskTagUrl\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    ...recoPhotoFragment\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment photoResult on PhotoResult {\n  result\n  llsid\n  expTag\n  serverExpTag\n  pcursor\n  feeds {\n    ...feedContent\n    __typename\n  }\n  webPageArea\n  __typename\n}\n\nquery brilliantTypeDataQuery($pcursor: String, $hotChannelId: String, $page: String, $webPageArea: String) {\n  brilliantTypeData(pcursor: $pcursor, hotChannelId: $hotChannelId, page: $page, webPageArea: $webPageArea) {\n    ...photoResult\n    __typename\n  }\n}\n"}
        self.headers = {
            # "Cookie": 'kpf=PC_WEB; clientid=3; did=web_a9e7580aea6c3d6d45f07eb926396c50; kpn=KUAISHOU_VISION; userId=4438926152; kuaishou.server.webday7_st=ChprdWFpc2hvdS5zZXJ2ZXIud2ViZGF5Ny5zdBKwARrGbBXI9ryftacX_icBpRon76NCmLpq3-tLCYbq8wggcNFceT7SkjoK3wx2m746shgP87RqoTIF0KFSM1z2Af3hm_dfk1xqk-MWGchKTQG6Fsk4I2BZCn9MNbmZzVPCKCGBUqnLL2HvEwhzCNiQxHGGlw6lP5Odiz9WsdrQEIdt7goIVLIrIdRfDGeFLKN7PZZ91XwUqO3-29UdlWmDvwcP7vwsuqlRikXkSYknvMITGhJ9HT6MbGrfdP_lNnYr-H8iHsEiIO9wqVPyOIUVbj6tqrco74beB1NWAM_XHOqWi2ge6d0YKAUwAQ; kuaishou.server.webday7_ph=af3848b074ef4d58648ae1842cdc14edfee3',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '1839',
            'Content-Type': 'application/json',
            'Host': 'www.kuaishou.com',
            'Origin': 'https://www.kuaishou.com',
            'Referer': 'https://www.kuaishou.com/brilliant',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }

    def run(self):
        index = 1
        while True:
            logger.info(f'index = {index}')
            # response = requests.post(self.url, json=self.data, headers=self.headers)
            response = self.retry_request()
            if response.status_code == 200:
                data_json = response.json()
                results = data_json['data']['brilliantTypeData']['feeds']
                print(results)
            else:
                logger.error(f'错误响应码为 {response.status_code}')
            index += 1

            if index > 30:
                index = 1
                logger.info(f'休眠')
                time.sleep(1 * 60)

    def retry_request(self, retries=5):
        """使用代理"""
        try:

            response = requests.post(self.url, json=self.data, headers=self.headers, timeout=10)
            if response.status_code == 200:
                """响应码为200才给返回"""
                return response

        except ProxyError as e:
            logger.error(f"代理异常: {e}")
            logger.error(f'重试请求 {str(e)}')
            if retries > 0:
                return self.retry_request()
                # return self.retry_request(url,data, retries=retries-1)
            else:
                return None

        except Exception as e:
            logger.error(f'重试请求 {str(e)}')
            if retries > 0:
                return self.retry_request()
                # return self.retry_request(url, data, retries=retries-1)
            else:
                return None


def main():
    """快手短视频抓取"""
    kuaishou = KuaiShou()
    kuaishou.run()


if __name__ == '__main__':
    main()
