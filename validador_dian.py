import re

def validar_factura_fisica(texto_factura):
    """
    Verifica que el texto de la factura contenga los requisitos mínimos
    exigidos por la DIAN (Art. 617 del Estatuto Tributario).
    """
    # Patrones de búsqueda (Expresiones regulares)
    requisitos = {
        "NIT del Vendedor": r"NIT[:\s]+[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]",
        "Denominación Expresa (Factura Electrónica)": r"FACTURA ELECTR[OÓ]NICA",
        "Fecha de Emisión": r"FECHA DE EMISI[OÓ]N",
        "Datos del Adquirente": r"ADQUIRENTE|CLIENTE"
    }

    faltantes = []
    # Convertimos todo a mayúsculas para que la búsqueda no falle por minúsculas
    texto_upper = texto_factura.upper()

    for requisito, patron in requisitos.items():
        # Buscamos el patrón en el texto
        if not re.search(patron, texto_upper):
            faltantes.append(requisito)

    # Es válida si la lista de faltantes está vacía (0 elementos)
    es_valida = len(faltantes) == 0
    return es_valida, faltantes