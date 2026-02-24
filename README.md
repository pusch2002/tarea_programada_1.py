# Tarea Programada 1 – Estructuras de Datos  
I Cuatrimestre 2026  
Sebastian Puschendorf

## Descripción del Proyecto

Este proyecto simula el funcionamiento de archivos secuenciales de registros con tamaño fijo, utilizando únicamente la biblioteca estándar de Python.

El sistema permite:

- Generar un archivo binario (.bin) con registros ordenados ascendentemente por número de empleado.
- Recuperar registros por posición (acceso directo).
- Recuperar registros por número de empleado utilizando búsqueda binaria directamente sobre el archivo.

El archivo binario utiliza estructuras de tamaño fijo para permitir acceso aleatorio eficiente mediante cálculo de posición.

---

## Estructura del Proyecto

records.py                 → Lógica del sistema (modelo y servicios)  
generador_ordenado.py      → Genera archivo .bin ordenado  
buscador_registros.py      → Recupera registros por posición o búsqueda binaria  

---

## Estructura del Registro

Cada registro contiene:

- Número de empleado (entero positivo)
- Nombre
- Edad
- Fecha de nacimiento
- Provincia
- Cantón
- Distrito

Todos los campos son almacenados en formato binario con tamaño fijo utilizando el módulo `struct`.

---

## Cómo Ejecutar

### Generar archivo binario

Ejecutar en la terminal:
