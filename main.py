import asyncio

from pkg.plugin.models import *
from pkg.plugin.host import EventContext, PluginHost
from pkg.qqbot.manager import QQBotManager
from plugins.qchat_system_status.pkg.system_test import drawstatus
from mirai import Image
from pkg.utils import context


@register(
    name="QchatSystemStatus",
    description="生成系统状态图",
    version="0.1",
    author="oliverkirk-sudo",
)
async def get_status(plugin_host: PluginHost):
    botmgr: QQBotManager = context.get_qqbot_manager()
    task = asyncio.create_task(botmgr.adapter.bot.bot_profile.get())
    await asyncio.wait([task])
    nickname = task.result().nickname
    print(nickname)
    bot_id = botmgr.bot_account_id  # 获取qq号
    img_b64 = drawstatus(qq=bot_id, nickname=nickname)
    return img_b64


def send_msg(kwargs, msg):
    host: pkg.plugin.host.PluginHost = kwargs["host"]
    host.send_person_message(kwargs["launcher_id"], msg) if kwargs[
        "launcher_type"
    ] == "person" else host.send_group_message(kwargs["launcher_id"], msg)


class HelloPlugin(Plugin):

    # 插件加载时触发
    # plugin_host (pkg.plugin.host.PluginHost) 提供了与主程序交互的一些方法，详细请查看其源码
    def __init__(self, plugin_host: PluginHost):
        pass

    @on(PersonCommandSent)
    @on(GroupCommandSent)
    def System_self_test(self, event: EventContext, **kwargs):
        command = kwargs["command"]
        if command in ["自检", "系统状态", "systemstatus"] and kwargs["is_admin"]:
            plugin_host: PluginHost = kwargs["host"]
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(get_status(plugin_host))
            send_msg(kwargs, [Image(base64=result)])
            event.prevent_default()
            event.prevent_postorder()

    def __del__(self):
        pass
