# Bot de Telegram para control del termostato IoT

Este bot de Telegram complementa el ejercicio de la Raspberry Pi Pico con sensor y control de temperatura mediante MQTT. Permite al usuario interactuar con el dispositivo remoto enviando órdenes vía MQTT sobre una conexión segura (MQTTS).

[Ejercico Anterior](https://github.com/GabyDs/Ejercicio-Sensor-con-MQTT/tree/main)

## Funcionalidad

A través de comandos en Telegram, el bot publica en tópicos MQTT las órdenes que controlan los parámetros del termostato implementado en la Raspberry Pi Pico.

### Comandos disponibles

- `/start`  
  Muestra un mensaje de bienvenida con la lista de comandos disponibles.

- `/setpoint <valor>`  
  Define un nuevo setpoint de temperatura. Ejemplo: `/setpoint 25.5`

- `/modo <manual|automatico>`  
  Cambia el modo de funcionamiento del termostato.  
  Ejemplo: `/modo automatico`

- `/periodo <segundos>`  
  Configura el intervalo de publicación de datos del sensor.  
  Ejemplo: `/periodo 10`

- `/rele <1|0>`  
  Activa (`1`) o desactiva (`0`) el relé, solo si el modo actual es manual.  
  Ejemplo: `/rele 1`

- `/destello`  
  Solicita a la Raspberry Pi que parpadee el LED integrado.

## MQTT - Tópicos utilizados

El bot publica en los siguientes tópicos:

- `ID_DEL_DISPOSITIVO/setpoint`
- `ID_DEL_DISPOSITIVO/periodo`
- `ID_DEL_DISPOSITIVO/modo`
- `ID_DEL_DISPOSITIVO/rele`
- `ID_DEL_DISPOSITIVO/destello`

> Donde `ID_DEL_DISPOSITIVO` es el identificador único del dispositivo definido por la Raspberry Pi Pico.

## Seguridad

- La comunicación con el broker MQTT se realiza utilizando TLS (MQTTS).
- El bot usa certificados del sistema para validar la conexión segura.
- El acceso al bot puede restringirse a ciertos usuarios usando validación por ID de Telegram o contraseña (opcional).

## Dependencias

- Python 3.11
- `python-telegram-bot`
- `aiomqtt`
- `certifi`

## Ejecución

Este bot puede ejecutarse como contenedor Docker o directamente en un entorno Python. Las variables de entorno necesarias son:

```env
TB_TOKEN=          # Token del bot de Telegram
DOMINIO=           # Dirección del broker MQTT
PUERTO_MQTTS=      # Puerto MQTT (usualmente 8883)
MQTT_USR=          # Usuario del broker MQTT
MQTT_PASS=         # Contraseña del broker MQTT

ID_DEL_DISPOSITIVO= # Identificador único de la raspberry
TOPICO_SETPOINT=    # Tópico para el setpoint
TOPICO_PERIODO=     # Tópico para el periodo
TOPICO_MODO=        # Tópico para el modo
TOPICO_RELE=        # Tópico para el relé
TOPICO_DESTELLO=    # Tópico para el destello