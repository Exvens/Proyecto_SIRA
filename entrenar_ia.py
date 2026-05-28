import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch

def entrenar_sira():
    print("🎓 Iniciando la academia de SIRA...")
    
    # 1. Leer los datos históricos
    try:
        df = pd.read_csv("datos_entrenamiento.csv")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'datos_entrenamiento.csv'.")
        return

    # 2. Preparar las etiquetas (Convertir números de cuenta a IDs matemáticos)
    etiquetas_unicas = df['etiqueta'].astype(str).unique().tolist()
    label2id = {etiqueta: i for i, etiqueta in enumerate(etiquetas_unicas)}
    id2label = {i: etiqueta for i, etiqueta in enumerate(etiquetas_unicas)}
    
    df['label'] = df['etiqueta'].astype(str).map(label2id)
    dataset = Dataset.from_pandas(df)

    # 3. Cargar el Tokenizador y el Modelo base
    nombre_modelo_base = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
    tokenizer = AutoTokenizer.from_pretrained(nombre_modelo_base)
    
    print("🧠 Descargando modelo base para entrenamiento...")
    modelo = AutoModelForSequenceClassification.from_pretrained(
        nombre_modelo_base, 
        num_labels=len(etiquetas_unicas),
        label2id=label2id,
        id2label=id2label,
        ignore_mismatched_sizes=True # Permite cambiar la cabeza de Zero-Shot a Entrenamiento
    )

    # 4. Función para tokenizar los textos (convertir palabras en números)
    def tokenizar_datos(ejemplos):
        return tokenizer(ejemplos["texto"], padding="max_length", truncation=True, max_length=128)

    dataset_tokenizado = dataset.map(tokenizar_datos, batched=True)

    # 5. Configurar los parámetros de entrenamiento
    argumentos_entrenamiento = TrainingArguments(
        output_dir="./resultados_entrenamiento",
        num_train_epochs=5,              # Cuántas veces repasará los datos
        per_device_train_batch_size=8,   # Cuántos ejemplos procesa a la vez
        save_strategy="epoch",
        logging_dir='./logs',
    )

    # 6. Inicializar el Entrenador (Trainer)
    entrenador = Trainer(
        model=modelo,
        args=argumentos_entrenamiento,
        train_dataset=dataset_tokenizado,
    )

    # 7. ¡Comenzar el entrenamiento!
    print("🚀 Entrenando a SIRA (Esto puede tardar dependiendo de tu computadora)...")
    entrenador.train()

    # 8. Guardar el nuevo cerebro personalizado en tu disco duro
    ruta_guardado = "./modelo_sira_entrenado"
    modelo.save_pretrained(ruta_guardado)
    tokenizer.save_pretrained(ruta_guardado)
    
    print(f"✅ ¡Entrenamiento exitoso! El nuevo cerebro está en: {ruta_guardado}")

if __name__ == "__main__":
    entrenar_sira()