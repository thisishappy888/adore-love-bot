from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_profile_inline_kb(profile_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"like:{profile_user_id}"),
                InlineKeyboardButton(text="💬", callback_data="message"),
                InlineKeyboardButton(text="👎", callback_data=f"dislike:{profile_user_id}"),
            ]
        ]
    )


def mutual_like_profile_inline_kb(profile_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"like:{profile_user_id}"),
                InlineKeyboardButton(text="👎", callback_data=f"dislike:{profile_user_id}"),
            ]
        ]
    )
