import os
import pandas as pd
from transformers import pipeline

def inicializar_modelo():
    """
    Carga el clasificador Zero-Shot oficial de mDeBERTa directo de internet
    para asegurar que use sus archivos limpios y no una copia corrupta.
    """
    print("🧠 Forzando descarga limpia de mDeBERTa-v3 desde Hugging Face...")
    # Forzamos la carga del modelo base oficial
    clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    return clasificador

def obtener_cuentas_desde_puc():
    """Retorna las cuentas estandarizadas para el menú de Streamlit"""
    return [
        "Mantenimiento y Reparaciones (Cuenta 514505)",
        "Retención Servicios (Cuenta 236530)",
        "Servicios Públicos / Energía EPM (Cuenta 513525)",
        "Retención Compras (Cuenta 236540)",
        "Combustibles y Peajes (Cuenta 513550)",
        "Papelería y Útiles (Cuenta 519525)",
        "Seguros y Pólizas (Cuenta 123463)",
        "RUNT y Tránsito (Cuenta 123464)",
        "Ferromax Estructuras (Cuenta 123456)",
        "Herramientas y Ferretería (Cuenta 123457)"
    ]

def predecir_cuenta_contable(clasificador, concepto_factura):
    """
    Predice la cuenta contable. Primero busca coincidencia exacta en el CSV.
    Si no existe, obliga a la IA a votar entre las categorías reales.
    """
    texto_limpio = str(concepto_factura).strip().lower()
    if not texto_limpio or len(texto_limpio) < 2:
        return "Concepto no legible", 0.0

    ruta_csv = "datos_entrenamiento.csv"

    # 🔥 1. REVISIÓN PRIORITARIA DEL HISTORIAL (Manda el usuario)
    if os.path.exists(ruta_csv):
        try:
            df_historial = pd.read_csv(ruta_csv)
            if not df_historial.empty and 'texto' in df_historial.columns and 'etiqueta' in df_historial.columns:
                df_historial['texto_clean'] = df_historial['texto'].astype(str).str.strip().str.lower()
                
                # Buscamos si el concepto ya fue corregido por ti
                coincidencia = df_historial[df_historial['texto_clean'] == texto_limpio]
                if not coincidencia.empty:
                    cuenta_ganadora = str(coincidencia.iloc[-1]['etiqueta']).strip()
                    if cuenta_ganadora.endswith('.0'): cuenta_ganadora = cuenta_ganadora[:-2]
                    return construir_respuesta_adaptativa(cuenta_ganadora, 100.0), 100.0
        except Exception as e:
            print(f"⚠️ Error en historial: {e}")

    # 🧠 2. PREDICCIÓN LOGICA DE IA (Si el concepto es nuevo)
    try:
        # Forzamos los nombres de las categorías comerciales reales que la IA sí entiende
        categorias_comerciales = [
            "mantenimiento, reparaciones e infraestructura de planta",
            "retencion en la fuente por servicios medicos o tecnicos",
            "servicios publicos, energia electrica, agua, luz y acueducto epm",
            "retencion en la fuente por compras e insumos comerciales",
            "combustibles, gasolina, acpm, peajes nacionales y transporte",
            "utiles de escritorio, papeleria, fotocopias y oficina",
            "seguros, polizas de vida e iva estatal",
            "tramites de transito, runt vehicular y transporte de carga",
            "hierro, perfiles, vigas, tejas y estructuras metalicas ferromax",
            "herramientas, tornillos, arena, cemento, palas y ferreteria"
        ]
        
        mapa_codigos = {
            "mantenimiento, reparaciones e infraestructura de planta": "514505",
            "retencion en la fuente por servicios medicos o tecnicos": "236530",
            "servicios publicos, energia electrica, agua, luz y acueducto epm": "513525",
            "retencion en la fuente por compras e insumos comerciales": "236540",
            "combustibles, gasolina, acpm, peajes nacionales y transporte": "513550",
            "utiles de escritorio, papeleria, fotocopias y oficina": "519525",
            "seguros, polizas de vida e iva estatal": "123463",
            "tramites de transito, runt vehicular y transporte de carga": "123464",
            "hierro, perfiles, vigas, tejas y estructuras metalicas ferromax": "123456",
            "herramientas, tornillos, arena, cemento, palas y ferreteria": "123457"
        }

        # La IA ejecuta la votación conceptual
        resultado = clasificador(texto_limpio, candidate_labels=categorias_comerciales)
        
        categoria_ganadora = resultado['labels'][0]
        confianza = float(resultado['scores'][0]) * 100
        cuenta_ganadora = mapa_codigos[categoria_ganadora]

    except Exception as e:
        print(f"❌ Error en IA: {e}")
        cuenta_ganadora = "Error"
        confianza = 0.0

    if confianza < 35.0:
        cuenta_ganadora = "Sin Clasificar - Requiere Revisión Manual"

    return construir_respuesta_adaptativa(cuenta_ganadora, confianza), confianza

def construir_respuesta_adaptativa(cuenta, confianza):
    class RespuestaAdaptativa(str):
        def __new__(cls, value, *args, **kwargs): return super().__new__(cls, value)
        def __init__(self, value, confidence): self.confidence = confidence
        def __getitem__(self, item):
            if item == 'label' or item == 0: return str(self)
            if item == 'score' or item == 1: return self.confidence / 100
            return getattr(self, item, None)
        def get(self, item, default=None):
            if item == 'score': return self.confidence / 100
            if item == 'label': return str(self)
            return default
    return RespuestaAdaptativa(cuenta, confianza)