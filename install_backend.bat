@rem 请确保使用Python3.9环境
@rem 请确保已安装git
@rem 请在该脚本所在文件夹下运行此脚本

@echo off

chcp 65001

@rem 请在proxy=之后添加代理url以设置代理, 可确保模型下载成功; 如果不添加, 将不使用代理

set proxy=http://localhost:10809

echo "请等待环境安装完成..."

python -m venv .
call .\Scripts\Activate
pip install -r requirements.txt
pip install torch==2.0.0+cu118 torchvision==0.15.0 torchaudio==2.0.0 --index-url https://download.pytorch.org/whl/cu118

:: 重置库, 避免冲突
pip uninstall --yes python-ffmpeg
pip uninstall --yes ffmpeg-python

pip install ffmpeg-python

copy .\app\GPT_SoVITS\utils.py .\Lib\site-packages
cd .\app\GPT_SoVITS\pretrained_models
:: 为了防止git拒绝克隆到已存在的文件夹中, 判断文件夹是否已存在。如果已存在, 则更新克隆文件; 如果不存在, 则创建克隆
if not exist .\chinese-hubert-base (
    git clone https://huggingface.co/TencentGameMate/chinese-hubert-base
) else (
    mkdir chinese-hubert-base-temp
    if not %proxy% == "" (
        git clone -c http.proxy=%proxy% https://huggingface.co/TencentGameMate/chinese-hubert-base chinese-hubert-base-temp
    ) else (
        git clone https://huggingface.co/TencentGameMate/chinese-hubert-base chinese-hubert-base-temp
    )
    xcopy chinese-hubert-base-temp\.git chinese-hubert-base\.git /H /E /S /i
    echo Y | rmdir /s chinese-hubert-base-temp
    cd chinese-hubert-base
    git checkout .
)



:: chinese-roberta-wwm-ext-large
:: mkdir chinese-roberta-wwm-ext-large
:: cd chinese-roberta-wwm-ext-large

:: if not %proxy% == "" (
:: 
::    curl --proxy %proxy% -o config.json -L https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/config.json?download=true
::     curl --proxy %proxy% -o pytorch_model.bin -L https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/pytorch_model.bin
::    curl --proxy %proxy% -o tokenizer.json -L https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/tokenizer.json?download=true
:: 
::     cd ..
::     curl --proxy %proxy% -o s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt -L https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25hz-2kh-longer-epoch%3D68e-step%3D50232.ckpt
::     curl --proxy %proxy% -o s2G488k.pth -L https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth
:: 
:: ) else (
::     curl -o config.json -L https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/config.json?download=true
::     curl -o pytorch_model.bin -L https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/pytorch_model.bin
::     curl -o tokenizer.json -L https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/tokenizer.json?download=true
:: 
::     cd ..
::     curl -o s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt -L https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25hz-2kh-longer-epoch%3D68e-step%3D50232.ckpt
::     curl -o s2G488k.pth -L https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth
:: )

cd ../../../..

echo "环境安装完毕。现在可以退出了。"

pause

exit