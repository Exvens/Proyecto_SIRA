import os
import pdfplumber
import xmltodict
from validador_dian import validar_factura_fisica
from modelo_ia import inicializar_modelo, predecir_cuenta_contable
from exportador_rpa import exportar_para_rpa 

def procesar_pdf(ruta_archivo):
    texto_extraido = ""
    try:
        with pdfplumber.open(ruta_archivo) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
        return texto_extraido
    except Exception as e:
        return f"Error al leer PDF: {e}"

def procesar_xml(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            return xmltodict.parse(archivo.read())
    except Exception as e:
        return f"Error al leer XML: {e}"

def leer_facturas(carpeta_facturas, clasificador_ia):
    print(f"--- Iniciando SIRA: Módulo Central (Modo JSON) en '{carpeta_facturas}' ---\n")
    if not os.path.exists(carpeta_facturas):
        print(f"Error: La carpeta '{carpeta_facturas}' no existe.")
        return

    archivos = os.listdir(carpeta_facturas)
    if not archivos:
        print("La carpeta está vacía.")
        return

    # Lista que contendrá los objetos JSON
    lote_para_rpa = []

    for archivo in archivos:
        ruta_completa = os.path.join(carpeta_facturas, archivo)

        if archivo.lower().endswith('.pdf'):
            print(f"📄 Procesando PDF: {archivo}")
            texto = procesar_pdf(ruta_completa)
            
            print("   🛡️  Ejecutando Auditoría DIAN...")
            es_valida, faltantes = validar_factura_fisica(texto)
            
            if es_valida:
                print("   ✅ Factura APROBADA.")
                concepto_prueba = "Compra de cemento, varillas y herramientas manuales"
                print(f"   🧠 Analizando IA: '{concepto_prueba}'")
                
                cuenta, confianza = predecir_cuenta_contable(clasificador_ia, concepto_prueba)
                
                # Estructura JSON para factura aprobada
                lote_para_rpa.append({
                    "id_archivo": archivo,
                    "metadata": {
                        "formato": "PDF",
                        "estado": "APROBADO_DIAN"
                    },
                    "analisis_contable": {
                        "concepto": concepto_prueba,
                        "cuenta_sugerida": cuenta,
                        "score_confianza": round(confianza / 100, 4)
                    }
                })
                
            else:
                print(f"   ❌ Factura RECHAZADA.")
                # Estructura JSON para factura rechazada
                lote_para_rpa.append({
                    "id_archivo": archivo,
                    "metadata": {
                        "formato": "PDF",
                        "estado": "RECHAZADO_DIAN"
                    },
                    "errores_encontrados": faltantes
                })
            print("-" * 50)

    # Exportamos el lote final a JSON
    exportar_para_rpa(lote_para_rpa)

if __name__ == "__main__":
    carpeta_prueba = "facturas_prueba"
    modelo_sira = inicializar_modelo()
    print("✅ IA Cargada.\n")
    leer_facturas(carpeta_prueba, modelo_sira)