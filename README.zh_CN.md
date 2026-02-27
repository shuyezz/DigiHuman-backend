[English](README.md) | [简体中文](README.zh_CN.md)

# 数字人项目

## 介绍

我们的项目旨在创建一个完整的、可部署的、面向用户的数字人系统。
该仓库为系统的后端部分，运行于 Python 环境下。

目前项目使用 Pytorch 作为机器学习模型框架，构建流水线。同时使用 Flask 作为服务器, 向前端提供 RESTful APIs.

目前，我们的仓库是私有的，仅允许合作者参与，包括提交问题、创建分支、更新文件等。
我们期望可以在整个项目完成后向大家开源 ❤️。

## 文档

### 部署项目

1.  克隆后端仓库, 为了同时克隆子模块，分成以下两种情况:

     - 之前未克隆过仓库。只需在指令之后添加一个<code>--recursive</code>参数, 完整指令如下:

        <code>git clone https://github.com/creamIcec/digital-human-backend --recursive</code>
    
     - 之前克隆了仓库。在后端根目录下, 使用下面的指令完成子模块的初始化:
    
        <code>git submodule update --init --recursive</code>

2.  运行<code>install_backend.bat</code>安装脚本
    <strong>或</strong>
    按照下面的方法进行:

     1. 在后端根目录下执行:
        <code>python -m venv .</code>
     2. 将以前的根目录下的<code>Lib/site-packages</code>下的所有文件和文件夹复制到新的<code>Lib/site-packages</code>

4.  由于 Github 文件大小限制和版权问题, 仓库中不包含模型文件和一些其他文件。我们将之前的文件按照以下方法复制(注:一些文件会被安装脚本自动下载，现在仍然需要手动排查，之后会优化自动化流程):

<table>
<thead>
    <tr>
        <td>原文件路径</td>
        <td>复制到...</td>
    </tr>
</thead>
<tbody>
    <tr>
        <td><原后端根目录>\app\GPT_SoVITS\pretrained_models 下的所有文件和文件夹</td>
        <td><新后端根目录>\app\GPT_SoVITS\pretrained_models</td>
    </tr>
    <tr>
        <td><原后端根目录>\ffmpeg.exe</td>
        <td><新后端根目录>\ffmpeg.exe</td>
    </tr>
    <tr>
        <td><原后端根目录>\ffprobe.exe</td>
        <td><新后端根目录>\ffprobe.exe</td>
    </tr>
</tbody>
</table>

3. 运行<code>run_backend.bat</code>启动后端。若成功启动 flask，则成功部署。

### 注意事项
