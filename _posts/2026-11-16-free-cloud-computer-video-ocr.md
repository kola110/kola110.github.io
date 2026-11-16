---
title: "领了一台免费云电脑，先跑视频 OCR 插件验证"
date: 2026-11-16
category: 编程
excerpt: "两个项目都有没跑过的验证，领了一台免费云电脑当跑场，先跑视频 OCR 插件。"
minutes: "约 8 分钟"
---

手头有两个项目，都卡在同一步上：代码写完了，也过了语法检查，但从来没真正跑过。

一个是货车视频识别，11 月 12 日刚加上了 ByteTrack 跟踪（`--track` + `--save-best`，每辆车一张最佳视角截图），推到了 GitHub，commit bfa822d7，之后就没再动过——没跑过，不知道在真实视频上表现如何。另一个是 DeepSeek Harness 的视频 OCR 插件，v0.2 已经把 PaddleOCR 接进去了，边车服务也能跑，但同样没在 dsh 里真正调用过一次。

验证一直没跑，不是不想跑，是没有合适的跑场。本地机器 Muse 碰不到，自己的电脑又不想为了两次验证装一堆环境。今天的解决办法是：领一台免费云电脑。晚上先跑了视频 OCR 插件，从搭环境到在 dsh 里调通，全程记录如下。

## 一、为什么需要一台跑场

这两个验证有个共同点：环境重，结果轻。

视频 OCR 插件要装的东西不少：Node、Python 3.11、conda 环境、PaddleOCR、ffmpeg、再加上 deepseek-harness 本身。只为了验证一次就往主力机器上装，装完还得收拾。云电脑的好处是隔离：跑完验证，要留就留快照，要扔就扔，不动本地环境。

另一个原因是会话长度。免费云电脑单次最长运行 2 小时（随使用时长能长到 8 小时），刚好够把一次验证拆成两个会话跑：第一个会话搭环境、验边车，第二个会话起 dsh、调插件。时间盒是现成的，拖不下去。

## 二、免费云电脑长什么样

领的是 InstaBox 的免费档，每账号限一台，规格是 4 vCPU / 8 GiB 内存 / 20 GiB 磁盘，agent-browser 模板。访问方式有三种：网页终端、VNC 桌面、SSH。

有几个限制要先说清楚，免得期望跑偏：

- 没有独立的入站 IPv4，不能对外提供服务，也当不了通用代理；
- 30 分钟空闲自动暂停，单次最长 2 小时起步；
- 纯 CPU，没有 GPU，YOLO 只能跑 CPU；
- 磁盘只有 20 GiB，Python 环境是大头，得省着用。

注册有个小插曲：注册页只有 Google / GitHub OAuth，没有邮箱密码注册。本来想用一个邮箱账号注册，结果用不上，最后用 Google 账号注册。机器名 `free-machine`，中午 13:34 创建，状态 Running。

## 三、测试分两个会话

两个验证，我先跑视频 OCR 插件。

按单次 2 小时的上限拆成两个会话：第一个会话摸清机器现状、搭环境、验边车；第二个会话起 dsh、在聊天里真正调一次 `video_ocr`。通过标准事先定好：边车健康检查返回 `{"status":"ok"}`，热身 OCR 返回 HTTP 200 且带 `{text, lines}` 结构，dsh 日志里出现 `[video-ocr-plugin] plugin loaded!`，最后在 dsh 聊天里拿到 `video_ocr` 的返回结果。测试片用的是 Mixkit 的一段 14.9 秒远景航拍货车片段——车牌和车门字根本看不清，所以空文本是预期的，测的是链路通不通，不是识别准不准。

## 四、第一个会话：搭环境、验边车

先查机器现状：Node 是 v22.23.3，dsh 要 24.9+，不够；Python 3.13.5；ffmpeg 和 conda 都没装；git 2.47.3；`/data` 是 20G 磁盘，已用 4.4G、可用 16G。

Node 从官网下了 linux-x64 的 tarball，装到 v24.22.3，路径写进 `~/.bashrc`。ffmpeg 用 apt 装，7.1.5。插件仓库 `kola110/dsh-plugin-video-ocr` 克隆到 `/data`，HEAD 是 6e4dbb7。

conda 装的是 Miniconda 26.9.4，装到 `/data/miniconda3`。建 `video-ocr` 环境时第一次失败了：`CondaToSNonInteractiveError`，main 和 r 两个频道没接受服务条款。按报错本身给出的命令执行 `conda tos accept` 后重试，成功。环境里是 paddleocr 3.7.0、paddlepaddle 3.3.1、paddlex 3.7.2。建完环境 `/data` 已用 8.2G、可用 12G——20G 磁盘确实得省着用。

边车服务后台启动（`nohup python server.py`），约 30 秒后 `curl http://127.0.0.1:8000/health` 返回 `{"status":"ok"}`。首次启动下载了 PP-OCRv6 的模型文件。

热身 OCR：下载 Mixkit 测试片到 `/data/truck.mp4`（约 4.5MB），ffmpeg 按 `fps=1/5` 抽出 0 秒、5 秒、10 秒三帧。把第一帧 POST 到 `/ocr`，返回 `{"text":"","lines":[]}`，HTTP 200。空文本是预期的——远景航拍，帧里没有可读的文字；通过标准是 200 加 `{text, lines}` 结构，这一项过了。

最后给机器存了个快照，名字叫 `video-ocr-sidecar-ready`，会话 1 的全部环境都在里面。以后机器暂停或者环境弄坏了，可以从这个快照恢复，不用重装。

## 五、第二个会话：起 dsh、调插件

先把 `cordis.yml` 里的占位路径 `<ABSOLUTE_PATH_TO_THIS_DIR>` 换成克隆目录的绝对路径 `/data/dsh-plugin-video-ocr/src/video-ocr-plugin.ts`。然后克隆 deepseek-harness（约 383MB），切到标签 `dsh-v0.2.2-rc.1`——注意标签名带 `dsh-` 前缀，`0.2.2-rc.1` 和 `v0.2.2-rc.1` 这两个名字都不存在。corepack 启用 pnpm 11.28.5，`pnpm install` 23.3 秒完成。

第一次启动 `pnpm dsh web` 失败了。日志第 3 行就出现了 `[video-ocr-plugin] plugin loaded!`，插件本身加载成功，但进程随后以 exit code 1 退出：缺已编译的客户端产物，`packages/client/ui-trajectory/lib/client.js` 等文件不存在。原因是 `pnpm install` 只装依赖，不构建。

修复办法是按仓库文档先构建：`pnpm run build`（package.json 里的 build 是 `tsx scripts/build.ts`）。构建跑了 194 秒，10 个 gate 全过，生成 366 个客户端产物，`lib/client.js`（467,284 字节）有了。

重启 dsh，插件再次加载。这一步又遇到两个小坑：

- 不带 token 直接访问 `http://127.0.0.1:3080/` 返回 401，这是 dsh 的鉴权设计，必须用它打印的带 token 的链接打开。而且这个链接是一次性的，约一分钟就失效——第一次拿两分钟前的链接打开，得到 401；重启 dsh 后几秒内立即打开，才成功。
- 重启时只杀 pnpm 包装进程不够，得连它的 node 子进程一起杀掉，不然 3080 端口被旧进程占着，新启动报 `EADDRINUSE`。

在机器的 Chromium（VNC 桌面）里打开 dsh，页面正常显示 "DSH Local Build"。dsh 弹出 Get started 对话框：要登录 DeepSeek 账号或加 API Key，只有 Add API Key 和 Sign in 两个按钮，没有跳过选项。输入 key 并保存——key 保存在这台机器的 dsh 里。

选工作区 `/data`，在聊天里发：

> Use the video_ocr tool on /data/truck.mp4 with interval 5 seconds.

11 秒完成，1 turn、3 steps、29.2K tok。`video_ocr` 的返回结果：视频时长 14.889875 秒，5 秒间隔，共 3 帧——0 秒、5 秒、10 秒，全部无文本。附注说明 OCR 由 PaddleOCR 边车提供（paddleocr==3.7.0，PP-OCRv6，中文）。dsh 还把结果整理成一张表：0.0s、5.0s、10.0s 三行，识别文本都是 (none)，并解释说片段里没有屏幕文字，或者文字太小太模糊；如果怀疑有文字，可以用 1–2 秒间隔重跑。

还有个小插曲：dsh 随后想用 bash 探查视频文件的时长和分辨率，失败了，报错是 sandbox 模式 `workspace-write` 没有可用的沙箱后端。这跟 OCR 任务无关，不影响上面的结果。

## 六、这次验证证明了什么、没证明什么

证明了：插件能在 dsh 里加载，工具能被 agent 端到端调用，边车 OCR 通路是通的。从"写完了，没跑过"变成了"跑过，返回了结果"——这就是当初给这个插件定的完成标准。

没证明：OCR 准不准。测试片是远景航拍，三帧空文本是预期的，测不出准确率。真正的准确率测试需要近景素材——能看清车牌和车门字的那种。下一步就是找一段自己的近景录像，再跑一次。

货车视频识别的验证还没跑，同一个跑场，下次接着来。

---

**收尾一句话：免费云电脑不是主力开发机，它就是个验证场——两个项目"没跑过"的状态，今晚先去掉了一个。**
