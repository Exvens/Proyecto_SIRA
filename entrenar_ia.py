import pandas as pd
import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import torch
import os

def entrenar_sira():
    print("🎓 Iniciando la academia de SIRA en Google Colab (GPU)...")
    
    # Validar uso de GPU
    if torch.cuda.is_available():
        print(f"⚡ Aceleración de Hardware activada: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ Advertencia: Estás usando CPU. El entrenamiento será muy lento.")

    # 1. Leer los datos históricos
    try:
        df = pd.read_csv("datos_entrenamiento.csv")
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'datos_entrenamiento.csv'. Sube el archivo a Colab.")
        return

    # 2. Preparar las etiquetas
    etiquetas_unicas = sorted(df['etiqueta'].astype(str).unique().tolist())
    label2id = {etiqueta: i for i, etiqueta in enumerate(etiquetas_unicas)}
    id2label = {i: etiqueta for i, etiqueta in enumerate(etiquetas_unicas)}
    
    df['label'] = df['etiqueta'].astype(str).map(label2id)
    dataset = Dataset.from_pandas(df)

    # 🚀 NUEVO: Dividir en Entrenamiento (80%) y Validación (20%)
    dataset_dividido = dataset.train_test_split(test_size=0.2, seed=42)
    dataset_entrenamiento = dataset_dividido['train']
    dataset_validacion = dataset_dividido['test']

    # 3. Cargar el Tokenizador y el Modelo base (BETO)
    nombre_modelo_base = "dccuchile/bert-base-spanish-wwm-uncased"
    print(f"🧠 Descargando BETO: {nombre_modelo_base}...")
    
    tokenizer = AutoTokenizer.from_pretrained(nombre_modelo_base)
    modelo = AutoModelForSequenceClassification.from_pretrained(
        nombre_modelo_base, 
        num_labels=len(etiquetas_unicas),
        label2id=label2id,
        id2label=id2label,
        ignore_mismatched_sizes=True 
    )

    # 4. Función para tokenizar los textos
    def tokenizar_datos(ejemplos):
        return tokenizer(ejemplos["texto"], padding="max_length", truncation=True, max_length=128)

    print("⚙️ Tokenizando conjuntos de datos...")
    train_tokenizado = dataset_entrenamiento.map(tokenizar_datos, batched=True)
    eval_tokenizado = dataset_validacion.map(tokenizar_datos, batched=True)

    # 🚀 NUEVO: Función para extraer los hallazgos estratégicos (Métricas)
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
        acc = accuracy_score(labels, preds)
        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    # 5. Configurar los parámetros de entrenamiento
    argumentos_entrenamiento = TrainingArguments(
        output_dir="./resultados_entrenamiento",
        num_train_epochs=5,
        per_device_train_batch_size=16, # BETO maneja bien lotes de 16 en GPUs T4
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",    # Evaluar al final de cada época
        save_strategy="epoch",
        logging_dir='./logs',
        logging_steps=10,
        load_best_model_at_end=True,    # Se queda con la versión más precisa
        metric_for_best_model="accuracy"
    )

    # 6. Inicializar el Entrenador (Trainer)
    entrenador = Trainer(
        model=modelo,
        args=argumentos_entrenamiento,
        train_dataset=train_tokenizado,
        eval_dataset=eval_tokenizado,    # Le pasamos los datos de prueba
        compute_metrics=compute_metrics  # Le pasamos la función de métricas
    )

    # 7. ¡Comenzar el entrenamiento!
    print("🚀 Entrenando a SIRA...")
    entrenador.train()

    # Mostrar hallazgos finales
    print("\n📊 Generando hallazgos estratégicos finales sobre el set de validación...")
    resultados = entrenador.evaluate()
    print(f"🎯 Precisión Final (Accuracy): {resultados['eval_accuracy']*100:.2f}%")

    # 8. Guardar el nuevo cerebro personalizado
    ruta_guardado = "./modelo_sira_entrenado"
    modelo.save_pretrained(ruta_guardado)
    tokenizer.save_pretrained(ruta_guardado)
    
    print(f"\n✅ ¡Entrenamiento exitoso! El modelo y tokenizador están en: {ruta_guardado}")

if __name__ == "__main__":
    entrenar_sira()