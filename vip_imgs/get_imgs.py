import requests
import os
import sys
import random
import pickle
# import pdb
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]



headers = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN,zh;q=0.9",
    # "Cache-Control":"max-age=0",
    # "Connection":"keep-alive",
    # "Host":"a.vpimg4.com",
    # "If-Modified-Since":'Mon, 04 Jun 2018 13":"42":"12 GMT',
    # "If-None-Match":'W/"ce6e4654a47388ae6495ba6f00800ffd"',
    # "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "H15EK0717042RY6D"
proxyPass = "077EE9B65130A2BF"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
  "host": proxyHost,
  "port": proxyPort,
  "user": proxyUser,
  "pass": proxyPass,
}

proxies = {
    "http"  : proxyMeta,
    "https" : proxyMeta,
}


def get(url):
    global headers
    headers['User-Agent'] = random.choice(USER_AGENTS)
    s = requests.session()

    try:
        s.headers = headers
        s.proxies = proxies
        s.timeout = 20
        s.verify = False
        data = s.get(url, headers=headers)
        if data.status_code not in [200, 304]:
            print(data.status_code)
            return False
        return data.content
    except:
        return False
    finally:
        s.close()


def get_imgs():
    err = []
    try:
        start = int(sys.argv[1])
    except:
        start = 1914
    with open('/home/zwb/Documents/python_work_inDeepin/spiders/vip_imgs/products.csv') as f:
        data = f.read()
    for e in data.split('\n'):
        e = [x.replace('"', '').replace('\r', '') for x in e.split(',')]
        if int(e[0]) <= start:
            continue
        if not e[1]:
            continue
        # os.mkdir(img_path)
        img_url = list(set(e[1:]))
        for n, i in enumerate(img_url, 1):
            img_name = os.path.join(os.path.abspath('./imgs'), '%s-%s.jpg' % (e[0], n))
            # img_name = os.path.join(img_path, 'i%s.jpg' % n)

            i_dat = get(i)
            # pdb.set_trace()

            if not i_dat:
                err.append([i, img_name])
                continue
                # return False, i, img_name
            with open(img_name, 'bw') as img:
                img.write(i_dat)
    with open('err_img.dt', 'w') as f:
        pickle.dump(err, f)

get_imgs()
# print(sys.argv)
