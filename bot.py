import os
import re
import json
import logging
import asyncio
from telethon import TelegramClient, events
from datetime import datetime

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# متغيرات البيئة (آمنة للرفع على أي سيرفر)
API_ID = int(os.environ.get('API_ID', '24730698'))  # قم بتعيين القيمة الافتراضية الخاصة بك
API_HASH = os.environ.get('API_HASH', '37f0c59c6b394e390d143b5a7dd02040')  # قم بتعيين القيمة الافتراضية الخاصة بك
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8383976918:AAGUcYyRHyLDa4XgO9puXFUPJlaOiddljmA')  # قم بتعيين القيمة الافتراضية الخاصة بك
CONFIG_FILE = os.environ.get('CONFIG_FILE', 'bot_config.json')

class ChannelCopyBot:
    def __init__(self):
        self.client = None
        self.user_settings = self.load_config()
        self.copy_count = 0
        self.last_activity = datetime.now()

    def load_config(self):
        """تحميل الإعدادات من ملف JSON"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل الإعدادات: {e}")
        return {}

    def save_config(self):
        """حفظ الإعدادات في ملف JSON"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"خطأ في حفظ الإعدادات: {e}")

    async def start(self):
        """بدء تشغيل البوت"""
        self.client = TelegramClient('channel_copy_bot', API_ID, API_HASH)
        await self.client.start(bot_token=BOT_TOKEN)
        
        me = await self.client.get_me()
        logger.info(f"✅ البوت يعمل باسم: @{me.username}")
        
        self.register_handlers()
        await self.keep_alive()
        await self.client.run_until_disconnected()

    def register_handlers(self):
        """تسجيل جميع معالجات الأحداث"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.handle_start(event)

        @self.client.on(events.NewMessage(pattern='/set_source'))
        async def set_source_handler(event):
            await self.handle_set_source(event)

        @self.client.on(events.NewMessage(pattern='/set_target'))
        async def set_target_handler(event):
            await self.handle_set_target(event)

        @self.client.on(events.NewMessage(pattern='/start_copy'))
        async def start_copy_handler(event):
            await self.handle_start_copy(event)

        @self.client.on(events.NewMessage(pattern='/stop_copy'))
        async def stop_copy_handler(event):
            await self.handle_stop_copy(event)

        @self.client.on(events.NewMessage(pattern='/status'))
        async def status_handler(event):
            await self.handle_status(event)

        @self.client.on(events.NewMessage(pattern='/show_channels'))
        async def show_channels_handler(event):
            await self.handle_show_channels(event)

        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            await self.handle_message(event)

    async def handle_start(self, event):
        """معالجة أمر /start"""
        user_id = str(event.sender_id)
        settings = self.user_settings.get(user_id, {})
        
        response = (
            "✨ **بوت نسخ القنوات المتقدم** ✨\n\n"
            "الأوامر المتاحة:\n"
            "/set_source @القناة - تعيين قناة المصدر\n"
            "/set_target @القناة - تعيين قناة الهدف\n"
            "/start_copy - بدء النسخ\n"
            "/stop_copy - إيقاف النسخ\n"
            "/status - عرض الحالة\n\n"
            f"المصدر الحالي: {settings.get('source', 'غير معين')}\n"
            f"الهدف الحالي: {settings.get('target', 'غير معين')}\n"
            f"الحالة: {'🟢 نشط' if settings.get('active') else '🔴 متوقف'}\n"
            f"الرسائل المنسوخة: {self.copy_count}"
        )
        await event.reply(response)

    async def handle_set_source(self, event):
        """تعيين قناة المصدر"""
        try:
            args = event.message.text.split()
            if len(args) < 2:
                await event.reply("⚠ يرجى تحديد معرف القناة بعد الأمر")
                return
                
            source = args[1]
            if not source.startswith('@'):
                await event.reply("⚠ يجب أن يبدأ المعرف ب @")
                return
                
            user_id = str(event.sender_id)
            self.user_settings.setdefault(user_id, {})
            self.user_settings[user_id]['source'] = source
            self.save_config()
            
            await event.reply(f"✅ تم تعيين المصدر: {source}")
        except Exception as e:
            logger.error(f"خطأ في تعيين المصدر: {e}")
            await event.reply("❌ حدث خطأ أثناء تعيين المصدر")

    async def handle_set_target(self, event):
        """تعيين قناة الهدف"""
        try:
            args = event.message.text.split()
            if len(args) < 2:
                await event.reply("⚠ يرجى تحديد معرف القناة بعد الأمر")
                return
                
            target = args[1]
            if not target.startswith('@'):
                await event.reply("⚠ يجب أن يبدأ المعرف ب @")
                return
                
            user_id = str(event.sender_id)
            self.user_settings.setdefault(user_id, {})
            self.user_settings[user_id]['target'] = target
            self.save_config()
            
            await event.reply(f"✅ تم تعيين الهدف: {target}")
        except Exception as e:
            logger.error(f"خطأ في تعيين الهدف: {e}")
            await event.reply("❌ حدث خطأ أثناء تعيين الهدف")

    async def handle_start_copy(self, event):
        """بدء عملية النسخ"""
        user_id = str(event.sender_id)
        settings = self.user_settings.get(user_id, {})
        
        if not settings.get('source') or not settings.get('target'):
            await event.reply("⚠ يرجى تعيين المصدر والهدف أولاً")
            return
            
        settings['active'] = True
        self.save_config()
        await event.reply("🟢 تم تفعيل النسخ بنجاح!")

    async def handle_stop_copy(self, event):
        """إيقاف عملية النسخ"""
        user_id = str(event.sender_id)
        if user_id in self.user_settings:
            self.user_settings[user_id]['active'] = False
            self.save_config()
            await event.reply("⏸ تم إيقاف النسخ")
        else:
            await event.reply("⚠ لا يوجد نسخ نشط")

    async def handle_status(self, event):
        """عرض حالة البوت"""
        user_id = str(event.sender_id)
        settings = self.user_settings.get(user_id, {})
        
        status = (
            "📊 **حالة البوت**\n\n"
            f"👤 المستخدم: {user_id}\n"
            f"📌 المصدر: {settings.get('source', 'غير معين')}\n"
            f"🎯 الهدف: {settings.get('target', 'غير معين')}\n"
            f"🔄 الحالة: {'🟢 نشط' if settings.get('active') else '🔴 متوقف'}\n"
            f"📤 الرسائل المنسوخة: {self.copy_count}\n"
            f"⏱ آخر نشاط: {self.last_activity.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await event.reply(status)

    async def handle_show_channels(self, event):
        """عرض القنوات المحفوظة"""
        user_id = str(event.sender_id)
        settings = self.user_settings.get(user_id, {})
        
        if not settings:
            await event.reply("⚠ لا توجد إعدادات محفوظة")
            return
            
        response = (
            "💾 **الإعدادات المحفوظة**\n\n"
            f"المصدر: {settings.get('source', 'غير معين')}\n"
            f"الهدف: {settings.get('target', 'غير معين')}\n"
            f"الحالة: {'🟢 نشط' if settings.get('active') else '🔴 متوقف'}"
        )
        await event.reply(response)

    async def handle_message(self, event):
        """معالجة الرسائل الواردة"""
        try:
            self.last_activity = datetime.now()
            
            if not hasattr(event, 'chat') or not event.chat:
                return
                
            for user_id, settings in self.user_settings.items():
                if settings.get('active'):
                    source = settings.get('source', '').replace('@', '')
                    if hasattr(event.chat, 'username') and event.chat.username == source:
                        target = settings.get('target')
                        if target:
                            if event.message.text:
                                text = self.process_text(event.message.text)
                                if text:
                                    await self.client.send_message(target, text)
                                    self.copy_count += 1
                                    logger.info(f"تم نسخ رسالة إلى {target}")
                            elif event.message.media:
                                await event.forward_to(target)
                                self.copy_count += 1
                                logger.info(f"تم نسخ ميديا إلى {target}")
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {e}")

    def process_text(self, text):
        """معالجة النص قبل النسخ"""
        if not text:
            return None
            
        replacements = {
            r'https://t\.me/AutoGiftsBot\?start=_tgr_LFvVK5s4MWEy\d+': '@giftsarab',
            r'@GiftChangesUpdates\b': '@giftsarab',
            r'https://t\.me/tonnel_network_bot/gifts\?startapp=ref_\d+': 'https://t.me/tonnel_network_bot/gifts?startapp=ref_5299026409',
            r'https://t\.me/portals/market\?startapp=giftchanges': 'https://t.me/portals/market?startapp=fyn4zg',
            r'https://t\.me/\+pXR4UDEHF8VhOTRi': '',
            r'@GiftChanges\b': '@giftsarab',
            r'@GiftNews\b': '@giftsarab'
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
            
        return text.strip() if text.strip() else None

    async def keep_alive(self):
        """الحفاظ على اتصال البوت نشطًا"""
        async def ping():
             0  +
             
            while True:
                try:
                    await asyncio.sleep(300)
                    await self.client.send_message('me', 'ping')
                except:
                    pass
                    
        asyncio.create_task(ping())

async def main():
    bot = ChannelCopyBot()
    await bot.start()

if __name__ == '__main__':
    logger.info("🚀 بدء تشغيل بوت نسخ القنوات...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت")
    except Exception as e:
        logger.error(f"حدث خطأ غير متوقع: {e}")