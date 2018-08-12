import json
import re


def select_empty_Url():
    url = []
    reg = r'"url": "(.*?)", "goods_info": "(.*?)",'
    i = 0
    with open('vip.log', 'r') as f:
        while True:
            data = f.readline()
            if not data:
                break
            if data.startswith('{'):
                data = data.replace("'", '"')
                d = re.search(reg, data)
                try:
                    if not d.group(2):
                        url.append(d.group(1))
                        i += 1
                        print(i)
                    else:
                        continue
                except:
                    break
            else:
                continue

    with open('sec_url.dt', 'w') as sf:
        for e in url:
            sf.write(e + '\n')


# try:
#     select_empty_Url()
# except Exception as e:
#     print(e) 

