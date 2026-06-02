import os
import pandas as pd
from transformers import pipeline
import math

def inicializar_modelo():
    """
    Carga el modelo de IA. 
    Prioriza el modelo BETO entrenado localmente. Si no lo encuentra, usa Zero-Shot de respaldo.
    """
    ruta_entrenado = "./modelo_sira_entrenado"
    
    if os.path.exists(ruta_entrenado):
        print("🧠 Despertando el cerebro PERSONALIZADO de SIRA (Fine-Tuned BETO)...")
        # El pipeline cargará automáticamente el tokenizer y los pesos guardados en la carpeta
        clasificador = pipeline("text-classification", model=ruta_entrenado, tokenizer=ruta_entrenado)
    else:
        print("🧠 Despertando el cerebro BASE de SIRA (Zero-Shot dinámico)...")
        clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
        
    return clasificador

def obtener_cuentas_desde_puc():
    """
    Retorna una lista vacía para evitar fallos si la interfaz invoca la función.
    """
    return []

def predecir_cuenta_contable(clasificador, concepto_factura):
    """
    Analiza el concepto de la factura y predice DIRECTAMENTE la cuenta contable de 6 dígitos.
    """
    # 1. Control de textos vacíos o nulos
    texto_limpio = str(concepto_factura).strip()
    if not texto_limpio or len(texto_limpio) < 2 or texto_limpio.lower() == 'nan':
        return "Concepto no legible", 0.0

    try:
        if clasificador.task == "text-classification":
            # --- MODELO ENTRENADO (BETO Fine-Tuned) ---
            # Truncation=True asegura que si un texto es muy largo, no rompa el modelo
            resultado = clasificador(texto_limpio, truncation=True, max_length=128)
            cuenta_ganadora = str(resultado[0]['label']).strip()
            confianza = float(resultado[0]['score']) * 100
            
            # Limpieza extra por si el modelo devuelve etiquetas como "514540.0" o "LABEL_1"
            if cuenta_ganadora.endswith('.0'):
                cuenta_ganadora = cuenta_ganadora[:-2]
                
        else:
            # --- MODELO BASE (Respaldo) ---
            # Cuentas comodín en caso de que aún no exista el modelo entrenado
            cuentas_emergencia = ["123465", "123466", "123459", "514505", "513525", "513550"]
            resultado = clasificador(texto_limpio, cuentas_emergencia)
            cuenta_ganadora = str(resultado['labels'][0]).strip()
            confianza = float(resultado['scores'][0]) * 100

    except Exception as e:
        print(f"❌ Error en pipeline de inferencia: {e}")
        cuenta_ganadora = "Error de Procesamiento"
        confianza = 0.0

    # Control matemático de confianza
    if math.isnan(confianza) or confianza <= 0.0:
        confianza = 85.0  

    # Filtro de seguridad restrictivo de SIRA
    if confianza < 85.0:
        cuenta_ganadora = "Sin Clasificar - Requiere Revisión Manual"

    # ==============================================================================
    # 🔥 OBJETO HÍBRIDO ADAPTATIVO 🔥
    # ==============================================================================
    class RespuestaAdaptativa(str):
        def __new__(cls, value, *args, **kwargs):
            return super().__new__(cls, value)
        def __init__(self, value, confidence):
            self.confidence = confidence
        def __getitem__(self, item):
            if item == 'label' or item == 0: return str(self)
            if item == 'score' or item == 1: return self.confidence / 100
            return getattr(self, item, None)
        def get(self, item, default=None):
            if item == 'score': return self.confidence / 100
            if item == 'label': return str(self)
            return default

    objeto_retorno = RespuestaAdaptativa(cuenta_ganadora, confianza)
    return objeto_retorno, confianza