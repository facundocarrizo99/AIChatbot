# **Correr el proyecto**

Esta guía describe cómo utilizar nuestro asistente de WhatsApp utilizando la API en la nube de Meta (anteriormente Facebook) con Python puro, específicamente con el framework Flask. También se integrarán eventos vía webhook para recibir mensajes en tiempo real, e incorporar respuestas automáticas generadas mediante inteligencia artificial.

## **Requisitos Previos**

1. Tener conocimientos básicos de Python.
2. Solicitar al administrador el acceso a:
    - Una cuenta de desarrollador en Meta.
    - Una aplicación empresarial de Meta con acceso a la API de WhatsApp.
    - La plataforma de inteligencia artificial (por ejemplo, OpenAI).
    - Un dominio y acceso a túneles seguros como ngrok.
    - La base de datos MongoDB utilizada por el bot.

## **Tabla de Contenidos**

- [Crear un Bot de WhatsApp con Python y Flask](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Requisitos Previos](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Tabla de Contenidos](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Comenzar](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Paso 1: Seleccionar Números de Teléfono](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Paso 2: Enviar Mensajes con la API](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Paso 3: Configurar Webhooks para Recibir Mensajes](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)
    - [Próximos Pasos](https://www.notion.so/Documentation-1b56583c45b480b1a90ac723548e0037?pvs=21)

## **Comenzar**

Antes de realizar pruebas, es necesario clonar el repositorio del proyecto y ejecutar la aplicación localmente. Para ello:

1. Clonar el repositorio:

```
git clone https://github.com/daveebbelaar/python-whatsapp-bot.git
cd python-whatsapp-bot
```

1. 
2. Instalar las dependencias:

```
pip install -r requirements.txt
```

1. 
2. Ejecutar la aplicación:

```
python run.py
```

Asegurarse de tener el entorno configurado correctamente y de haber solicitado previamente acceso a las credenciales necesarias.

## **Paso 1: Seleccionar Números de Teléfono**

1. Asegurarse de que WhatsApp esté habilitado en la aplicación correspondiente.
2. Se comenzará con un número de prueba proporcionado por la plataforma, el cual puede enviar mensajes a hasta 5 números diferentes.
3. Desde la configuración de la API, identificar el número de prueba desde el cual se enviarán los mensajes.
4. Se pueden añadir otros números de destino, incluido el propio número de WhatsApp del usuario.
5. Para verificar el número, se recibirá un código vía mensaje de WhatsApp en el dispositivo correspondiente.

## **Paso 2: Enviar Mensajes con la API**

1. Solicitar al administrador un token de acceso válido.
2. El administrador también podrá proveer ejemplos de cómo enviar mensajes desde Python.
3. Crear un archivo .env basado en un ejemplo proporcionado y completar las variables necesarias con los datos provistos.
4. Ejecutar la aplicación para enviar un mensaje de prueba. El mensaje puede tardar entre 60 y 120 segundos en llegar.

## **Paso 3: Configurar Webhooks para Recibir Mensajes**

1. Solicitar al administrador acceso al dominio de prueba (ngrok) y configurar el endpoint para recibir los mensajes.
2. En el panel de la aplicación de Meta, dirigirse a WhatsApp > Configuración y editar la URL del webhook.
3. Ingresar la URL proporcionada por ngrok y añadir /webhook al final.
4. Definir un token de verificación personalizado y establecerlo como variable de entorno.
5. Asegurarse de que la aplicación local registre correctamente la verificación del webhook en la consola.
6. Suscribirse al campo **messages** en el panel de configuración del webhook.
7. Probar la suscripción enviando un mensaje de prueba desde Meta.
8. Verificar que el bot reciba y procese correctamente los mensajes, mostrando tanto encabezados como cuerpo del mensaje en la consola.

## **Próximos Pasos**

Una vez verificado que el bot responde correctamente, se podrá avanzar en el desarrollo de funcionalidades personalizadas. Para esto, será necesario solicitar acceso a la base de datos MongoDB donde se almacenan y consultan los datos de los usuarios y conversaciones.
