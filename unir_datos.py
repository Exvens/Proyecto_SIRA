import pandas as pd
import os

def preparar_datos_entrenamiento():
    print("🔄 Iniciando cruce de datos definitivo...")
    ruta_excel = "base de datos.xlsx"
    
    if not os.path.exists(ruta_excel):
        print(f"❌ Error: No encuentro el archivo '{ruta_excel}'.")
        return

    try:
        # ==========================================
        # 1. LEER CONTABILIZACIÓN
        # ==========================================
        print("📄 Analizando pestaña: Contabilizacion...")
        df_cuentas = pd.read_excel(ruta_excel, sheet_name="Contabilizacion")
        df_cuentas.columns = df_cuentas.columns.str.strip()
        
        col_llave_contab = 'Origen_Documento' # Cambia esto a 'No_Comprobante' si te da 0 facturas al final
        col_cuenta_contab = 'Cuenta_PUC'
        
        df_cuentas = df_cuentas[[col_llave_contab, col_cuenta_contab]]
        df_cuentas[col_llave_contab] = df_cuentas[col_llave_contab].astype(str).str.strip().str.upper()

        datos_listos = []

        # ==========================================
        # 2. LEER MERCANCÍA
        # ==========================================
        print("📄 Analizando pestaña: mercancia...")
        df_mercancia = pd.read_excel(ruta_excel, sheet_name="mercancia")
        df_mercancia.columns = df_mercancia.columns.str.strip()
        
        col_llave_merc = 'ID_Factura'
        col_texto_merc = 'Item_Descripcion'
        
        df_mercancia[col_llave_merc] = df_mercancia[col_llave_merc].astype(str).str.strip().str.upper()
        df_m = pd.merge(df_mercancia, df_cuentas, left_on=col_llave_merc, right_on=col_llave_contab, how='inner')
        df_m = df_m.rename(columns={col_texto_merc: 'texto', col_cuenta_contab: 'etiqueta'})
        datos_listos.append(df_m[['texto', 'etiqueta']])

        # ==========================================
        # 3. LEER GASTOS ADMINISTRATIVOS
        # ==========================================
        print("📄 Analizando pestaña: Gastos_Administrativos...")
        df_gastos = pd.read_excel(ruta_excel, sheet_name="Gastos_Administrativos")
        df_gastos.columns = df_gastos.columns.str.strip()
        
        # 👉 EL ERROR ESTABA AQUÍ: En esta pestaña se llama ID_Gasto
        col_llave_gastos = 'ID_Gasto' 
        col_texto_gastos = 'Concepto_Gasto'
        
        df_gastos[col_llave_gastos] = df_gastos[col_llave_gastos].astype(str).str.strip().str.upper()
        df_g = pd.merge(df_gastos, df_cuentas, left_on=col_llave_gastos, right_on=col_llave_contab, how='inner')
        df_g = df_g.rename(columns={col_texto_gastos: 'texto', col_cuenta_contab: 'etiqueta'})
        datos_listos.append(df_g[['texto', 'etiqueta']])

        # ==========================================
        # 4. EXPORTAR ARCHIVO FINAL
        # ==========================================
        print("⚙️ Uniendo y consolidando registros...")
        df_final = pd.concat(datos_listos, ignore_index=True)
        
        df_final = df_final.dropna(subset=['texto', 'etiqueta'])
        df_final['etiqueta'] = df_final['etiqueta'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_final = df_final[df_final['texto'].str.lower() != 'nan']
        
        df_final.to_csv("datos_entrenamiento.csv", index=False, encoding="utf-8")
        print(f"\n🎉 ¡ÉXITO TOTAL! Se creó 'datos_entrenamiento.csv' con {len(df_final)} facturas reales listas para entrenar.")

    except Exception as e:
        print(f"\n⚠️ Ocurrió un error inesperado durante el cruce: {e}")

if __name__ == "__main__":
    preparar_datos_entrenamiento()