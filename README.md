# CRUD de Contactos en Flask

Este proyecto es una aplicación web CRUD (Crear, Leer, Actualizar, Borrar) de contactos desarrollada con **Flask** y **MySQL**. Permite gestionar una agenda de contactos con autenticación de usuario y cambio de tema visual.

## Funcionalidad

- Registro y login de usuarios.
- Alta, baja, modificación y consulta de contactos.
- Cambio de tema (oscuro/claro) desde el menú superior.
- Confirmación visual de acciones mediante mensajes flash.
- Protección de rutas mediante autenticación.

## Estructura

- **crud.py**: Lógica principal de la aplicación Flask.
- **templates/**: Plantillas HTML (Bootstrap 5).
- **static/js/**: Archivos JavaScript para confirmaciones.
- **requirements.txt**: Dependencias del proyecto.
- **Dockerfile**: Para despliegue en contenedor Docker.

## Variables de entorno necesarias

```env
FLASK_SECRET_KEY=   # Clave secreta para sesiones Flask
MYSQL_USER=         # Usuario de MySQL
MYSQL_PASSWORD=     # Contraseña de MySQL
MYSQL_DB=           # Nombre de la base de datos
MYSQL_HOST=         # Host de la base de datos
```

## Instalación y ejecución

1. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

2. Crea la base de datos y las tablas necesarias en MySQL, por ejemplo:
    ```sql
    CREATE TABLE usuarios (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(255) NOT NULL,
        hash VARCHAR(255) NOT NULL
    );

    CREATE TABLE contactos (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        tel VARCHAR(30) NOT NULL,
        email VARCHAR(100) NOT NULL
    );
    ```

3. Ejecuta la aplicación:
    ```bash
    docker compose up -d --build
    ```

## Uso

- Accede a la aplicación en [http://localhost:8000](http://localhost:8000)
- Regístrate y comienza a gestionar tus contactos.

---

> Este README corresponde únicamente a la funcionalidad CRUD de la carpeta `crud/`.