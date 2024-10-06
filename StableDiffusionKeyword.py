import os, requests, json, time


def writeFile(path, data, mode="w"):
    with open(path, mode, encoding='utf-8') as f:
        f.write(data)
        f.close()


def doGet(url):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.content.decode('utf-8')
        print("url", url)
        # print("response", data)
        return data
    except Exception as e:
        print("Exception", e)
        return None


proxy = "http://172.30.240.1:1081"
os.environ["http_proxy"] = proxy
os.environ["https_proxy"] = proxy

savePath = "E:\\youtube\\sddownloads"
index = 0
url = "https://civitai.com/api/v1/images?limit=200"

while True:
    f = f'{savePath}\\{index}.json'
    print(f)
    fileExists = os.path.exists(f) and os.path.isfile(f)
    if fileExists:
        data = open(f, encoding='utf-8').read()
    else:
        data = doGet(url)
        time.sleep(1.2)

    if data is not None:
        result = json.loads(data)
        url = result['metadata']['nextPage']
        print("nextPage", url)

        if not fileExists:
            writeFile(f, data)
        index += 1
