import os
import pdfplumber
import xmltodict

def procesar_pdf(ruta_archivo):
    """Extrae el texto de un archivo PDF utilizando pdfplumber."""
    texto_extraido = ""
    try:
        # Abrimos el PDF
        with pdfplumber.open(ruta_archivo) as pdf:
            # Recorremos todas las páginas y extraemos el texto
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
        return texto_extraido
    except Exception as e:
        return f"Error al leer PDF: {e}"

def procesar_xml(ruta_archivo):
    """Lee un archivo XML y lo convierte en un diccionario de Python."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            # xmltodict convierte el texto XML crudo en un diccionario estructurado
            diccionario_xml = xmltodict.parse(archivo.read())
            return diccionario_xml
    except Exception as e:
        return f"Error al leer XML: {e}"

def leer_facturas(carpeta_facturas):
    """Recorre la carpeta de facturas y procesa cada archivo según su formato."""
    print(f"--- Iniciando SIRA: Módulo de Ingestión en '{carpeta_facturas}' ---\n")

    if not os.path.exists(carpeta_facturas):
        print(f"Error: La carpeta '{carpeta_facturas}' no existe.")
        return

    # Obtenemos la lista de archivos en la carpeta
    archivos = os.listdir(carpeta_facturas)

    if not archivos:
        print("La carpeta está vacía. ¡Agrega facturas de prueba!")
        return

    for archivo in archivos:
        ruta_completa = os.path.join(carpeta_facturas, archivo)

        # Si es un PDF
        if archivo.lower().endswith('.pdf'):
            print(f"📄 Procesando PDF: {archivo}")
            texto = procesar_pdf(ruta_completa)
            # Imprimimos un resumen (los primeros 200 caracteres) para verificar que leyó algo
            print(f"   Contenido extraído (resumen): {texto[:200]}...\n")

        # Si es un XML
        elif archivo.lower().endswith('.xml'):
            print(f"🧾 Procesando XML: {archivo}")
            datos = procesar_xml(ruta_completa)
            print("   XML leído con éxito y convertido a estructura de datos.\n")

        else:
            print(f"⚠️ Formato no soportado, se ignorará: {archivo}\n")

# Punto de entrada del script
if __name__ == "__main__":
    carpeta_prueba = "facturas_prueba"
    leer_facturas(carpeta_prueba)