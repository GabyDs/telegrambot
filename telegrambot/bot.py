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


async def send_mqtt_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    topic: str,
    payload: str,
    success_msg: str,
):
    """Función auxiliar para enviar comandos MQTT"""
    mqtt_client = context.application.bot_data.get("mqtt_client")

    if mqtt_client:
        try:
            await mqtt_client.publish(topic, payload)
            await update.message.reply_text(success_msg)
            logger.info(f"Mensaje enviado al tópico {topic}: {payload}")
        except Exception as e:
            logger.error(f"Error al enviar MQTT: {e}")
            await update.message.reply_text("Error al enviar el comando.")
    else:
        await update.message.reply_text("Cliente MQTT no disponible.")


async def setpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /setpoint <valor>")
        return

    try:
        valor = float(context.args[0])
        payload = f'{{"setpoint": {valor}}}'
        await send_mqtt_command(
            update, context, TOPICOS["setpoint"], payload, f"Setpoint enviado: {valor}"
        )

    except ValueError:
        await update.message.reply_text("El valor debe ser numérico.")


async def modo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /modo <manual|automatico>")
        return

    modo_str = context.args[0].lower()
    if modo_str not in ("manual", "automatico"):
        await update.message.reply_text("Modo inválido. Use 'manual' o 'automatico'.")
        return

    payload = f'{{"modo": "{modo_str}"}}'
    await send_mqtt_command(
        update, context, TOPICOS["modo"], payload, f"Modo configurado a: {modo_str}"
    )


async def periodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /periodo <valor_en_segundos>")
        return

    if not context.args[0].isdigit():
        await update.message.reply_text("El valor debe ser un número entero positivo.")
        return

    valor = context.args[0]
    payload = f'{{"periodo": {valor}}}'
    await send_mqtt_command(
        update,
        context,
        TOPICOS["periodo"],
        payload,
        f"Periodo configurado a: {valor} segundos",
    )


async def destello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = '{"destello": 1}'
    await send_mqtt_command(
        update,
        context,
        TOPICOS["destello"],
        payload,
        "LED destello activado en la Raspberry",
    )


async def rele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /rele <1|0>")
        return

    valor = context.args[0]
    if valor not in ("1", "0"):
        await update.message.reply_text(
            "El valor debe ser 1 (encendido) o 0 (apagado)."
        )
        return

    payload = f'{{"rele": {valor}}}'
    await send_mqtt_command(
        update, context, TOPICOS["rele"], payload, f"Rele configurado a: {valor}"
    )


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
    logger.info("Inicializando cliente MQTT...")
    mqtt_client = await connect_mqtt()
    if mqtt_client:
        application.bot_data["mqtt_client"] = mqtt_client
        logger.info("Cliente MQTT almacenado en bot_data")
    else:
        logger.error("No se pudo inicializar el cliente MQTT")
        application.bot_data["mqtt_client"] = None


if __name__ == "__main__":
    logger.info("Iniciando bot y cliente MQTT...")

    application = Application.builder().token(TOKEN).build()

    application.post_init = post_init

    # Handlers de comandos
    handlers = [
        ("start", start),
        ("setpoint", setpoint),
        ("modo", modo),
        ("periodo", periodo),
        ("destello", destello),
        ("rele", rele),
    ]

    for command, handler in handlers:
        application.add_handler(CommandHandler(command, handler))

    application.run_polling()
