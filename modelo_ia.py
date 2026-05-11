from transformers import pipeline

def inicializar_modelo():
    """Carga el modelo de IA basado en la arquitectura Transformer (BERT/BETO)."""
    print("🧠 Despertando el cerebro de SIRA (Descargando/Cargando modelo IA)...")
    print("   (Esto puede tardar un par de minutos la primera vez mientras descarga el modelo)")
    
    # Usamos un pipeline zero-shot optimizado para múltiples idiomas, incluyendo español.
    # En la fase final, aquí se conectará tu modelo BETO fine-tuneado.
    clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    return clasificador

def predecir_cuenta_contable(clasificador, concepto_factura):
    """Analiza el concepto de la factura y decide a qué cuenta contable pertenece."""
    
    # Estas son las categorías que la IA intentará predecir
    cuentas_candidatas = [
        "Mantenimiento de Servidores y Equipos de Computo (Cuenta 5145)",
        "Compra de Papelería y Útiles de Oficina (Cuenta 5195)",
        "Honorarios Profesionales y Asesorías (Cuenta 5110)",
        "Compra de Materiales de Construcción y Ferretería (Cuenta 1435)"
    ]
    
    # SIRA analiza el texto contra las opciones
    resultado = clasificador(concepto_factura, cuentas_candidatas)
    
    # Obtenemos la cuenta ganadora y su porcentaje de seguridad (confianza)
    cuenta_ganadora = resultado['labels'][0]
    confianza = resultado['scores'][0] * 100
    
    return cuenta_ganadora, confianza