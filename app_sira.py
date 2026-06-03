import streamlit as st
import pdfplumber
import pandas as pd
import json
import os
import csv
import re
import xml.etree.ElementTree as ET

# Importamos las mentes de SIRA
from validador_dian import validar_factura_fisica
from modelo_ia import inicializar_modelo, predecir_cuenta_contable, obtener_cuentas_desde_puc

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="SIRA - IA Contable", page_icon="🤖", layout="wide")

@st.cache_resource
def cargar_cerebro_ia():
    return inicializar_modelo()

st.title("🤖 SIRA: Sistema Inteligente de Reportes y Auditoría")
modelo_sira = cargar_cerebro_ia()

def extraer_conceptos_pdf(texto_pdf):
    """
    MÁQUINA DE ESTADOS: Lee línea por línea para evitar la trampa
    de las palabras "Subtotal" en la misma cabecera de la tabla.
    """
    lineas = texto_pdf.split('\n')
    conceptos_crudos = []
    en_tabla = False
    
    for linea in lineas:
        linea_low = linea.lower()
        
        # 1. Encender la máquina al ver la cabecera de artículos
        if "descripción" in linea_low or "descripcion" in linea_low or "artículo" in linea_low:
            en_tabla = True
            continue # Saltamos esta línea para no tropezar con la palabra 'subtotal' de la cabecera
            
        if en_tabla:
            # 2. Apagar la máquina al llegar a la fila de los totales de abajo
            if "subtotal:" in linea_low or "total neto" in linea_low or "iva " in linea_low or "observaciones" in linea_low or "son:" in linea_low:
                break
            
            # 3. Guardar el contenido puro de la tabla
            if linea.strip():
                conceptos_crudos.append(linea.strip())
                
    # Si la factura tiene un diseño rarísimo y no halló tabla, toma un pedazo inicial
    if not conceptos_crudos:
        return texto_pdf[:150]
        
    return " ".join(conceptos_crudos)

def limpiar_concepto_para_ia(texto_sucio):
    """
    Elimina los números y basura de la tabla (Cantidades y Precios).
    """
    if not texto_sucio: 
        return ""
    texto = str(texto_sucio).lower()
    
    # Eliminar valores monetarios ($ 8.264.400)
    texto = re.sub(r'\$\s*[\d\.,]+', ' ', texto)
    # Eliminar cantidades y porcentajes aislados (12, 35, 19%)
    texto = re.sub(r'\b\d+[\d\.,]*%?\b', ' ', texto)
    
    # Eliminar palabras residuales de las cabeceras
    ruidos = ["subtotal", "total", "iva", "cant.", "cant", "v. unitario", "v unitario", "item"]
    for r in ruidos:
        texto = re.sub(r'\b' + r + r'\b', ' ', texto)
        
    # Limpiar caracteres especiales y normalizar
    texto = re.sub(r'[^\w\sáéíóúñ]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def procesar_xml_nativo(xml_bytes):
    """
    Perfora el XML y busca estrictamente las etiquetas <Item>
    para no confundirse con las firmas digitales de la DIAN.
    """
    xml_texto = xml_bytes.decode("utf-8", errors="ignore")
    
    # Extraer el Invoice real si viene encriptado en un AttachedDocument
    if "<AttachedDocument" in xml_texto and "<![CDATA[" in xml_texto:
        match_cdata = re.search(r'<!\[CDATA\[(.*?)\]\]>', xml_texto, re.DOTALL)
        if match_cdata:
            xml_texto = match_cdata.group(1).strip()

    faltantes = []
    
    try:
        root = ET.fromstring(xml_texto)
    except Exception as e:
        return False, [f"Estructura XML corrupta: {str(e)}"], ""
        
    # Quitar namespaces para hacer la búsqueda limpia
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}')[-1]

    # Validaciones obligatorias de la DIAN
    id_nodo = root.find('.//ID')
    if id_nodo is None or not id_nodo.text: faltantes.append("Número de Factura")
        
    fecha_nodo = root.find('.//IssueDate')
    if fecha_nodo is None or not fecha_nodo.text: faltantes.append("Fecha de Emisión")
        
    supplier = root.find('.//AccountingSupplierParty')
    if supplier is None or supplier.find('.//CompanyID') is None: faltantes.append("NIT Vendedor")
        
    customer = root.find('.//AccountingCustomerParty')
    if customer is None or customer.find('.//CompanyID') is None: faltantes.append("NIT Adquirente")
        
    es_valido = (len(faltantes) == 0)

    # 🚀 EXTRACCIÓN ESTRICTA: Solo busca descripciones DENTRO de los "Items" reales
    descripciones = []
    for item in root.findall('.//Item'):
        desc = item.find('.//Description')
        if desc is not None and desc.text:
            descripciones.append(desc.text.strip())
        else:
            name = item.find('.//Name')
            if name is not None and name.text:
                descripciones.append(name.text.strip())
                
    concepto_detectado = " | ".join(descripciones) if descripciones else ""
    return es_valido, faltantes, concepto_detectado


# ==============================================================================
# 🗂️ CONTROL DE PESTAÑAS Y MEMORIA VOLÁTIL DE SIRA
# ==============================================================================
tab_operacion, tab_entrenamiento = st.tabs(["📊 Operación Diaria", "🧠 Entrenamiento y Aprendizaje"])

# Inicializamos la memoria de la sesión para que Streamlit recuerde las facturas procesadas
if "lote_procesado" not in st.session_state:
    st.session_state.lote_procesado = []

# ==========================================
# PESTAÑA 1: OPERACIÓN Y FEEDBACK HUMANO
# ==========================================
with tab_operacion:
    st.markdown("Auditoría automatizada de archivos **PDF** y contenedores **XML** de la DIAN.")
    
    archivos_subidos = st.file_uploader("Arrastra aquí tus facturas", type=["pdf", "xml"], accept_multiple_files=True)
    
    if st.button("🚀 Procesar Facturas con IA", type="primary"):
        if not archivos_subidos:
            st.warning("⚠️ Sube al menos una factura.")
        else:
            lote_temporal = []
            barra_progreso = st.progress(0)
            
            for i, archivo in enumerate(archivos_subidos):
                concepto_real = ""
                es_valida = False
                faltantes = []
                nombre_ext = os.path.splitext(archivo.name)[1].lower()
                
                # --- PROCESAMIENTO XML ---
                if nombre_ext == ".xml":
                    xml_bytes = archivo.read()
                    es_valida, faltantes, concepto_xml = procesar_xml_nativo(xml_bytes)
                    concepto_real = limpiar_concepto_para_ia(concepto_xml)
                
                # --- PROCESAMIENTO PDF ---
                else:
                    texto_pdf = ""
                    with pdfplumber.open(archivo) as pdf:
                        for pagina in pdf.pages:
                            txt = pagina.extract_text()
                            if txt: texto_pdf += txt + "\n"
                    
                    # Normalización de sinónimos de fecha antes del validador de la DIAN
                    import re
                    texto_normalizado_fecha = re.sub(r'fecha\s+de\s+expedición|expedición', 'Fecha de Emisión', texto_pdf, flags=re.IGNORECASE)
                    
                    es_valida, faltantes = validar_factura_fisica(texto_normalizado_fecha)
                    
                    # Extraer mediante Máquina de Estados y limpiar números
                    bloque_tabla = extraer_conceptos_pdf(texto_pdf)
                    concepto_real = limpiar_concepto_para_ia(bloque_tabla)
                
                # --- CLASIFICACIÓN CON IA ---
                if es_valida:
                    if not concepto_real or len(concepto_real) < 3:
                        concepto_real = "compra de mercancia o servicio general"
                        
                    cuenta, confianza = predecir_cuenta_contable(modelo_sira, concepto_real)
                    
                    import math
                    if math.isnan(confianza):
                        confianza_print = "0.00%"
                    else:
                        confianza_print = f"{confianza:.2f}%"
                        
                    lote_temporal.append({
                        "Archivo": archivo.name,
                        "Concepto Real": concepto_real,  # Texto completo para el panel inferior
                        "Concepto": concepto_real[:80] + "..." if len(concepto_real) > 80 else concepto_real,
                        "Cuenta IA": cuenta,
                        "Confianza": confianza_print
                    })
                else:
                    motivo = ", ".join(faltantes) if faltantes else "Estructura inválida"
                    lote_temporal.append({
                        "Archivo": archivo.name,
                        "Concepto Real": f"RECHAZADO: Falta {motivo}",
                        "Concepto": f"❌ RECHAZADO: Falta {motivo}",
                        "Cuenta IA": "Bloqueado",
                        "Confianza": "N/A"
                    })
                
                barra_progreso.progress((i + 1) / len(archivos_subidos))
            
            # Guardamos el lote en memoria y forzamos recarga limpia de la interfaz (Soporta versiones viejas y nuevas)
            st.session_state.lote_procesado = lote_temporal
            st.success("✅ Procesamiento completado.")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

    # --- DESPLEGAR TABLA DE RESULTADOS REALES ---
    if st.session_state.lote_procesado:
        st.dataframe(pd.DataFrame(st.session_state.lote_procesado)[["Archivo", "Concepto", "Cuenta IA", "Confianza"]], use_container_width=True)

    st.divider()
    
    # --- SECCIÓN DE AUDITORÍA Y CORRECCIÓN INTERACTIVA ---
    st.subheader("✍️ Corregir a la IA (Añadir al historial)")
    
    # Filtramos para interactuar únicamente con las facturas válidas
    facturas_validas = [f for f in st.session_state.lote_procesado if f["Cuenta IA"] != "Bloqueado"]
    
    if not facturas_validas:
        st.info("💡 Sube y procesa facturas válidas arriba para que aparezcan en el panel de corrección automática.")
    else:
        # Selector desplegable dinámico amarrado a los resultados de la tabla superior
        opciones_selector = [f"{f['Archivo']} -> ({f['Concepto']})" for f in facturas_validas]
        seleccion = st.selectbox("🎯 Selecciona la factura que deseas corregir o registrar en el historial:", opciones_selector)
        
        # Recuperamos la información exacta de la factura elegida en el menú
        indice_seleccionado = opciones_selector.index(seleccion)
        factura_elegida = facturas_validas[indice_seleccionado]
        
        col1, col2 = st.columns(2)
        with col1: 
            # El concepto se autorellena mágicamente con el texto real extraído de la factura seleccionada
            concepto_corregido = st.text_input("Concepto extraído automáticamente (puedes editarlo si deseas):", value=factura_elegida["Concepto Real"])
        with col2: 
            cuenta_correcta = st.selectbox("Selecciona la cuenta correcta para este concepto", obtener_cuentas_desde_puc())
        
        if st.button("💾 Guardar Corrección y Aprender"):
            if concepto_corregido:
                codigo_cuenta = cuenta_correcta.split("Cuenta ")[-1].replace(")", "").strip()
                existe = os.path.exists("datos_entrenamiento.csv")
                with open("datos_entrenamiento.csv", 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not existe: writer.writerow(['texto', 'etiqueta'])
                    writer.writerow([concepto_corregido, codigo_cuenta])
                st.success(f"✅ ¡Guardado con éxito! SIRA ha aprendido que '{concepto_corregido}' pertenece a la cuenta {codigo_cuenta}.")
            else:
                st.error("❌ El concepto no puede estar vacío.")

# ==========================================
# PESTAÑA 2: CARGA MASIVA (HISTÓRICO CSV)
# ==========================================
with tab_entrenamiento:
    st.header("⚙️ Panel de Entrenamiento")
    archivo_csv = st.file_uploader("Sube tu archivo CSV histórico", type=["csv"])
    if archivo_csv:
        if st.button("📥 Reemplazar base de datos"):
            with open("datos_entrenamiento.csv", "wb") as f:
                f.write(archivo_csv.getbuffer())
            st.success("✅ Archivo cargado.")