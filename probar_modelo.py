import os
import math
from modelo_ia import inicializar_modelo, predecir_cuenta_contable

def verificar_sistema():
    print("🤖 === DIAGNÓSTICO DEL MODELO SIRA ===")
    
    # 1. Validar existencia de la carpeta entrenada
    ruta_modelo = "modelo_sira_trained" 
    # NOTA: Cambia "modelo_sira_trained" por "modelo_sira_entrenado" si esa es la ruta que inicializa tu script
    
    print(f"Checking folders...")
    if os.path.exists("modelo_sira_entrenado"):
        print("✅ Carpeta 'modelo_sira_entrenado' detectada.")
    else:
        print("⚠️ No se ve la carpeta por defecto 'modelo_sira_entrenado' en la raíz.")

    try:
        print("\n🧠 Cargando el cerebro de la IA...")
        modelo = inicializar_modelo()
        print("✅ Modelo cargado en memoria exitosamente.")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO al cargar el modelo: {e}")
        return

    # 2. Realizar pruebas de predicción con conceptos variados
    conceptos_prueba = [
        "FERRETERÍA ANTIOQUEÑA LTDA. Compra de cemento gris, varillas de alta resistencia y herramientas manuales para construcción",
        "Pinturas y Acabados Aburrá S.A.S. Servicio de mantenimiento locativo de oficinas y pintura de fachadas",
        "Compra de papelería, resmas de papel bond, esferos y clips para el área de administración"
    ]

    print("\n🚀 Ejecutando lote de prueba en consola:")
    for i, concepto in enumerate(conceptos_prueba, 1):
        try:
            cuenta, confianza = predecir_cuenta_contable(modelo, concepto)
            
            # Validamos si la confianza es un NaN real matemáticamente
            es_nan = False
            if isinstance(confianza, float) and math.isnan(confianza):
                es_nan = True
            
            print(f"\nPrueba #{i}:")
            print(f"  Texto enviado: '{concepto[:80]}...'")
            print(f"  Cuenta asignada por IA: {cuenta}")
            
            if es_nan:
                print(f"  Confianza: ❌ valor NaN detectado (Error de cálculo matemático en el modelo).")
            else:
                print(f"  Confianza:  {confianza}%")
                
        except Exception as e:
            print(f"  ❌ Error al predecir en la Prueba #{i}: {e}")

if __name__ == "__main__":
    verificar_sistema()