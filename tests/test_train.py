from unittest.mock import patch
from src.train_model import main

def test_train_smoke():
    """
    Smoke test for training script.
    Runs the main function with minimal arguments to ensure it runs without error.
    """
    test_args = [
        "train_model.py",
        "--epochs", "1",
        "--batch-size", "10",
        "--model-dir", "/tmp/test_models"
    ]
    
    with patch("sys.argv", test_args):
        # We don't want to actually save files if possible, or we clean them up.
        # But for a smoke test, letting it write to /tmp is fine.
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
