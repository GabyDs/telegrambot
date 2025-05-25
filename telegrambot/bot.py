import os, ssl, logging, aiomqtt, asyncio
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# Logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelegramBot")

# MQTT TLS context
tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
tls_context.verify_mode = ssl.CERT_REQUIRED
tls_context.check_hostname = True
tls_context.load_default_certs()


# Variables de entorno
TOKEN = os.environ["TB_TOKEN"]
BROKER = os.environ["DOMINIO"]
PUERTO = int(os.environ["PUERTO_MQTTS"])
MQTT_USR = os.environ["MQTT_USR"]
MQTT_PASS = os.environ["MQTT_PASS"]
ID_DEL_DISPOSITIVO = os.environ["ID_DEL_DISPOSITIVO"]

# Tópicos MQTT
TOPICOS = {
    "setpoint": f"{ID_DEL_DISPOSITIVO}/{os.environ['TOPICO_SETPOINT']}",
    "modo": f"{ID_DEL_DISPOSITIVO}/{os.environ['TOPICO_MODO']}",
    "periodo": f"{ID_DEL_DISPOSITIVO}/{os.environ['TOPICO_PERIODO']}",
    "destello": f"{ID_DEL_DISPOSITIVO}/{os.environ['TOPICO_DESTELLO']}",
    "rele": f"{ID_DEL_DISPOSITIVO}/{os.environ['TOPICO_RELE']}",
}


async def connect_mqtt():
    """Conecta al broker MQTT"""
    try:
        mqtt_client = aiomqtt.Client(
            BROKER,
            username=MQTT_USR,
            password=MQTT_PASS,
            port=PUERTO,
            tls_context=tls_context,
        )
        await mqtt_client.__aenter__()
        logger.info("Cliente MQTT conectado exitosamente")
        return mqtt_client
    except Exception as e:
        logger.error(f"Error al conectar MQTT: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Comandos disponibles:\n"
        "/setpoint <valor>\n"
        "/modo <manual|automatico>\n"
        "/periodo <segundos>\n"
        "/destello\n"
        "/rele <1|0>"
    )


async def post_init(application: Application):
    """Inicializa el cliente MQTT después de crear la aplicación"""
    mqtt_client = await connect_mqtt()
    application.bot_data["mqtt_client"] = mqtt_client


async def main():
    logger.info("Iniciando bot y cliente MQTT...")

    # Crear aplicación
    application = Application.builder().token(TOKEN).build()

    # Configurar callbacks
    application.post_init = post_init

    # Handlers de comandos
    handlers = [
        ("start", start),
    ]

    for command, handler in handlers:
        application.add_handler(CommandHandler(command, handler))

    # Inicializar y ejecutar
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        logger.info("Bot iniciado. Presiona Ctrl+C para detener.")

        # Mantener el bot corriendo
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Deteniendo bot...")

    finally:
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
