#!/usr/bin/env python
#encoding=utf-8
# python3.5


__author__ = 'Tim Liu'
__date__ = '2017/7/20 15:25'

import requests
import re
import os
import codecs
import time
import threading
import datetime

from bs4 import BeautifulSoup

from os.path import basename
import logging
import logging.config

# 返回一个tuple元组的值：(Watch,Star, Fork) ,注意顺序
def markdown_add_stars(url):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36' }
    html = requests.get(url, headers=headers)

    # print(md_txt.text)
    soup = BeautifulSoup(html.text, "html.parser")
    # 使用css解析器
    '''
    <ul class="pagehead-actions">
  <li>
	<a ...>
		Watch
	</a>
    <a class="social-count" href="/larkjs/lark/watchers"
     aria-label="23 users are watching this repository">
    23
    </a>
  </li>

  <li>
    <a ...>
		Star
	</a>
    <a class="social-count js-social-count" href="/larkjs/lark/stargazers"
      aria-label="142 users starred this repository">
      142
    </a>
  </li>

  <li>
	<a ...>
		Fork
	</a>
    <a href="/larkjs/lark/network" class="social-count"
       aria-label="18 users forked this repository">
      18
    </a>
  </li>
</ul>
    '''
    a_list = soup.select("ul.pagehead-actions > li > a.social-count" )
    if not a_list:
        return None
    watchers = a_list[0].text.strip()
    stargazers = a_list[1].text.strip()
    network = a_list[2].text.strip()

    # print(watchers)
    # print(stargazers)
    # print(network)
    return (watchers,stargazers, network)


def md_parse_add_stars(old_file_path):
    start = time.time()
    # print(u"{0}============>bengin...".format(old_file_path))

    old_name = basename(old_file_path)
    # 一个执行开始标志,2个md文件同时多线程后，用了没有意义了
    # logger.error(u"\n======================== {0} is beginning ========================\n".format(old_name))

    new_txt_path = '%s/data_files/new_%s_%s' %(os.getcwd(), datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S'), old_name)
    print(new_txt_path)

    new_file = codecs.open(new_txt_path, "a", "utf-8")

    old_file = codecs.open(old_file_path, "r", "utf-8")

    i = 0
    for line in old_file:
        i += 1
        if i % 20 == 0: # 每20行把缓冲区内容写入文件中
            new_file.flush()


        # print(line)
        # 用正则取出数字
        # line = " * [my-git](https://github.COM/xirong/my-git/)有关 git 的学习资料"
        # 特例1：这是一个特例，注意其贪婪匹配
        # line = " * [gogs](https://github.com/gogits/gogs) - Gogs (Go Git Service) 是一款极易搭建的自助 Git 服务，由[无闻](https://github.com/Unknwon)编写并开源在GitHub。"
        # 特例2:
        # line = "* [octokit](https://github.com/octokit) - GitHub API的官方封装库"
        # 特例3： url已经对应的库已经删除了: https://github.com/menxu/MusicPlayert
        # line = "* [MusicPlayert](https://github.com/menxu/MusicPlayert) - MusicPlayert本地音乐播放+音乐信息显示+在线歌词搜索显示（千千静听服务器）。"


        # 这里有忽略大小写：re.I, .*?:非贪婪匹配模式,3两个地方要，否则出现上面  特例1 的贪婪情况, github.com 项目的地址格式：https://github.com/xxx/xxxx
        pattern = re.compile(r'\s*\*\s*\[(?P<title>.*?)\]\s*\((?P<url>https://github.com/.*?/.*?)\).*', re.I)
        match = pattern.match(line)
        # match = re.match(r'\s*\*\s*\[(?P<title>.*)\]\s*\((?P<url>https://github.com/.*)\)',txt)
        if match:
            # title = match.group("title")
            http_url = match.group("url")
            stars_tuple = markdown_add_stars(http_url)
            #print(stars_tuple)
            if stars_tuple:
                stars_txt = " ---- (Star:{0}) (Fork:{1}) (Watch:{2})".format(stars_tuple[1], stars_tuple[2], stars_tuple[0])
                print(http_url)
                print(stars_txt)
                # 去掉原来旧的："  (Star:486) (Fork:46) (Watch:12)  "   例如： * [FileExplorer](https://github.com/Augustyniak/FileExplorer) 完整的文件资源管理器组件.  (Star:486) (Fork:46) (Watch:12)
                match_old_stars = re.match(r'(?P<no_stars_info>.*?)(?P<stars_info>\s*----\s*\(Star:.*?\)\s*\(Fork:.*?\)\s*\(Watch:.*?\)\s*)',line.strip('\n'))
                if match_old_stars: # 说明有旧的star、Fork、Watch信息了： 例如：  (Star:486) (Fork:46) (Watch:12)
                    line_no_stars_info = match_old_stars.group("no_stars_info")
                    #print("有旧的star信息了，头部：{}".format(line_no_stars_info ) )
                    #print("有旧的star信息了，旧star信息：{}".format(match_old_stars.group("stars_info")))
                    new_file.write(u"{0}  {1}  \n".format(line_no_stars_info, stars_txt) )

                else:
                    # 记得去掉回车换行
                    new_file.write(u"{0}  {1}  \n".format(line.strip('\n'), stars_txt) )

            else:
                print("此GitHub的url的项目已经不存在：{0}".format(http_url))
                # 失效的github的url项目地址，写入logs/stars_url_error.log 日志文件里面
                logger.error("{0}:  {1}".format(old_name,http_url))
                new_file.write(u"{0}".format(line))
        else:
            new_file.write(u"{0}".format(line))


    old_file.close()
    new_file.close()

    end = time.time()
    print(u"{0}============>end...".format(old_file_path))
    print(u"{0}本任务执行时间：{1}秒".format(old_file_path, end-start))




if __name__ == '__main__':

    # error级别的日志文件：stars_url_error.log,并且在屏幕上输出info级别的log
    logging.config.fileConfig("conf/logger_stars.conf")
    logger = logging.getLogger("exampleError")
    # logs/start_url_error.log :文件里面做个时间开始标记
    logger.error(u"\n\n================={0}=================".format(datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S')))


     #  'https://github.com/Tim9Liu9/TimLiu-iOS/blob/master/README.md';
    # md_parse_add_stars("data_files/README.md")
    # md_parse_add_stars("data_files/Swift.md")

    # 多线程执行
    threads = []

    tr = threading.Thread(target=md_parse_add_stars,args=("data_files/README.md",))
    threads.append(tr)


    ts = threading.Thread(target=md_parse_add_stars,args=("data_files/Swift.md",))
    threads.append(ts)

    for t in threads:
        t.start()
    for t in threads:
        t.join()



















