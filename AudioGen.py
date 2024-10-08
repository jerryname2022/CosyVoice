import os, logging, sys, torchaudio, chardet, subprocess

from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav
from utils.file_utils import read_lines, write_to_file

logging.getLogger('matplotlib').setLevel(logging.WARNING)

ROOT_DIR = "D:/CosyVoice"
modelPath = '{}/pretrained_models/CosyVoice-300M-25Hz'.format(ROOT_DIR)
matchaTTSPath = '{}/third_party/Matcha-TTS'.format(ROOT_DIR)

sys.path.append(ROOT_DIR)
sys.path.append(matchaTTSPath)

print("modelPath is ", modelPath)

cosyvoice = CosyVoice(modelPath)


# ['中文女', '中文男', '日语男', '粤语女', '英文女', '英文男', '韩语女']
# print(cosyvoice.list_avaliable_spks())


def requestSFT(ttsText, spkID, savePath):
    output = cosyvoice.inference_sft(ttsText, spkID)
    torchaudio.save(savePath, output['tts_speech'], 22050)


def requestZeroShot(ttsText, promptText, promptWav, savePath):
    prompt_speech_16k = load_wav(promptWav, 16000)
    outputs = cosyvoice.inference_zero_shot(ttsText, promptText, prompt_speech_16k, speed=1.2)

    count = 0
    for output in outputs:
        torchaudio.save(savePath, output['tts_speech'], 22050)
        count += 1

    # torchaudio.save(savePath, output['tts_speech'], 22050)


def requestCrossLingual(ttsText, promptWav, savePath):
    prompt_speech_16k = load_wav(promptWav, 16000)
    output = cosyvoice.inference_cross_lingual(ttsText, prompt_speech_16k)
    torchaudio.save(savePath, output['tts_speech'], 22050)


def requestInstruct(ttsText, spkID, instructText, savePath):
    # instruct usage, support <laughter></laughter><strong></strong>[laughter][breath]
    output = cosyvoice.inference_instruct(ttsText, spkID, instructText)
    torchaudio.save(savePath, output['tts_speech'], 22050)


def text2Voices(textPath, promptName, promptText, promptWav):
    filename = os.path.basename(textPath)
    folder = os.path.dirname(textPath)
    basename = str(filename).split(".")[0]

    voiceRoot = os.path.join(folder, "{}_{}".format(basename, promptName))
    os.makedirs(voiceRoot, exist_ok=True)

    savePath = os.path.join(folder, "{}_{}.wav".format(basename, promptName))
    # print(filename, folder, basename)
    lines = read_lines(textPath)

    medias = []
    for index in range(len(lines)):
        text = lines[index].strip()
        if len(text) <= 1:
            break
        wav = "{}.wav".format(index)
        wavFile = os.path.join(voiceRoot, wav)
        print(wavFile, text)
        medias.append(wavFile)

        requestZeroShot(text, promptText, promptWav, wavFile)
    mergeMedias(medias, savePath)


wavs = {
    "郭德纲": "./asset/gdg.wav",
    "封神榜男旁白": "./asset/fengshenbang-nan.wav",
    "舌尖上的中国": "./asset/shejianzhongguo.wav",
    "过秦论": "./asset/guoqinlun.wav",
    "上虞代言人-男声": "./asset/shangyudaiyanren-nan.wav",
    "科技感-男声": "./asset/kejigan-nan.wav",
    "专题片-男声": "./asset/zhuantipian-nan.wav",
}

prompts = {
    "郭德纲": "好好说话，以德服人，我是郭德纲，挺高兴的通过爱奇艺又跟大伙儿见面了，有人说这个跟做节目有什么区别吗，您记住了，节目上一般都是特别正经的",
    "封神榜男旁白": "殷十娘一直想不通会飞的老虎是什么意思，只好将哪吒留在飞虎涧，但是哪吒一个小孩子被人弃在荒山野岭，慌不择路，竟然离开飞虎涧，走到毒蛇谷",
    "舌尖上的中国": "这种地理和气候的跨度，有助于物种的形成和保存，任何一个国家都没有这样多潜在的食物原材料",
    "过秦论": "秦孝公据崤函之固，拥雍州之地，君臣固守以窥周室，有席卷天下，包举宇内，囊括四海之意，并吞八荒之心",
    "上虞代言人-男声": "基本在任何地方，都不可能在一到两年，两到三年的时间里，白手起家赚二十套房子，成为上虞代言人以后，成为上虞代言人以后，而且人人可为",
    "科技感-男声": "从古至今，蚊子与人类的战争从未停止，传话一直在探索更好的防蚊虫方案",
    "专题片-男声": "在抗日战争刚刚爆发的历史转折关头",
}


def ffmpegCommand(medias, mediaOut):
    # ffmpeg -f concat -i filelist.txt -c copy output.mkv

    folder = os.path.dirname(mediaOut)
    filelist = ""
    for media in medias:
        folder = os.path.dirname(media)
        filelist += "file {}\r".format(os.path.basename(media))

    filepath = os.path.join(folder, "filelist.txt")

    write_to_file(filepath, filelist)
    command = ["ffmpeg", "-f", "concat", "-i", os.path.abspath(filepath), "-c", "copy", os.path.abspath(mediaOut)]

    return command


def mergeMedias(medias, mediaOut):
    command = ffmpegCommand(medias, mediaOut)
    try:
        # Execute the command using subprocess
        process = subprocess.run(command, check=True)
        if process.returncode == 0:
            print("Video merging is successful.")
        else:
            print("An error occurred during video merging.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to merge videos: {e}")


def testMerge():
    media1 = "E:\\images\\1\\0.wav"
    media2 = "E:\\images\\1\\1.wav"
    media3 = "E:\\images\\1\\2.wav"

    mediaOut = "E:\\images\\out.wav"
    mergeMedias([media1, media2, media3], mediaOut)


if __name__ == "__main__":
    text = "原来女娲氏炼石补天之时"
    spkID = "中文女"
    savePath = "./asset/zeroShot.wav"

    promptName = "专题片-男声"  # "封神榜男旁白", 舌尖上的中国  ,过秦论 上虞代言人-男声  科技感-男声  专题片-男声
    promptText = prompts[promptName]
    promptWav = wavs[promptName]

    # requestSFT(text, spkID, savePath)
    # requestZeroShot(text, promptText, promptWav, savePath)

    # shitouji = "E:\\douyin\\videos\\车床介绍.txt"
    shitouji = "C:\\Users\\Administrator\\Documents\\现代学林点将录\\天王晁盖-章太炎\\天王晁盖-章太炎.txt"

    text2Voices(shitouji, promptName, promptText, promptWav)

    # testMerge()
