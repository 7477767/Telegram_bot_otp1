from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8477822565:AAGhqerrsD2HTO5tGsXvi3LV0Fuh2DvJ3_Y"
ADMIN_ID = 6568634089

users = set()
stock = {}

# 🔥 CHANNEL LIST
CHANNELS = [
    {"name": "Channel 1", "link": "https://t.me/OX_OFFLINE_CHANNEL"},
    {"name": "Channel 2", "link": "https://t.me/OX_OFFLINE_OTP"},
    {"name": "Channel 3", "link": "https://t.me/OX_OFFLINE_EARNING"},
    {"name": "Channel 4", "link": "https://t.me/OX_OFFLINE_BACKUP"},
]


# Start (UPDATED ONLY THIS PART)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # 👇 check new or old user
    is_new_user = user_id not in users
    users.add(user_id)

    # 👇 welcome back
    if not is_new_user:
        await update.message.reply_text("👋 Welcome back!")
        return

    context.user_data["joined"] = set()

    keyboard = []

    for i, ch in enumerate(CHANNELS):
        keyboard.append([
            InlineKeyboardButton(ch["name"], url=ch["link"])
        ])

    keyboard.append([
        InlineKeyboardButton("✅ Verify", callback_data="verify_user")
    ])

    await update.message.reply_text(
        "🔐 Click all channels then press Verify:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= USER ================= #

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text

    if text == "📱 Get Number":

        keyboard = []

        for country, numbers in stock.items():
            if len(numbers) > 0:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{country} WhatsApp ({len(numbers)})",
                        callback_data=f"country_{country}"
                    )
                ])

        if len(keyboard) == 0:
            await update.message.reply_text("❌ No country available")
            return

        await update.message.reply_text(
            "🌍 Select Country:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif text == "📊 Live Stock":
        total = sum(len(v) for v in stock.values())
        await update.message.reply_text(f"📦 Total Stock: {total}")

    elif text == "🎧 Support":
        await update.message.reply_text("Contact Admin")

    elif text == "👥 Invite & Earn":
        await update.message.reply_text("Coming soon...")


# ================= BUTTON ================= #

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # ✅ VERIFY
    if data == "verify_user":
        keyboard = [
            ["📱 Get Number", "📊 Live Stock"],
            ["👥 Invite & Earn"],
            ["🎧 Support"]
        ]

        await query.message.reply_text(
            "✅ Verified! Welcome!",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return

    elif data.startswith("country_"):
        country = data.split("_")[1]
        numbers = stock.get(country, [])

        if not numbers:
            await query.edit_message_text("❌ No number available")
            return

        number = numbers.pop(0)
        context.user_data["last_country"] = country

        keyboard = [
            [
                InlineKeyboardButton("🔄 Next Number", callback_data="next_number"),
                InlineKeyboardButton("🔙 Back", callback_data="back")
            ],
            [
                InlineKeyboardButton("📩 OTP Group", url="https://t.me/OX_OFFLINE_OTP")
            ]
        ]

        await query.edit_message_text(
            f"📱 {country} WhatsApp Number:\n\n`{number}`\n\n"
            f"📩 OTP will be delivered via our OTP Group.\n"
            f"🔗 Join the group to receive your OTP instantly.\n\n"
            f"⚠️ Important: Do not share this number with anyone.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "next_number":
        country = context.user_data.get("last_country")

        if not country:
            await query.answer("❌ Error", show_alert=True)
            return

        numbers = stock.get(country, [])

        if not numbers:
            await query.edit_message_text("❌ No more numbers available")
            return

        number = numbers.pop(0)

        keyboard = [
            [
                InlineKeyboardButton("🔄 Next Number", callback_data="next_number"),
                InlineKeyboardButton("🔙 Back", callback_data="back")
            ],
            [
                InlineKeyboardButton("📩 OTP Group", url="https://t.me/YOUR_GROUP_LINK")
            ]
        ]

        await query.edit_message_text(
            f"📱 {country} WhatsApp Number:\n\n`{number}`\n\n"
            f"📩 OTP will be delivered via our OTP Group.\n"
            f"🔗 Join the group to receive your OTP instantly.\n\n"
            f"⚠️ Important: Do not share this number with anyone.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back":
        keyboard = []

        for country, numbers in stock.items():
            if len(numbers) > 0:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{country} WhatsApp ({len(numbers)})",
                        callback_data=f"country_{country}"
                    )
                ])

        if len(keyboard) == 0:
            await query.edit_message_text("❌ No country available")
            return

        await query.edit_message_text(
            "🌍 Select Country:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ================= TXT FILE ================= #

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    doc = update.message.document

    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Only TXT file allowed")
        return

    file = await doc.get_file()
    path = await file.download_to_drive()

    country = "India"

    if country not in stock:
        stock[country] = []

    added = 0

    with open(path, "r") as f:
        for line in f:
            num = line.strip().replace("+", "").replace(" ", "")

            if not num:
                continue

            stock[country].append(num)
            added += 1

    await update.message.reply_text(f"✅ {added} numbers added to {country}")


# ================= ADMIN ================= #

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    keyboard = [
        ["👥 Total Users"],
        ["📢 Broadcast"],
        ["➕ Add Stock"]
    ]

    await update.message.reply_text(
        "🔐 Admin Panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "👥 Total Users":
        await update.message.reply_text(f"Total Users: {len(users)}")

    elif text == "📢 Broadcast":
        context.user_data["broadcast"] = True
        await update.message.reply_text("Send message:")

    elif text == "➕ Add Stock":
        context.user_data["add_stock"] = True
        await update.message.reply_text(
            "Format:\nCountry:number,number\nExample:\nOman:96812345678,96898765432"
        )

    elif context.user_data.get("broadcast"):
        for user in users:
            try:
                await context.bot.send_message(chat_id=user, text=text)
            except:
                pass
        context.user_data["broadcast"] = False
        await update.message.reply_text("✅ Broadcast sent")

    elif context.user_data.get("add_stock"):
        try:
            country, numbers = text.split(":")
            country = country.strip().title()

            numbers = numbers.split(",")

            cleaned = [n.replace("+", "").replace(" ", "").strip() for n in numbers]

            if country not in stock:
                stock[country] = []

            stock[country].extend(cleaned)

            await update.message.reply_text(f"✅ {country} stock added")

        except:
            await update.message.reply_text("❌ Wrong format")

        context.user_data["add_stock"] = False


# ================= MAIN ================= #

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(CallbackQueryHandler(button_click))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_actions))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
