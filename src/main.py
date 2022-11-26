import asyncio
from datetime import timedelta, datetime

import uvloop

from pyrogram import Client, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from core import log, context
from core import settings
from model import PinMessage

uvloop.install()
app = Client(
    "bot",
    api_id=settings.api_id,
    api_hash=settings.api_hash,
    bot_token=settings.token,
    in_memory=True,
)

IN_LINE_BUTTONS = InlineKeyboardMarkup(
    [
        [  # First row
            InlineKeyboardButton(  # Generates a callback query when pressed
                "+ день",
                callback_data="up:day"
            ),
            InlineKeyboardButton(  # Generates a callback query when pressed
                "+ неделя",
                callback_data="up:week"
            ),
            InlineKeyboardButton(  # Generates a callback query when pressed
                "не откреплять",
                callback_data="up:infinitely"
            ),
        ], [
        InlineKeyboardButton(  # Generates a callback query when pressed
            "сохранить",
            callback_data="up:ok"
        ),
    ],
    ]
)


def get_period_str(d: timedelta) -> str:
    if d.days > 0:
        if d.days == 1:
            m = f'{d.days} день'
        elif d.days in (2, 3, 4):
            m = f'{d.days} дня'
        else:
            m = f'{d.days} дней'
    else:
        h = d.seconds // 3600
        if h < 0:
            m = '~1 час'
        elif h == 1:
            m = f'{h} час'
        elif h in (2, 3, 4):
            m = f'{h} часа'
        else:
            m = f'{h} часов'
    return m


@app.on_message()
async def hello(client: Client, message: Message):
    if message.pinned_message:
        pin = await PinMessage.create(
            chat_id=message.chat.id,
            message_id=message.id,
            unpin_date=datetime.utcnow() + timedelta(days=1, hours=1),
        )

        diff = (pin.unpin_date - pin.created_at)
        await message.reply_text(
            text=f'Сообщение будет откреплено через {get_period_str(diff)}',
            disable_notification=True,
            reply_markup=IN_LINE_BUTTONS,
        )


@app.on_callback_query()
async def inline_query(client, query):
    data = query.data.split(':')[1]

    maps = {
        'day': timedelta(days=1),
        'week': timedelta(weeks=1),
    }

    pin = await PinMessage.query \
        .where(PinMessage.chat_id == query.message.chat.id) \
        .where(PinMessage.message_id == query.message.reply_to_message.id).gino.first()

    if data in ('infinitely', 'ok'):
        if data == 'infinitely':
            await pin.update(on_delete=True).apply()

        await query.message.delete()
    else:
        await pin.update(unpin_date=pin.unpin_date + maps[data]).apply()

        diff = pin.unpin_date - pin.created_at
        await query.message.edit_text(
            text=f'Сообщение будет откреплено через {get_period_str(diff)}',
            reply_markup=IN_LINE_BUTTONS,
        )
    await query.answer(text='ok')


async def looooooop():
    while True:
        if not context.on_run:
            await asyncio.sleep(settings.sleep)
            continue

        try:
            pins = await PinMessage.query \
                .where(PinMessage.on_delete == False) \
                .where(PinMessage.unpin_date < datetime.utcnow()) \
                .gino.all()
            for p in pins:
                m = await app.get_messages(p.chat_id, p.message_id)
                await m.unpin()
                await p.update(on_delete=True).apply()
        except Exception as ex:
            log.error(ex)
        await asyncio.sleep(settings.loop)


async def bot():
    loop = asyncio.get_event_loop()
    log.info('start app')

    await context.db.set_bind(settings.db)
    log.info('init db')

    context.on_run = True
    log.info('start app')

    loop.create_task(looooooop())
    await app.start()
    log.info('start bot')
    await idle()
    await app.stop()
    log.info('stop app')


if __name__ == '__main__':
    app.loop.create_task(looooooop())
    app.run(bot())
