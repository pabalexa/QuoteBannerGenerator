from PIL import Image, ImageDraw, ImageFont
import os
import csv
import random

def crear_imagen_con_texto(
    texto: str,
    ancho: int,
    alto: int,
    ruta_fuente: str,
    nombre_fuente: str,
    color_texto: tuple,
    color_fondo: tuple | None,
    tamano_fuente_max: int,
    tamano_fuente_min: int
) -> Image.Image:
    """
    Crea una imagen con texto optimizado para llenar el espacio disponible.
    """

    def obtener_dimensiones_texto(texto: str, fuente: ImageFont.FreeTypeFont) -> tuple:
        """Obtiene las dimensiones que ocuparía el texto con una fuente dada."""
        ancho_texto = fuente.getlength(texto)
        ascent, descent = fuente.getmetrics()
        alto_linea = ascent + descent
        return (ancho_texto, alto_linea, ascent, descent)

    def obtener_dimensiones_lineas(lineas: list, fuente: ImageFont.FreeTypeFont) -> tuple:
        """Obtiene las dimensiones totales que ocuparían las líneas de texto."""
        ancho_maximo = 0
        dimensiones_por_linea = []
        ascent, descent = fuente.getmetrics()
        alto_linea = ascent + descent
        espacio_entre_lineas = int(fuente.size * 0.3)

        for linea in lineas:
            ancho_linea = fuente.getlength(linea)
            ancho_maximo = max(ancho_maximo, ancho_linea)
            dimensiones_por_linea.append((ancho_linea, alto_linea, ascent, descent))

        altura_total = len(lineas) * alto_linea + (len(lineas) - 1) * espacio_entre_lineas if len(lineas) > 0 else 0

        return ancho_maximo, altura_total, dimensiones_por_linea, espacio_entre_lineas

    def ajustar_texto(texto: str, fuente: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Ajusta el texto para que quepa en el ancho máximo."""
        palabras = texto.split()
        lineas = []
        linea_actual = []
        ancho_actual = 0

        for palabra in palabras:
            ancho_palabra, _, _, _ = obtener_dimensiones_texto(palabra, fuente)
            ancho_espacio = fuente.getlength(" ")

            if not linea_actual:
                if ancho_palabra <= max_width:
                    linea_actual.append(palabra)
                    ancho_actual = ancho_palabra
                else:
                    return None
                continue

            if ancho_actual + ancho_espacio + ancho_palabra <= max_width:
                linea_actual.append(palabra)
                ancho_actual += ancho_espacio + ancho_palabra
            else:
                lineas.append(' '.join(linea_actual))
                linea_actual = [palabra]
                ancho_actual = ancho_palabra

        if linea_actual:
            lineas.append(' '.join(linea_actual))

        return lineas

    def encontrar_mejor_tamano_fuente():
        """Encuentra el mejor tamaño de fuente que maximice el uso del espacio."""
        margen = 20  # margen en cada lado
        area_disponible = (ancho - margen * 2) * (alto - margen * 2)
        mejor_tamano = tamano_fuente_min
        mejor_relacion = 0
        mejores_lineas = None

        for tamano in range(tamano_fuente_max, tamano_fuente_min - 1, -1):
            fuente = ImageFont.truetype(os.path.join(ruta_fuente, nombre_fuente), tamano)
            lineas = ajustar_texto(texto, fuente, ancho - margen * 2)

            if lineas is None:
                continue

            ancho_total, altura_total, _, _ = obtener_dimensiones_lineas(lineas, fuente)

            if altura_total > alto - margen * 2 or ancho_total > ancho - margen * 2:
                continue

            area_texto = ancho_total * altura_total
            relacion_area = area_texto / area_disponible

            if relacion_area > mejor_relacion:
                mejor_relacion = relacion_area
                mejor_tamano = tamano
                mejores_lineas = lineas

        fuente_final = ImageFont.truetype(os.path.join(ruta_fuente, nombre_fuente), mejor_tamano)
        return mejor_tamano, mejores_lineas, fuente_final

    tamano_optimo, lineas_ajustadas, fuente = encontrar_mejor_tamano_fuente()

    if color_fondo is None:
        modo = 'RGBA'
        extension = '.png'
        color_fondo = (0, 0, 0, 0)
    else:
        modo = 'RGB'
        extension = '.jpg'

    imagen = Image.new(modo, (ancho, alto), color_fondo)
    draw = ImageDraw.Draw(imagen)

    ancho_total, altura_total, dimensiones_lineas, espacio_entre_lineas = obtener_dimensiones_lineas(lineas_ajustadas, fuente)

    y_inicial = (alto - altura_total) // 2
    y_inicial = max(y_inicial, 0)

    y_actual = y_inicial
    for i, linea in enumerate(lineas_ajustadas):
        ancho_linea = dimensiones_lineas[i][0]
        x = (ancho - ancho_linea) // 2

        draw.text((x, y_actual), linea, font=fuente, fill=color_texto)

        y_actual += dimensiones_lineas[i][1] + espacio_entre_lineas

    return imagen

if __name__ == "__main__":
    # Obtener la ruta del directorio donde está ubicado el archivo Python
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Definir rutas predeterminadas relativas al directorio del script
    ruta_imagenes_default = os.path.join(script_dir, "originals")
    ruta_csv_default = os.path.join(script_dir, "quotes.csv")
    ruta_salida_default = os.path.join(script_dir, "banners")
    ruta_fuentes_default = os.path.join(script_dir, "fonts")
    nombre_fuente_default = "Montserrat-Bold.ttf"

    # Solicitar rutas al usuario con valores predeterminados
    ruta_imagenes = input(f'Ingrese la ubicación del directorio donde se encuentran las imágenes (por defecto "{ruta_imagenes_default}"): ') or ruta_imagenes_default
    ruta_csv = input(f'Ingrese la ubicación completa del archivo CSV con las citas (por defecto "{ruta_csv_default}"): ') or ruta_csv_default
    ruta_salida = input(f'Ingrese la ubicación del directorio donde se guardarán las imágenes banners (por defecto "{ruta_salida_default}"): ') or ruta_salida_default
    ruta_fuentes = input(f'Ingrese la ubicación del directorio donde se encuentran las fuentes (por defecto "{ruta_fuentes_default}"): ') or ruta_fuentes_default
    nombre_fuente = input(f'Ingrese el nombre del archivo de fuente a utilizar (por defecto "{nombre_fuente_default}"): ') or nombre_fuente_default

    # Preguntar por el tipo de comillas tipográficas
    tipo_comillas_opciones = {
        "1": {"nombre": "angulares", "abrir": "«", "cerrar": "»"},
        "2": {"nombre": "altas", "abrir": "“", "cerrar": "”"},
        "3": {"nombre": "simples", "abrir": "‘", "cerrar": "’"},
        "4": {"nombre": "ninguna", "abrir": "", "cerrar": ""}
    }
    print("\nSeleccione el tipo de comillas tipográficas para la cita:")
    for key, opcion in tipo_comillas_opciones.items():
        print(f"{key}. {opcion['nombre'].capitalize()} ({opcion['abrir']}{opcion['cerrar']})")

    seleccion_comillas = input(f'Ingrese el número de opción (por defecto 1 - angulares): ') or "1"

    comillas_seleccionadas = tipo_comillas_opciones.get(seleccion_comillas, tipo_comillas_opciones["1"]) # Por defecto angulares

    # Crear directorios si no existen
    os.makedirs(ruta_imagenes, exist_ok=True)
    os.makedirs(ruta_salida, exist_ok=True)
    os.makedirs(ruta_fuentes, exist_ok=True)

    # Leer citas del archivo CSV
    citas = []
    try:
        with open(ruta_csv, newline='', encoding='utf-8') as archivo_csv:
            lector = csv.reader(archivo_csv)
            next(lector, None) # Saltar la primera fila (encabezados) si existe
            for fila in lector:
                if len(fila) < 4:
                    continue
                cita = fila[0].strip()
                autor = fila[1].strip().replace('"','')
                libro = fila[2].strip().replace('"','')
                twitter = fila[3].strip().replace('"','')
                citas.append({
                    'cita': cita,
                    'autor': autor,
                    'libro': libro,
                    'twitter': twitter
                })
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV en la ruta {ruta_csv}")
        exit(1)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        exit(1)

    # Obtener lista de imágenes en el directorio especificado
    try:
        lista_imagenes = [os.path.join(ruta_imagenes, archivo) for archivo in os.listdir(ruta_imagenes)
                         if archivo.lower().endswith(('.jpg', '.jpeg', '.png'))]
    except FileNotFoundError:
        print(f"Error: No se encontró el directorio de imágenes en la ruta {ruta_imagenes}")
        exit(1)
    except Exception as e:
        print(f"Error al listar las imágenes: {e}")
        exit(1)

    indice_imagen = 0
    total_imagenes = len(lista_imagenes)

    if total_imagenes == 0:
        print(f"Error: No hay imágenes disponibles en {ruta_imagenes}")
        exit(1)

    print(f"Procesando {len(citas)} citas con {total_imagenes} imágenes...")

    for i, elemento in enumerate(citas):
        if total_imagenes == 0:
            break
        ruta_imagen_actual = lista_imagenes[indice_imagen]
        indice_imagen = (indice_imagen + 1) % total_imagenes

        try:
            imagen_banner = Image.open(ruta_imagen_actual).convert("RGB")

            # Definición de la caja para la cita con dimensiones exactas
            caja_x = 90
            caja_y = 90
            caja_ancho = 1080 - 90 - 90   # 900 píxeles de ancho
            caja_alto = 800 - 90          # 710 píxeles de alto

            cita_texto = elemento['cita'].strip()
            cita_texto_con_comillas = f"{comillas_seleccionadas['abrir']}{cita_texto}{comillas_seleccionadas['cerrar']}"


            imagen_cita = crear_imagen_con_texto(
                texto=cita_texto_con_comillas,
                ancho=caja_ancho,
                alto=caja_alto,
                ruta_fuente=ruta_fuentes,
                nombre_fuente=nombre_fuente,
                color_texto=(255, 255, 255),
                color_fondo=None,
                tamano_fuente_max=116,
                tamano_fuente_min=11
            )

            imagen_banner.paste(imagen_cita, (caja_x, caja_y), imagen_cita)

            draw = ImageDraw.Draw(imagen_banner)
            fuente_libro = ImageFont.truetype(os.path.join(ruta_fuentes, nombre_fuente), 50)
            texto_libro = elemento['libro']
            ancho_texto_libro = fuente_libro.getlength(texto_libro)
            x_libro = (1080 - ancho_texto_libro) // 2
            draw.text((x_libro, 836), texto_libro, font=fuente_libro, fill=(255, 255, 255))

            fuente_autor = ImageFont.truetype(os.path.join(ruta_fuentes, nombre_fuente), 35)
            texto_autor = elemento['autor']
            ancho_texto_autor = fuente_autor.getlength(texto_autor)
            x_autor = (1080 - ancho_texto_autor) // 2
            draw.text((x_autor, 902), texto_autor, font=fuente_autor, fill=(255, 255, 255))

            fuente_twitter = ImageFont.truetype(os.path.join(ruta_fuentes, nombre_fuente), 35)
            texto_twitter = elemento['twitter']
            ancho_texto_twitter = fuente_twitter.getlength(texto_twitter)
            x_twitter = (1080 - ancho_texto_twitter) // 2
            draw.text((x_twitter, 958), texto_twitter, font=fuente_twitter, fill=(255, 255, 255))

            nombre_archivo = f"banner_{i+1}.jpg"
            ruta_guardado = os.path.join(ruta_salida, nombre_archivo)
            imagen_banner.save(ruta_guardado, quality=95)

            print(f"Generada imagen {i+1}/{len(citas)}: {nombre_archivo}")

        except Exception as e:
            print(f"Error al procesar la imagen {i+1}: {e}")

    print(f"Proceso completado. Se generaron {min(len(citas), total_imagenes)} banners en {ruta_salida}")