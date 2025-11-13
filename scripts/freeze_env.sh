#!/usr/bin/env bash
set -e

REQ_DIR="../requirements"

echo "Generando snapshot completo del entorno..."
pip freeze > ${REQ_DIR}/tf-lock.txt

echo "Creando versión sin TensorFlow..."
grep -vE '^(tensorflow|keras|protobuf|grpcio|absl-py|opt-einsum|wrapt|astunparse|h5py)' \
    ${REQ_DIR}/tf-lock.txt > ${REQ_DIR}/no-tf.txt

echo "Archivos actualizados:"
echo " - ${REQ_DIR}/tf-lock.txt"
echo " - ${REQ_DIR}/no-tf.txt"
