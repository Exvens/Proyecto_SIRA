import json
import os

def exportar_para_rpa(datos_procesados, nombre_archivo="lote_contabilizacion_rpa.json"):
    """
    Toma la lista de facturas procesadas y genera un archivo JSON
    estructurado, ideal para ser consumido por un RPA o una API.
    """
    if not datos_procesados:
        print("⚠️ No hay datos válidos para exportar al RPA.")
        return

    print(f"\n💾 Generando archivo JSON para el RPA: '{nombre_archivo}'...")
    
    try:
        # Guardamos la lista de diccionarios en formato JSON con sangría para que sea legible
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo_json:
            json.dump(datos_procesados, archivo_json, indent=4, ensure_ascii=False)
        
        ruta_absoluta = os.path.abspath(nombre_archivo)
        print(f"   ✅ Archivo JSON generado con éxito.")
        print(f"      Ubicación: {ruta_absoluta}")
    except Exception as e:
        print(f"   ❌ Error al generar el JSON: {e}")