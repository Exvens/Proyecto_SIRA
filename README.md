#  Proyecto SIRA (Sistema Inteligente de Reportes y Auditoría)

SIRA es una solución tecnológica integral de automatización contable diseñada para la lectura, auditoría normativa y contabilización inteligente de facturas utilizando Inteligencia Artificial y preparando los datos para su consumo vía RPA.

##  Características Actuales (Fase Inicial)
Hasta la fecha, el proyecto cuenta con los siguientes módulos funcionales:
- **Ingestión Multiformato:** Extracción automática de texto desde documentos no estructurados (`.pdf`) y estructurados (`.xml`).
- **Filtro de Legalidad DIAN:** Validación mediante expresiones regulares de los requisitos mínimos exigidos por la ley colombiana (NIT, denominación expresa, etc.).
- **Motor de Inteligencia Artificial (Zero-Shot):** Clasificación semántica de los conceptos facturados para sugerir la cuenta contable correcta utilizando modelos basados en la arquitectura Transformers (BERT/mDeBERTa).
- **Exportación Estructurada (JSON):** Generación automática de un archivo `lote_contabilizacion_rpa.json` con los datos limpios y clasificados, listo para ser consumido por un robot RPA (UiPath, Power Automate, etc.).

---

##  Estructura del Proyecto

```text
Proyecto_SIRA/
├── facturas_prueba/         # Carpeta donde se deben depositar los PDF/XML a procesar
│   ├── FE-1025.pdf
│   └── FE-1025.xml
├── .gitignore               # Exclusiones de Git (entornos virtuales, caché)
├── exportador_rpa.py        # Módulo que genera el archivo JSON final
├── ingestion.py             # Script principal que orquesta todo el flujo (Main)
├── modelo_ia.py             # Módulo de Inteligencia Artificial (Hugging Face)
├── requirements.txt         # Dependencias y librerías del proyecto
└── validador_dian.py        # Motor de auditoría normativa (Reglas DIAN)

⚙️ Guía de Instalación y Ejecución Local
Sigue estos pasos para clonar y ejecutar SIRA en tu máquina local.

1. Requisitos Previos
Tener instalado Python 3.9 o superior.

Tener Git instalado.

2. Clonar el repositorio
Abre tu terminal y clona este repositorio en tu máquina:

Bash
git clone <URL_DE_TU_REPOSITORIO_AQUI>
cd Proyecto_SIRA
3. Crear y activar el Entorno Virtual
Es una buena práctica aislar las dependencias del proyecto.

En Windows:

Bash
python -m venv venv
.\venv\Scripts\activate
En macOS / Linux:

Bash
python3 -m venv venv
source venv/bin/activate
4. Instalar Dependencias
Con el entorno virtual activado (deberías ver un (venv) en tu terminal), instala todas las librerías necesarias ejecutando:

Bash
pip install -r requirements.txt
(Nota: La instalación de librerías como torch puede tardar varios minutos dependiendo de tu conexión a internet).

5. Ejecutar el Modelo
Asegúrate de tener al menos una factura en formato PDF o XML dentro de la carpeta facturas_prueba/.

Ejecuta el orquestador principal:

Bash
python ingestion.py
(La primera vez que ejecutes el código, Python descargará el modelo de IA pre-entrenado, lo cual puede tomar un par de minutos).

6. Resultados
Al finalizar la ejecución, la consola mostrará el proceso de auditoría y la imputación contable de la IA. Automáticamente se generará en la raíz del proyecto un archivo llamado lote_contabilizacion_rpa.json con toda la información estructurada.