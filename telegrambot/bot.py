import os, ssl, logging, aiomqtt, asyncio

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

async def connect_mqtt():
    """Conecta al broker MQTT"""
    global mqtt_client
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
        return True
    except Exception as e:
        logger.error(f"Error al conectar MQTT: {e}")
        return False

async def main():
    logger.info("Iniciando bot y cliente MQTT...")
    
    # Conectar MQTT
    if not await connect_mqtt():
        logger.error("No se pudo conectar a MQTT. Saliendo...")
        return

if __name__ == "__main__":
    asyncio.run(main())