# Natursur - Proyecto Django PGPI

Proyecto web para Natursur desarrollado en Django

## 🚀 Características

- Tienda online de productos naturales (Puente hacia Herbalife)
- Sistema de citas para masajes
- Integración con Herbalife
- Notificaciones automáticas


## 🛠️ Instalación

1. Clonar el repositorio: `git clone 'url'`
2. Crear entorno virtual: `python -m venv .venv`
3. Activar entorno: `.\.venv\Scripts\activate.bat`
4. Instalar Django: `python -m pip install Django`
5. Instalar dependencias: `pip install -r requirements.txt`
6. Migrar base de datos: `python manage.py migrate`
7. Ejecutar servidor: `python manage.py runserver`


## 🌿 Política de ramas

### **Estructura de ramas:**
- `main` -> Rama principal (solo código probado)
- `feature/nombre-feature` -> Nuevas funcionalidades
- `fix/nombre-error` -> Corrección de bugs
- `docs/nombre-doc` -> Documentación

### **Flujo de trabajo:**
1. Crear rama desde `main`: `git checkout -b feature/nombre`
2. Desarrollar la feature
3. Hacer commits descriptivos (titulo corto pero claro)
4. Subir cambios de la rama: `git push -u origin feature/nombre`
5. Fusionar con `main` después de aprobarse: `git checkout main`  --  `git merge feature/nombre-feature`


## 👥 Equipo
- Jesús García Pérez
- Ángel Mateos Marín
- Rares Nicolae Petre
- Felipe Peña Núñez
- Marta Recio Gil