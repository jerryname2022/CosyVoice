# SDK模型下载
import os
from modelscope import snapshot_download

#  # git模型下载，请确保已安装git lfs
# mkdir -p pretrained_models
# git clone https://www.modelscope.cn/iic/CosyVoice-300M.git pretrained_models/CosyVoice-300M
# git clone https://www.modelscope.cn/iic/CosyVoice-300M-25Hz.git pretrained_models/CosyVoice-300M-25Hz
# git clone https://www.modelscope.cn/iic/CosyVoice-300M-SFT.git pretrained_models/CosyVoice-300M-SFT
# git clone https://www.modelscope.cn/iic/CosyVoice-300M-Instruct.git pretrained_models/CosyVoice-300M-Instruct
# git clone https://www.modelscope.cn/iic/CosyVoice-ttsfrd.git pretrained_models/CosyVoice-ttsfrd

os.environ["http_proxy"] = "http://192.168.124.9:1081"
os.environ["https_proxy"] = "http://192.168.124.9:1081"

# snapshot_download('iic/CosyVoice-300M', cache_dir='pretrained_models/CosyVoice-300M')
# # snapshot_download('iic/CosyVoice-300M-25Hz', cache_dir='pretrained_models/CosyVoice-300M-25Hz')
# snapshot_download('iic/CosyVoice-300M-SFT', cache_dir='pretrained_models/CosyVoice-300M-SFT')
# snapshot_download('iic/CosyVoice-300M-Instruct', cache_dir='pretrained_models/CosyVoice-300M-Instruct')
# snapshot_download('iic/CosyVoice-ttsfrd', cache_dir='pretrained_models/CosyVoice-ttsfrd')

snapshot_download('THUDM/glm-4-voice-decoder', cache_dir='pretrained_models/glm-4-voice-decoder')
