# Agente de IA local con Function Calling

Agente conversacional que ejecuta acciones reales sobre el sistema de archivos a partir de instrucciones en lenguaje natural. Corre 100% local usando **Qwen2.5 7B** a través de **Ollama**, sin depender de ninguna API en la nube.

## ¿Qué hace?

El agente entiende instrucciones como:
- "crea una carpeta llamada proyectos"
- "lee el archivo notas.txt"
- "mueve notas.txt a la carpeta archivados"

Y decide por sí mismo qué herramienta usar, ejecuta la acción real en el sistema, y puede encadenar varios pasos para completar tareas más complejas (razonamiento multi-paso).

## Cómo funciona

1. El usuario escribe una instrucción en lenguaje natural.
2. El modelo (Qwen2.5 7B, corriendo local vía Ollama) decide si necesita usar alguna herramienta para responder.
3. Si decide usar una, el agente la ejecuta de verdad en el sistema de archivos.
4. El resultado se le devuelve al modelo, que decide si necesita otro paso o ya puede dar la respuesta final.
5. Esto se repite hasta que la tarea se completa (o hasta un límite de seguridad de pasos).

## Herramientas disponibles

| Herramienta | Qué hace |
|---|---|
| `crear_carpeta` | Crea una carpeta nueva |
| `listar_archivos` | Lista archivos y carpetas en una ruta |
| `leer_archivo` | Lee el contenido de un archivo de texto |
| `escribir_archivo` | Crea un archivo con contenido específico |
| `mover_archivo` | Mueve o renombra un archivo |

## Stack técnico

- **Python 3.11**
- **Ollama** — para correr el modelo localmente
- **Qwen2.5 7B** — modelo con buen soporte de function calling
- **SDK de OpenAI** — usado como cliente, apuntando al endpoint local de Ollama (compatible con su formato)

## Cómo correrlo

1. Instala [Ollama](https://ollama.com) y descarga el modelo:
```bash
ollama pull qwen2.5:7b
```

2. Clona este repositorio y crea un entorno virtual:
```bash
git clone https://github.com/TU_USUARIO/agente-ia-archivos.git
cd agente-ia-archivos
python -m venv venv
venv\Scripts\activate
pip install openai
```

3. Corre el agente:
```bash
python agente.py
```

## Por qué lo construí

Este proyecto es mi base para aprender orquestación de agentes de IA desde cero — entendiendo function calling, manejo de errores, y razonamiento multi-paso antes de escalar a sistemas más complejos (integración con WhatsApp, múltiples agentes coordinados, y eventualmente, agentes que controlan sistemas robóticos vía ROS2).

## Próximos pasos

- [ ] Conectar el agente a WhatsApp Cloud API para atención al cliente
- [ ] Agregar memoria de conversación entre sesiones
- [ ] Sumar herramientas específicas para agendar citas y gestionar datos de clientes
