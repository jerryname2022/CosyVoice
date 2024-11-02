from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from utils.subtitle_utils import generate_srt, generate_srt_clip
from utils.file_utils import write_to_file, read_lines
from utils.log_utils import log_time
from utils.srt_utils import srt_texts, reset_srt, parse_srt_texts
from utils.trans_utils import pre_proc, proc, write_state, load_state, proc_spk, convert_pcm_to_float
import librosa, time, os

# os.environ["http_proxy"] = "http://172.29.0.1:1081"
# os.environ["https_proxy"] = "http://172.29.0.1:1081"


ROOT_DIR = "D:/CosyVoice"
log_time("pre ... ")

# cn  C:\Users\Administrator\.cache\modelscope\hub
model = AutoModel(
    model="{}/pretrained_models/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch".format(
        ROOT_DIR),
    vad_model="{}/pretrained_models/speech_fsmn_vad_zh-cn-16k-common-pytorch".format(ROOT_DIR),
    punc_model="{}/pretrained_models/punc_ct-transformer_zh-cn-common-vocab272727-pytorch".format(ROOT_DIR),
    spk_model="{}/pretrained_models/speech_campplus_sv_zh-cn_16k-common".format(ROOT_DIR),
    device="cuda:0",
    batch_size=1,
    disable_pbar=True,
    disable_log=True,
    disable_update=True
)


# en
# model = AutoModel(model="iic/speech_paraformer_asr-en-16k-vocab4199-pytorch",
#                   vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
#                   punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
#                   spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
#                   )


def genAudioSrt(audioInput, txtInputs=None, output=None):
    wav = librosa.load(audioInput, sr=16000)[0]
    data = convert_pcm_to_float(wav)
    log_time("start ... ")

    res = model.generate(data,
                         return_spk_res=True,
                         sentence_timestamp=False,
                         return_raw_text=False,
                         is_final=True,
                         pred_timestamp=True,
                         en_post_proc=True,
                         cache={})

    # print(res)
    # text = rich_transcription_postprocess(res[0]["text"])
    resSrt = generate_srt(res[0]['sentence_info'])

    if output is None:
        folder = os.path.dirname(audioInput)
        basename = os.path.basename(audioInput).split(".")[0]
        output = os.path.join(folder, "{}.srt".format(basename))

    if txtInputs is not None:
        folder = os.path.dirname(audioInput)
        basename = os.path.basename(audioInput).split(".")[0]
        temp = os.path.join(folder, "{}.tmp".format(basename))
        write_to_file(temp, resSrt)
        texts = read_lines(temp)

        subtitles = reset_srt(texts, txtInputs)
        resSrt = srt_texts(subtitles)
        os.remove(temp)

    # print(resSrt)
    write_to_file(output, resSrt)
    log_time("end ... ")


count = 1
audio = f"E:\\youtube\hlm\\{count}/{count}.wav"
txtFile = f"E:\\youtube\hlm\\{count}/{count}.txt"
srtFile = f"E:\\youtube\hlm\\{count}/{count}.srt"

if not os.path.exists(srtFile) and os.path.exists(txtFile):
    texts = read_lines(txtFile)
    genAudioSrt(audio, txtInputs=texts)
