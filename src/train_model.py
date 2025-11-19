import os
import argparse
from pathlib import Path
import tensorflow as tf
import keras
import numpy as np

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Train a simple TensorFlow model.")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--model-dir", type=str, default=os.getenv("MODEL_DIR", "/app/models"), help="Directory to save the model")
    parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate for optimizer")
    return parser.parse_args()

def main():
    """
    Main training function.
    """
    args = parse_args()
    
    print("TensorFlow version:", tf.__version__)
    print("GPUs available:", tf.config.list_physical_devices('GPU'))

    model_dir = Path(args.model_dir)
    save_path = model_dir / "model.keras"
    model_dir.mkdir(parents=True, exist_ok=True)

    # Minimum example of model and saving
    model = keras.Sequential([
        keras.layers.Input(shape=(4,)),
        keras.layers.Dense(8, activation="relu"),
        keras.layers.Dense(1)
    ])
    
    optimizer = keras.optimizers.Adam(learning_rate=args.learning_rate)
    model.compile(optimizer=optimizer, loss="mse")

    # Generate dummy data
    X = np.random.rand(100, 4).astype("float32")
    y = np.random.rand(100, 1).astype("float32")

    print(f"Starting training for {args.epochs} epochs...")
    model.fit(X, y, epochs=args.epochs, batch_size=args.batch_size, verbose=1)

    model.save(save_path)
    print(f"Model saved to: {save_path}")

if __name__ == "__main__":
    main()