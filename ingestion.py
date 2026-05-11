import os
import pdfplumber
import xmltodict
from validador_dian import validar_factura_fisica
from modelo_ia import inicializar_modelo, predecir_cuenta_contable

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

def leer_facturas(carpeta_facturas, clasificador_ia):
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
            
            # --- FILTRO DIAN ---
            print("   🛡️  Ejecutando Auditoría DIAN...")
            es_valida, faltantes = validar_factura_fisica(texto)
            
            if es_valida:
                print("   ✅ Factura APROBADA por la DIAN.")
                
                # --- NUEVO: CEREBRO IA ---
                # Para la prueba, simularemos que extrajimos un concepto de la factura
                concepto_prueba = "Compra de cemento, varillas y herramientas manuales"
                print(f"   🧠 Analizando concepto con IA: '{concepto_prueba}'")
                
                cuenta, confianza = predecir_cuenta_contable(clasificador_ia, concepto_prueba)
                
                print(f"   📊 Imputación Contable: {cuenta} (Seguridad: {confianza:.2f}%)")
                
            else:
                print(f"   ❌ Factura RECHAZADA. Incumple ley colombiana.")
                print(f"      Faltan los siguientes requisitos: {faltantes}")
            print("-" * 50 + "\n")

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
    
    # Encendemos la IA antes de leer facturas
    modelo_sira = inicializar_modelo()
    print("✅ IA Cargada y lista.\n")
    
    # Le pasamos el modelo a la función
    leer_facturas(carpeta_prueba, modelo_sira)