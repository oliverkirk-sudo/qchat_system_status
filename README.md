# qchat_system_status
适用于QChatGPT的系统状态查看插件，以图片形式输出
效果如图：
![000000000-000000000-BDFE2919EF554594F362C008C64FE164](https://github.com/oliverkirk-sudo/qchat_system_status/assets/78022033/354be0f8-676b-42ca-aff5-c83dc15b22d3)

## 一些问题

- 输出时间较长

## 1、前置工作

- 下载本插件`!plugin get https://github.com/oliverkirk-sudo/qchat_system_status.git`

## 2、修改配置文件

- 若不想在底部输出PowerBy,可将main.py中的create_by改为False
- 用`!relaod`重新加载插件
## 3、包含的指令
使用命令：
- !自检
- !系统状态
- !systemstatus
## 4、我的其他插件
- [oliverkirk-sudo/chat_voice](https://github.com/oliverkirk-sudo/chat_voice) - 文字转语音输出，支持HuggingFace上的[VITS模型](https://huggingface.co/spaces/Plachta/VITS-Umamusume-voice-synthesizer),azure语音合成,vits本地语音合成,sovits语音合成
- [oliverkirk-sudo/QChatAIPaint](https://github.com/oliverkirk-sudo/QChatAIPaint) - 基于[Holara](https://holara.ai/)的ai绘图插件
- [oliverkirk-sudo/QChatCodeRunner](https://github.com/oliverkirk-sudo/QChatCodeRunner) - 基于[CodeRunner-Plugin](https://github.com/oliverkirk-sudo/CodeRunner-Plugin)的代码运行与图表生成插件
- [oliverkirk-sudo/QChatWeather](https://github.com/oliverkirk-sudo/QChatWeather) - 生成好看的天气图片，基于和风天气
- [oliverkirk-sudo/QChatMarkdown](https://github.com/oliverkirk-sudo/QChatMarkdown) - 将机器人输出的markdown转换为图片，基于[playwright](https://playwright.dev/python/docs/intro)
