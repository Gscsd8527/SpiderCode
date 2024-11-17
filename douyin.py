import json
from loguru import logger
import random
import requests
import re
import urllib
import execjs
import urllib.parse

COMMON_PARAMS = {
    'device_platform': 'webapp',
    'aid': '6383',
    'channel': 'channel_pc_web',
    'update_version_code': '170400',
    'pc_client_type': '1', # Windows
    'version_code': '190500',
    'version_name': '19.5.0',
    'cookie_enabled': 'true',
    'screen_width': '2560', # from cookie dy_swidth
    'screen_height': '1440', # from cookie dy_sheight
    'browser_language': 'zh-CN',
    'browser_platform': 'Win32',
    'browser_name': 'Chrome',
    'browser_version': '126.0.0.0',
    'browser_online': 'true',
    'engine_name': 'Blink',
    'engine_version': '126.0.0.0',
    'os_name': 'Windows',
    'os_version': '10',
    'cpu_core_num': '24',   # device_web_cpu_core
    'device_memory': '8',   # device_web_memory_size
    'platform': 'PC',
    'downlink': '10',
    'effective_type': '4g',
    'round_trip_time': '50',
    # 'webid': '7378325321550546458',   # from doc
    # 'verifyFp': 'verify_lx6xgiix_cde2e4d7_7a43_e749_7cda_b5e7c149c780',   # from cookie s_v_web_id
    # 'fp': 'verify_lx6xgiix_cde2e4d7_7a43_e749_7cda_b5e7c149c780', # from cookie s_v_web_id
    # 'msToken': 'hfAykirauBE-RKDm8bF2o2_cKuSdwHsbGXjJBuo8s3w9n46-Tu0CtxX7-iiZWZ8D7mRUAmRAkeiaU35194AJehc9u6_mei3Q9s_LABQuoANQmbd81DDS3wuA5u9UVIo%3D',  # from cookie msToken
    # 'a_bogus': 'xJRwQfLfDkdsgDyh54OLfY3q66M3YQnV0trEMD2f5V3WF639HMPh9exLx-TvU6DjNs%2FDIeEjy4haT3nprQVH8qw39W4x%2F2CgQ6h0t-P2so0j53iJCLgmE0hE4vj3SlF85XNAiOk0y7ICKY00AInymhK4bfebY7Y6i6tryE%3D%3D' # sign
}

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "sec-ch-ua-platform": "Windows",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "referer": "https://www.douyin.com/?recommend=1",
    "priority": "u=1, i",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "accept": "application/json, text/plain, */*",
    "dnt": "1",
}

DOUYIN_SIGN = execjs.compile(open('douyin.js', encoding='utf-8').read())


class Douyin:
    def __init__(self):
        self.base_url = 'https://www.douyin.com'
        self.cookie = '自己抖音的cookie'

    def get_video_id_data(self, id):
        """传入video id获取数据"""
        logger.info(f'抓取视频ID： {id}')
        params = {"aweme_id": id}
        headers = {"cookie": self.cookie}
        resp, succ = self.common_request('/aweme/v1/web/aweme/detail/', params, headers)
        if not succ:
            return resp, succ
        ret = resp.get('aweme_detail', {})
        # print(ret)
        print(json.dumps(ret, ensure_ascii=False))

    def get_uesr_data(self, user_id):
        """获取用户下所有视频"""
        videos = self.get_user_all_video(id=user_id)
        logger.info(f'videos = {len(videos)}')

    def get_user_all_video(self, id: str):
        headers = {"cookie": self.cookie}
        max_cursor = 0
        has_more = True
        videos = []
        index = 1
        while has_more:
            logger.info(f'请求第 {index} 次')
            params = {"publish_video_strategy_type": 2, "max_cursor": max_cursor, "locate_query": False,
                      'show_live_replay_strategy': 1, 'need_time_list': 0, 'time_list_query': 0, 'whale_cut_token': '',
                      'count': 18, "sec_user_id": id}
            resp, succ = self.common_request('/aweme/v1/web/aweme/post/', params, headers)
            if not succ:
                return videos
            for _ in resp.get('aweme_list', []):
                logger.info(f'aweme_id = {_["aweme_id"]}  desc = {_["desc"]}')
            videos.extend(resp.get('aweme_list', []))
            max_cursor = resp.get('max_cursor', 0)
            has_more = resp.get('has_more', 0) == 1
            index += 1
        return videos

    def common_request(self, url, params, headers):
        url = f'{self.base_url}{url}'
        params.update(COMMON_PARAMS)
        headers.update(COMMON_HEADERS)
        params = self.deal_params(params, headers)
        query = '&'.join([f'{k}={urllib.parse.quote(str(v))}' for k, v in params.items()])
        call_name = 'sign_datail'
        if 'reply' in url:
            call_name = 'sign_reply'
        a_bogus = DOUYIN_SIGN.call(call_name, query, headers["User-Agent"])
        params["a_bogus"] = a_bogus

        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200 or response.text == '':

            return {}, False
        if response.json().get('status_code', 0) != 0:

            return response.json(), False

        return response.json(), True

    def deal_params(self, params: dict, headers: dict) -> dict:
        cookie = headers.get('cookie') or headers.get('Cookie')
        if not cookie:
            return params
        cookie_dict = self.cookies_to_dict(cookie)
        params['msToken'] = self.get_ms_token()
        params['screen_width'] = cookie_dict.get('dy_swidth', 2560)
        params['screen_height'] = cookie_dict.get('dy_sheight', 1440)
        params['cpu_core_num'] = cookie_dict.get('device_web_cpu_core', 24)
        params['device_memory'] = cookie_dict.get('device_web_memory_size', 8)
        params['verifyFp'] = cookie_dict.get('s_v_web_id', None)
        params['fp'] = cookie_dict.get('s_v_web_id', None)
        params['webid'] = self.get_webid(headers)
        return params

    def cookies_to_dict(self, cookie_string) -> dict:
        cookies = cookie_string.split('; ')
        cookie_dict = {}
        for cookie in cookies:
            if cookie == '' or cookie == 'douyin.com':
                continue
            key, value = cookie.split('=', 1)[0], cookie.split('=', 1)[1]
            cookie_dict[key] = value
        return cookie_dict

    @staticmethod
    def get_ms_token(randomlength=120):
        """
        根据传入长度产生随机字符串
        """
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        length = len(base_str) - 1
        for _ in range(randomlength):
            random_str += base_str[random.randint(0, length)]
        return random_str

    @staticmethod
    def get_webid(headers: dict):
        url = 'https://www.douyin.com/?recommend=1'
        headers['sec-fetch-dest'] = 'document'
        response = requests.get(url, headers=headers)

        if response.status_code != 200 or response.text == '':
            return None
        pattern = r'\\"user_unique_id\\":\\"(\d+)\\"'
        match = re.search(pattern, response.text)
        if match:
            return match.group(1)
        return None


def main():
    """抓取抖音视频"""
    douyin = Douyin()
    # douyin.get_uesr_data('MS4wLjABAAAArK5ZriSUmPYTIE34KIDGxdGlKaHMTla08BCu6zNuCE0')
    douyin.get_video_id_data('7308941125551689012')


if __name__ == '__main__':
    main()
