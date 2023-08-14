from pkg.plugin.models import *
from pkg.plugin.host import EventContext, PluginHost
from plugins.qchat_system_status.system_test import drawstatus
from mirai import Image
from pkg.utils import context


@register(
    name="QchatSystemStatus",
    description="生成系统状态图",
    version="0.1",
    author="oliverkirk-sudo",
)
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
            botmgr = context.get_qqbot_manager()  # 获取运行时QQBotManager对象
            bot_id = botmgr.bot_account_id  # 获取qq号
            img_b64 = drawstatus(qq=bot_id)
            event.add_return("reply", [Image(base64=img_b64)])
            event.prevent_default()
            event.prevent_postorder()

    def __del__(self):
        pass
