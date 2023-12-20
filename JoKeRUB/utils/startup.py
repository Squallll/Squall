import time
import asyncio
import glob
import os
import sys
from telethon.errors.rpcerrorlist import ChannelPrivateError
import urllib.request
from datetime import timedelta
from pathlib import Path
import requests
from telethon import Button, functions, types, utils
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import FloodWaitError
from JoKeRUB import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from ..Config import Config
from aiohttp import web
from ..core import web_server
from ..core.logger import logging
from ..core.session import l313l
from ..helpers.utils import install_pip
from ..helpers.utils.utils import runcmd
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup
LOGS = logging.getLogger("aljoker")
logging.getLogger('telethon').setLevel(logging.WARNING)
##Reda hands here
cmdhr = Config.COMMAND_HAND_LER
bot = l313l
ENV = bool(os.environ.get("ENV", False))

if ENV:
    VPS_NOLOAD = ["سيرفر"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["هيروكو"]

async def check_dyno_type():
    headers = {
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": f"Bearer {Config.HEROKU_API_KEY}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.heroku.com/apps/{Config.HEROKU_APP_NAME}/dynos", headers=headers) as resp:
            if resp.status == 200:
                dynos = await resp.json()
                for dyno in dynos:
                    if dyno["type"] != "standard-1X":
                        return False
            else:
                return False
    return True

async def setup_bot():
    """
    To set up bot for JoKeRUB
    """
    try:
        await l313l.connect()
        config = await l313l(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == l313l.session.server_address:
                if l313l.session.dc_id != option.id:
                    LOGS.warning(
                        f"⌯︙معرف ثابت في الجلسة من {l313l.session.dc_id}"
                        f"⌯︙لـ  {option.id}"
                    )
                l313l.session.set_dc(option.id, option.ip_address, option.port)
                l313l.session.save()
                break
        bot_details = await l313l.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        redaport = Config.PORT
        await web.TCPSite(app, bind_address, redaport).start()
        l313l.me = await l313l.get_me()
        l313l.uid = l313l.tgbot.uid = utils.get_peer_id(l313l.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(l313l.me)
        if not check_dyno_type:
            LOGS.error("قد تحدث مشكلة ولن يعمل السورس لان نوع الداينو ليس بيسك قم بتحويله الى basic")
    except Exception as e:
        LOGS.error(f"كـود تيرمكس - {str(e)}")
        sys.exit()

async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            Config.CATUBLOGO = await l313l.tgbot.send_file(
                BOTLOG_CHATID,
                "https://t.me/E9N99",
                caption="**‏᯽︙ بــوت فلسطين العرب يـعـمـل بـنـجـاح ✓ \n᯽︙ أرسل `.الاوامر`لرؤية اوامر السورس \n  ᯽︙ لأستعمال بوت الأختراق عبر كود التيرمكس أرسل`.هاك`**",
                buttons=[(Button.url("سورس فلسطين العرب", "https://t.me/E9N99"),)],
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await l313l.check_testcases()
            message = await l313l.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**تم تشغيل البوت الأن أرسل `.فحص`**"
            await l313l.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await l313l.send_message(
                    msg_details[0],
                    f"{cmdhr}بنك",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


async def mybot():
    try:
        starkbot = await l313l.tgbot.get_me()
        joker = "الجوكر 🤡"
        bot_name = starkbot.first_name
        botname = f"@{starkbot.username}"
        if bot_name.endswith("Assistant"):
            print("تم تشغيل البوت")
        if starkbot.bot_inline_placeholder:
            print("Aljoker ForEver")
        else:
            try:
                await l313l.send_message("@BotFather", "/setinline")
                await asyncio.sleep(1)
                await l313l.send_message("@BotFather", botname)
                await asyncio.sleep(1)
                await l313l.send_message("@BotFather", joker)
                await asyncio.sleep(2)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

async def ipchange():
    """
    Just to check if ip change or not
    """
    newip = requests.get("https://ipv4.jsonip.com/").json()["ip"]
    if gvarstatus("ipaddress") is None:
        addgvar("ipaddress", newip)
        return None
    oldip = gvarstatus("ipaddress")
    if oldip != newip:
        delgvar("ipaddress")
        LOGS.info("Ip Change detected")
        try:
            await l313l.disconnect()
        except (ConnectionError, CancelledError):
            pass
        return "ip change"


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await l313l.tgbot.get_me()
    try:
        await l313l(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await l313l(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))
JoKeRUB = {"@E9N99"}
async def saves():
   for lMl10l in JoKeRUB:
        try:
             await l313l(JoinChannelRequest(channel=lMl10l))
        except OverflowError:
            LOGS.error("Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
            continue
        except ChannelPrivateError:
            continue
                
async def load_plugins(folder, extfolder=None):
    """
    تحميل ملفات السورس
    """
    if extfolder:
        path = f"{extfolder}/*.py"
        plugin_path = extfolder
    else:
        path = f"JoKeRUB/{folder}/*.py"
        plugin_path = f"JoKeRUB/{folder}"
    files = glob.glob(path)
    files.sort()
    success = 0
    failure = []
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            pluginname = shortname.replace(".py", "")
            try:
                if (pluginname not in Config.NO_LOAD) and (
                    pluginname not in VPS_NOLOAD
                ):
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                pluginname,
                                plugin_path=plugin_path,
                            )
                            if shortname in failure:
                                failure.remove(shortname)
                            success += 1
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if shortname not in failure:
                                failure.append(shortname)
                            if check > 5:
                                break
                else:
                    os.remove(Path(f"{plugin_path}/{shortname}.py"))
            except Exception as e:
                if shortname not in failure:
                    failure.append(shortname)
                os.remove(Path(f"{plugin_path}/{shortname}.py"))
                LOGS.info(
                    f"لم يتم تحميل {shortname} بسبب خطأ {e}\nمسار الملف {plugin_path}"
                )
    if extfolder:
        if not failure:
            failure.append("None")
        await l313l.tgbot.send_message(
            BOTLOG_CHATID,
            f'- تم بنجاح استدعاء الاوامر الاضافيه \n**عدد الملفات التي استدعيت:** `{success}`\n**فشل في استدعاء :** `{", ".join(failure)}`',
        )
#شعندك هنا تبحوش ياحلو 😉
#سورس الجوكر عمك
async def aljoker_the_best(l313l, group_name):
    async for dialog in l313l.iter_dialogs():
        if dialog.is_group and dialog.title == group_name:
            return dialog.id
    return None

async def verifyLoggerGroup():
    """
    Will verify both loggers group
    """
    flag = False
    if BOTLOG:
        try:
            entity = await l313l.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "᯽︙الفار الأذونات مفقودة لإرسال رسائل لـ PRIVATE_GROUP_BOT_API_ID المحدد."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "᯽︙الفار الأذونات مفقودة لإرسال رسائل لـ PRIVATE_GROUP_BOT_API_ID المحدد."
                    )
        except ValueError:
            LOGS.error("᯽︙تـأكد من فـار المجـموعة  PRIVATE_GROUP_BOT_API_ID.")
        except TypeError:
            LOGS.error(
                "᯽︙لا يمكـن العثور على فار المجموعه PRIVATE_GROUP_BOT_API_ID. تأكد من صحتها."
            )
        except Exception as e:
            LOGS.error(
                "᯽︙حدث استثناء عند محاولة التحقق من PRIVATE_GROUP_BOT_API_ID.\n"
                + str(e)
            )
    else:
        descript = "- عزيزي المستخدم هذه هي مجموعه الاشعارات يرجى عدم حذفها  - @E9N99"
        photobt = await l313l.upload_file(file="data:image/jpeg;base64,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")
        botlog_group_id = await aljoker_the_best(l313l, "مجموعة أشعارات الجوكر")
        if botlog_group_id:
            addgvar("PRIVATE_GROUP_BOT_API_ID", botlog_group_id)
            print("᯽︙تم العثور على مجموعة المساعدة بالفعل وإضافتها إلى المتغيرات.")
        else:
            _, groupid = await create_supergroup(
                "مجموعة أشعارات الجوكر", l313l, Config.TG_BOT_USERNAME, descript, photobt
            )
            addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
            print("᯽︙تم إنشاء مجموعة المسـاعدة بنجاح وإضافتها إلى المتغيرات.")
        flag = True
    if PM_LOGGER_GROUP_ID == -100:
        descript = "᯽︙ وظيفه الكروب يحفظ رسائل الخاص اذا ما تريد الامر احذف الكروب نهائي \n  - @E9N99"
        photobt = await l313l.upload_file(file="https://alwatannews.net/uploads/images/2022/09/28/2485688.jpg")
        pm_logger_group_id = await aljoker_the_best(l313l, "مجموعة التخزين")
        if pm_logger_group_id:
            addgvar("PM_LOGGER_GROUP_ID", pm_logger_group_id)
            print("تـم العثور على مجموعة الكروب التخزين بالفعل واضافة الـفارات الـيها.")
        else:
            _, groupid = await create_supergroup(
                "مجموعة التخزين", l313l, Config.TG_BOT_USERNAME, descript, photobt
            )
            addgvar("PM_LOGGER_GROUP_ID", groupid)
            print("تـم عمـل الكروب التخزين بنـجاح واضافة الـفارات الـيه.")
        flag = True
    if flag:
        executable = sys.executable.replace(" ", "\\ ")
        args = [executable, "-m", "JoKeRUB"]
        os.execle(executable, *args, os.environ)
        sys.exit(0)

async def install_externalrepo(repo, branch, cfolder):
    jokerREPO = repo
    rpath = os.path.join(cfolder, "requirements.txt")
    if jokerBRANCH := branch:
        repourl = os.path.join(jokerREPO, f"tree/{jokerBRANCH}")
        gcmd = f"git clone -b {jokerBRANCH} {jokerREPO} {cfolder}"
        errtext = f"لا يوحد فرع بأسم `{jokerBRANCH}` في الريبو الخارجي {jokerREPO}. تاكد من اسم الفرع عبر فار (`EXTERNAL_REPO_BRANCH`)"
    else:
        repourl = jokerREPO
        gcmd = f"git clone {jokerREPO} {cfolder}"
        errtext = f"الرابط ({jokerREPO}) الذي وضعته لفار `EXTERNAL_REPO` غير صحيح عليك وضع رابط صحيح"
    response = urllib.request.urlopen(repourl)
    if response.code != 200:
        LOGS.error(errtext)
        return await l313l.tgbot.send_message(BOTLOG_CHATID, errtext)
    await runcmd(gcmd)
    if not os.path.exists(cfolder):
        LOGS.error(
            "هنالك خطأ اثناء استدعاء رابط الملفات الاضافية يجب التأكد من الرابط اولا "
        )
        return await l313l.tgbot.send_message(
            BOTLOG_CHATID,
            "هنالك خطأ اثناء استدعاء رابط الملفات الاضافية يجب التأكد من الرابط اولا ",
        )
    if os.path.exists(rpath):
        await runcmd(f"pip3 install --no-cache-dir -r {rpath}")
    await load_plugins(folder="JoKeRUB", extfolder=cfolder)
