# -*- coding:utf-8 -*-
import os, json, requests, io, base64, time
from PIL import Image


class StableDiffusionApi(object):

    def __init__(self, baseURL="https://stablediffusionapi.com"):
        self.baseURL = baseURL

    def txt2img(self, prompt, negativePrompt, sampling_method='DPM++ 2M', scheduler='Karras',
                steps=30, cfg_scale=7, seed=-1, width=512, height=512):
        url = "{}/sdapi/v1/txt2img".format(self.baseURL)

        body = {
            "prompt": prompt,  # 正面提示词，包含您想要在图像中生成的内容的描述。
            "negative_prompt": negativePrompt,  # 反面提示词，包含您不想要在图像中生成的内容的描述。
            "seed": seed,
            "sampler_name": sampling_method,
            "scheduler": scheduler,
            "batch_size": 1,
            "n_iter": 1,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height
        }

        return self.postURL(url, body)

    def imageInfo(self, imagePath):
        url = "{}/sdapi/v1/png-info".format(self.baseURL)

        data = open(imagePath, 'rb').read()
        b64Str = base64.b64encode(data).decode("utf-8")
        # print(b64Str)

        body = {
            "image": b64Str
        }

        return self.postURL(url, body)

    def getKeyword(self, keyword):
        url = "https://backend-k8s.flowgpt.com/v2/chat-anonymous"

        body = json.dumps({
            "model": "gpt-3.5-turbo",
            "nsfw": False,
            "question": keyword,
            "history": [
                {
                    "role": "assistant",
                    "content": "【图片内容】一个穿着黑色夹克和牛仔裤的男人，戴着黑色帽子和太阳镜，右手拿着一支香烟，左手插在裤兜里，站在海滩上，背景是蓝天和海浪。\n\n【正向提示】A man wearing a black jacket and jeans, with a black hat and sunglasses, holding a cigarette in his right hand and his left hand in his pocket, standing on the beach with blue skies and sea waves in the background. High-quality photo of a rugged man enjoying a smoke break by the sea, capturing the sense of freedom and relaxation. Shot in high definition, this image is perfect for any project that requires a cool and laid-back vibe.\n\n【反向提示】blurred, low quality, pixelated, (unattractive), (grimy), (old man), (dark), (out of focus), (unclear), (dirty), ((extra arm)), ((extra leg)), ((extra nose)), ((extra mouth)), (out of frame), (bad composition), (too bright), (too dark), ((extra cigarette)), ((extra hand)), (poor lighting), (bad color grading), (red-eyed), (morphed face), (unnatural posture), (awkward pose), (frozen animation), (poorly photoshopped), (low-res), (bad framing), (insipid)\n\n【参数】Sampling method: Euler; Sampling steps: 20; CFG Scale: 6; Seed: 83592794; 最优长宽比: 16:9"
                }
            ],
            "system": "从现在开始你将扮演一个stable diffusion的提示词工程师，你的任务是帮助我设计stable diffusion的文生图提示词。你需要按照如下流程完成工作。1、我将给你发送一段图片情景，你需要将这段图片情景更加丰富和具象生成一段图片描述。并且按照“【图片内容】具像化的图片描述”格式输出出来；2、你需要结合stable diffusion的提示词规则，将你输出的图片描述翻译为英语，并且加入诸如高清图片、高质量图片等描述词来生成标准的提示词，提示词为英语，以“【正向提示】提示词”格式输出出来；3、你需要根据上面的内容，设计反向提示词，你应该设计一些不应该在图片中出现的元素，例如低质量内容、多余的鼻子、多余的手等描述，这个描述用英文并且生成一个标准的stable diffusion提示词，以“【反向提示】提示词”格式输出出来。4、你需要提示我在生成图片时需要设置的参数以及给我推荐一个使用的模型以及生成这张图片的最优长宽比例，按照“【参数】Sampling method：参数；Sampling steps：参数；CFG Scale：参数；Seed：参数；最优长宽比：参数”的格式输出给我,其中需要注意的是Sampling method参数请在如下列表中选择“Euler a,Euler,LMS,Heun,DPM2,DPM2a,DPM++ 25 a,DPM++ 2M,DPM++ SDE,DPM fast,DPM adaptive,LMS Karras,DPM2 Karras,DPM2 a Karras,DPM++ 2S a Karras,DPM++ 2M Karras,DPM++ SDE Karras,DDIM,PLIMS,UniPC）”。例如：我发送：一个二战时期的护士。你回复：\n【图片内容】一个穿着二战期间德国护士服的护士，手里拿着一个酒瓶，带着听诊器坐在附近的桌子上，衣服是白色的，背后有桌子。\n【正向提示】A nurse wearing a German nurse's uniform during World War II, holding a wine bottle and a stethoscope, sat on a nearby table with white clothes and a table behind,full shot body photo of the most beautiful artwork in the world featuring ww2 nurse holding a liquor bottle sitting on a desk nearby, smiling, freckles, white outfit, nostalgia, sexy, stethoscope, heart professional majestic oil painting by Ed Blinkey, Atey Ghailan, Studio Ghibli, by Jeremy Mann, Greg Manchess, Antonio Moro, trending on ArtStation, trending on CGSociety, Intricate, High Detail, Sharp focus, dramatic, photorealistic painting art by midjourney and greg rutkowski；【反向提示】cartoon, 3d, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), wierd colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy, 3d rende；\n【参数】Sampling method：DPM++ 2M Karras；Sampling steps：20；CFG Scale：7；Seed：639249185；最优长宽比：3:4 现在我的第一个图片场景如下：一个海边抽烟的男人",
            "temperature": 0.7,
            "promptId": "SNTqb0Xo0KlfudbB2z2A-",
            "documentIds": [],
            "chatFileDocumentIds": [],
            "generateImage": False,
            "generateAudio": False
        })

        headers = {'Content-Type': 'application/json',
                   'Origin': 'https://flowgpt.com',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                   'X-Lang': 'chinese',
                   'Sec-Ch-Ua-Platform': '"Windows"',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                   }
        try:
            response = requests.post(url, data=body, headers=headers, timeout=10)
            data = response.text
            print("url", url)
            print("response", data)
            return json.loads(data)
        except Exception as e:
            print("Exception", e)

    def saveFromLocalImages(self, result, savePath="tmp"):

        result = json.loads(result)
        index = 0
        for image in result['images']:
            # image = Image.open(io.BytesIO(base64.b64decode(image.split(",", 1)[0])))
            image = Image.open(io.BytesIO(base64.b64decode(image)))
            image.save("{}/{}.png".format(savePath, index))
            index += 1

    def downloadImages(self, result, savePath="tmp"):

        index = 0
        id = result["id"]
        for imageURL in result['output']:
            imageData = requests.get(imageURL).content
            open("{}/{}_{}.png".format(savePath, id, index), 'wb').write(imageData)

            index += 1

    def postURL(self, url, body, timeout=600):
        try:
            # proxies = {"http": None, "https": None}
            response = requests.post(url, json=body, timeout=timeout)
            data = response.text
            # print("request", url, body)
            # print("response", data)
            return data
        except Exception as e:
            print("Exception", url, e)


def formatTime(timestamp, format="%Y%m%d %H:%M:%S") -> str:
    t = time.localtime(timestamp)
    return time.strftime(format, t)


def logTime(tag=""):
    print(tag, formatTime(time.time()))


def testApi():
    width = 512
    height = 512

    imagePath = "E:\\youtube\\test"
    api = StableDiffusionApi(baseURL="http://127.0.0.1:7860")

    logTime("Start")
    # , <lora:HANFU:0.6>
    prompt = "(chinese traditional minimalism:1.3), Close-up Portrait, Left View, Chinese eenchanting Maiden, Charming smile, solo,1girl, beautiful ,elegant, pink color matching, white background, hair, hair accessories, earrings,"
    negativePrompt = "(worst quality:2),(low quality:2),(normal quality:2),lowres,watermark,ng_deepnegative_v1_75t EasyNegative badhandv4, dark stroke, bad facial features, thinning hair,nsfw"

    result = api.txt2img(prompt, negativePrompt, seed=2109842228, width=width, height=height)
    api.saveFromLocalImages(result, savePath=imagePath)
    # info = api.imageInfo(imagePath=f"{imagePath}/0.png")
    # print(info)
    # api.getKeyword("一个帅气的古装男子")
    logTime("End")
    # api.imageInfo("{}/0.png".format(imagePath))


if __name__ == "__main__":
    testApi()
