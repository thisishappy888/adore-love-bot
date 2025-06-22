from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👍", callback_data="like"),
            InlineKeyboardButton(text="💬", callback_data="message"),
            InlineKeyboardButton(text="👎", callback_data="dislike")
        ]
    ],
)