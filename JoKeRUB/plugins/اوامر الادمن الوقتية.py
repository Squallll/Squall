from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from JoKeRUB import l313l

from ..core.managers import edit_or_reply
from ..helpers.utils import _format
from . import BOTLOG, BOTLOG_CHATID, extract_time, get_user_from_event

plugin_category = "admin"

# =================== CONSTANT ===================
NO_ADMIN = "**᯽︙  عذرا انا لست مشرف في المجموعة ❕**"
NO_PERM = "**᯽︙ يبـدو انه ليس لديك صلاحيات كافية هذا حزين جدا 🥱♥**"

joker_t8ed = "https://stickarat.com/uploads/stickers/IIt9iYHSH33Ul5UFGe4sG4uTEKl3mI4G30oKGVfG.webp"
joker_unt8ed = "data:image/jpeg;base64,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"
@l313l.ar_cmd(
    pattern="تقييد_مؤقت(?:\s|$)([\s\S]*)",
    command=("تقييد_مؤقت", plugin_category),
    info={
        "header": "To stop sending messages permission for that user",
        "description": "Temporary mutes the user for given time.",
        "Time units": {
            "s": "seconds",
            "m": "minutes",
            "h": "Hours",
            "d": "days",
            "w": "weeks",
        },
        "usage": [
            "{tr}tmute <userid/username/reply> <time>",
            "{tr}tmute <userid/username/reply> <time> <reason>",
        ],
        "examples": ["{tr}tmute 2d to test muting for 2 days"],
    },
    groups_only=True,
    require_admin=True,
)
async def tmuter(event):  # sourcery no-metrics
    "لكـتم شخص لمدة معينة"
    await event.delete()
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if not reason:
        return await event.edit("᯽︙ انـت لم تقـم بـوضـع وقـت مع الامـر")
    reason = reason.split(" ", 1)
    hmm = len(reason)
    cattime = reason[0].strip()
    reason = "".join(reason[1:]) if hmm > 1 else None
    ctime = await extract_time(event, cattime)
    if not ctime:
        return
    if user.id == event.client.uid:
        return await event.edit(f"᯽︙ عـذرا لا يمـكننـي حـظر نفـسي ")
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=ctime, send_messages=True),
            )
        )
        # Announce that the function is done
        if reason:
            await event.client.send_file(
                event.chat_id,
                joker_t8ed,
                caption=f"᯽︙ تم تقييد المستخدم {_format.mentionuser(user.first_name ,user.id)} بنجاح ✅\n ᯽︙السبب  : {reason}\n ** ᯽︙ مدة الكتم : **`{cattime}`",
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#الكتـم المؤقـت\n"
                    f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**الدردشـه : **{event.chat.title}(`{event.chat_id}`)\n"
                    f"**مدة الـكتم : **`{cattime}`\n"
                    f"**السـبب : **`{reason}``",
                )
        else:
            await event.client.send_file(
                event.chat_id,
                joker_t8ed,
                caption=f"**᯽︙ تم تقييد المستخدم {_format.mentionuser(user.first_name ,user.id)} بنجاح ✓** \n** ᯽︙ مدة الكتم : **`{cattime}`",
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#الـكتم المـؤقت\n"
                    f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**الدردشه : **{event.chat.title}(`{event.chat_id}`)\n"
                    f"** مـدة الكتـم : **`{cattime}`",
                )
        # Announce to logging group
    except UserIdInvalidError:
        return await event.edit("**يبدو ان كتم الشخص تم الغائه**")
    except UserAdminInvalidError:
        return await event.edit(
            "** يبـدو أنك لسـت مشرف في المجموعة او تحاول كتم مشـرف هنا**"
        )
    except Exception as e:
        return await event.edit(f"`{str(e)}`")


@l313l.ar_cmd(
    pattern="حظر_مؤقت(?:\s|$)([\s\S]*)",
    command=("حظر_مؤقت", plugin_category),
    info={
        "header": "To remove a user from the group for specified time.",
        "description": "Temporary bans the user for given time.",
        "Time units": {
            "s": "seconds",
            "m": "minutes",
            "h": "Hours",
            "d": "days",
            "w": "weeks",
        },
        "usage": [
            "{tr}tban <userid/username/reply> <time>",
            "{tr}tban <userid/username/reply> <time> <reason>",
        ],
        "examples": ["{tr}tban 2d to test baning for 2 days"],
    },
    groups_only=True,
    require_admin=True,
)
async def tban(event):  # sourcery no-metrics
    "لحـظر شخص مع وقـت معيـن"
    catevent = await edit_or_reply(event, "᯽︙ يتـم  الـحظر مؤقـتا أنتـظر **")
    user, reason = await get_user_from_event(event, catevent)
    if not user:
        return
    if not reason:
        return await catevent.edit("᯽︙ يبدو انك لم تقم بوضع وقت مع الامر **")
    reason = reason.split(" ", 1)
    hmm = len(reason)
    cattime = reason[0].strip()
    reason = "".join(reason[1:]) if hmm > 1 else None
    ctime = await extract_time(catevent, cattime)
    if not ctime:
        return
    if user.id == event.client.uid:
        return await catevent.edit(f"᯽︙ عذرا لا يمكنني كتم نفسـي")
    await catevent.edit("᯽︙ تـم حـظره مـؤقـتا")
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=ctime, view_messages=True),
            )
        )
    except UserAdminInvalidError:
        return await catevent.edit(
            "᯽︙ ** يبـدو أنك لسـت مشرف في المجموعة او تحاول كتم مشـرف هنا**"
        )
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    # Helps ban group join spammers more easily
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await catevent.edit(
            "᯽︙ ** لـيس لدي صلاحيـات الحذف لكن سيبقى محظور ❕**"
        )
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later
    if reason:
        await catevent.edit(
            f"**المستخدم {_format.mentionuser(user.first_name ,user.id)}** /n **تـم حظره بنـجاح ✅**\n"
            f"مـدة الحـظر {cattime}\n"
            f"السـبب:`{reason}`"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الـحظر المـؤقت\n"
                f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**الدردشـه : **{event.chat.title}(`{event.chat_id}`)\n"
                f"**مـدة الحـظر : **`{cattime}`\n"
                f"**السـبب : **__{reason}__",
            )
    else:
        await catevent.edit(
            f"** الـمستخدم {_format.mentionuser(user.first_name ,user.id)} \n **تـم حظره بنـجاح ✅** \n"
            f"**مـدة الحـظر** {cattime}\n"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الـحظر المـؤقت\n"
                f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**المستخدم : **{event.chat.title}(`{event.chat_id}`)\n"
                f"**مـدة الحـظر : **`{cattime}`",
            )

@l313l.ar_cmd(
    pattern="تقييد(?:\s|$)([\s\S]*)",
    command=("تقييد", plugin_category),
    info={
        "header": "لتقييد المستخدم في المجموعة بدون مدة زمنية",
        "description": "يقوم بتقييد المستخدم في المجموعة بدون تحديد مدة زمنية.",
        "usage": [
            "{tr}تقييد <userid/username/reply>",
            "{tr}تقييد <userid/username/reply> <reason>",
        ],
        "examples": ["{tr}تقييد @username لأسباب مختلفة"],
    },
    groups_only=True,
    require_admin=True,
)
async def T8ed_Joker(event):
    await event.delete()
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == event.client.uid:
        return await event.edit("عذرًا، لا يمكنني تقييد نفسي.")
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=None, send_messages=True),
            )
        )
        if reason:
            await event.client.send_file(
                event.chat_id,
                joker_t8ed,
                caption=f"تم تقييد المستخدم {_format.mentionuser(user.first_name ,user.id)} بنجاح ✅.\nالسبب: {reason}",
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#تقييد المستخدم\n"
                    f"**المستخدم: **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**الدردشة: **{event.chat.title}(`{event.chat_id}`)\n"
                    f"**السبب: **`{reason}`",
                )
        else:
            await event.client.send_file(
                event.chat_id,
                joker_t8ed,
                caption=f"᯽︙تم تقييد المستخدم بنجاح ✓ : {_format.mentionuser(user.first_name ,user.id)} ",
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#تقييد المستخدم\n"
                    f"**المستخدم: **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**الدردشة: **{event.chat.title}(`{event.chat_id}`)",
                )
    except UserIdInvalidError:
        return await event.edit("يبدو أن تقييد هذا المستخدم تم إلغاؤه.")
    except UserAdminInvalidError:
        return await event.edit("يبدو أنك لست مشرفًا في المجموعة أو تحاول تقييد مشرف هنا.")
    except Exception as e:
        return await event.edit(f"`{str(e)}`")
@l313l.ar_cmd(
    pattern="الغاء تقييد(?:\s|$)([\s\S]*)",
    command=("الغاء تقييد", plugin_category),
    info={
        "header": "لالغاء التقيد المستخدم في المجموعة ",
        "description": "يقوم بالغاء المستخدم في المجموعة.",
        "usage": [
            "{tr}الغاء تقييد <userid/username/reply>",
            "{tr}الغاء تقييد <userid/username/reply> <reason>",
        ],
        "examples": ["{tr}الغاء تقييد @username لأسباب مختلفة"],
    },
    groups_only=True,
    require_admin=True,
)
async def cancel_t8ed(event):
    await event.delete()
    user, _ = await get_user_from_event(event)
    if not user:
        return
    if user.id == event.client.uid:
        return await event.client.send_message(event.chat_id, "عذرًا، لا يمكنك إلغاء تقييد نفسك.")
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=None, send_messages=False),
            )
        )
        await event.client.send_file(
            event.chat_id,
            joker_unt8ed,
            caption=f"**᯽︙ تم الغاء تقييد المستخدم {_format.mentionuser(user.first_name, user.id)} بنجاح ✅.**"
        )
    except UserIdInvalidError:
        return await event.client.send_message(event.chat_id, "يبدو أن التقييد على هذا المستخدم تم إلغاؤه بالفعل.")
    except UserAdminInvalidError:
        return await event.client.send_message(event.chat_id, "يبدو أنك لست مشرفًا في المجموعة أو تحاول إلغاء تقييد مشرف هنا.")
    except Exception as e:
        return await event.client.send_message(event.chat_id, f"`{str(e)}`")