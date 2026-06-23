from openai import OpenAI
import os
import json
import shutil

# Apuntamos al servidor LOCAL de Ollama (no a la nube)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama no valida esto, pero el SDK lo pide igual
)

# --- Definimos las "herramientas" que el agente puede usar ---

def crear_carpeta(nombre):
    try:
        os.makedirs(nombre, exist_ok=True)
        return f"Carpeta '{nombre}' creada exitosamente."
    except Exception as e:
        return f"Error creando la carpeta: {str(e)}"

def listar_archivos(ruta="."):
    try:
        archivos = os.listdir(ruta)
        return f"Archivos en '{ruta}': {', '.join(archivos)}"
    except Exception as e:
        return f"Error listando archivos: {str(e)}"

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        return contenido[:1000]
    except FileNotFoundError:
        return f"No encontré el archivo '{ruta}'."
    except Exception as e:
        return f"Error leyendo el archivo: {str(e)}"

def escribir_archivo(ruta, contenido):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Archivo '{ruta}' creado con el contenido especificado."
    except Exception as e:
        return f"Error creando el archivo: {str(e)}"

def mover_archivo(origen, destino):
    try:
        shutil.move(origen, destino)
        return f"Movido de '{origen}' a '{destino}' exitosamente."
    except FileNotFoundError:
        return f"No encontré el archivo de origen '{origen}'."
    except Exception as e:
        return f"Error moviendo el archivo: {str(e)}"

# Esto le describe al modelo qué herramientas existen y cómo usarlas
herramientas = [
    {
        "type": "function",
        "function": {
            "name": "crear_carpeta",
            "description": "Crea una carpeta nueva en el sistema de archivos",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre de la carpeta a crear"}
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_archivos",
            "description": "Lista los archivos y carpetas en una ruta",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {"type": "string", "description": "Ruta a listar, usa '.' para la carpeta actual"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escribir_archivo",
            "description": "Crea un archivo de texto con un contenido específico en la ruta indicada",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {"type": "string", "description": "Ruta y nombre del archivo a crear, ej: prueba.txt"},
                    "contenido": {"type": "string", "description": "Texto que va dentro del archivo"}
                },
                "required": ["ruta", "contenido"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "leer_archivo",
            "description": "Lee y devuelve el contenido de un archivo de texto existente",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {"type": "string", "description": "Ruta del archivo a leer"}
                },
                "required": ["ruta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mover_archivo",
            "description": "Mueve o renombra un archivo de una ruta a otra",
            "parameters": {
                "type": "object",
                "properties": {
                    "origen": {"type": "string", "description": "Ruta actual del archivo"},
                    "destino": {"type": "string", "description": "Nueva ruta o nombre del archivo"}
                },
                "required": ["origen", "destino"]
            }
        }
    }
]

# Diccionario para llamar la función real según el nombre que decida el modelo
funciones_disponibles = {
    "crear_carpeta": crear_carpeta,
    "listar_archivos": listar_archivos,
    "escribir_archivo": escribir_archivo,
    "leer_archivo": leer_archivo,
    "mover_archivo": mover_archivo
}

def chat_con_agente(mensaje_usuario):
    mensajes = [{"role": "user", "content": mensaje_usuario}]

    # Límite de seguridad para que no se quede en loop infinito si algo sale mal
    max_pasos = 6

    for paso in range(max_pasos):
        respuesta = client.chat.completions.create(
            model="qwen2.5:7b",
            messages=mensajes,
            tools=herramientas
        )

        mensaje = respuesta.choices[0].message

        # Si el modelo YA NO necesita usar herramientas, nos da la respuesta final
        if not mensaje.tool_calls:
            print(mensaje.content)
            return

        # Si SÍ decidió usar una o más herramientas, las ejecutamos
        # y le agregamos tanto su decisión como el resultado al historial
        mensajes.append(mensaje)

        for tool_call in mensaje.tool_calls:
            nombre_funcion = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)

            print(f"\n[El agente decidió usar: {nombre_funcion} con argumentos: {argumentos}]")

            resultado = funciones_disponibles[nombre_funcion](**argumentos)
            print(f"[Resultado: {resultado}]")

            # Le devolvemos el resultado al modelo para que decida el siguiente paso
            mensajes.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(resultado)
            })

    print("\n[El agente llegó al límite de pasos sin terminar la tarea]")

# --- Loop para chatear con tu agente desde la terminal ---
if __name__ == "__main__":
    print("Agente listo. Escribe tu instrucción (o 'salir' para terminar):\n")
    while True:
        entrada = input("Tú: ")
        if entrada.lower() == "salir":
            break
        chat_con_agente(entrada)