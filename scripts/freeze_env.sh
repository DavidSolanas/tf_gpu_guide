#!/usr/bin/env bash
set -euo pipefail

# Resolver rutas de forma robusta
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REQ_DIR="${SCRIPT_DIR}/../requirements"

mkdir -p "${REQ_DIR}"

echo "Generando snapshot completo del entorno (pip freeze)..."
pip freeze > "${REQ_DIR}/tf-lock.txt"

echo "Preparando exclusiones..."

# 1) Pila de TensorFlow (no queremos en no-tf.txt porque la imagen base ya lo incluye)
TF_STACK='tensorflow|tf-nightly|tensorflow-gpu|tensorflow-cpu|keras|tb-nightly|tensorboard|tensorboard-data-server|protobuf|grpcio|absl-py|opt-einsum|wrapt|astunparse|h5py|gast|google-pasta'

# 2) Paquetes típicos de desarrollo/QA/Jupyter (estáticos)
DEV_DEFAULT='pytest(-.*)?|pytest|pytest-cov|coverage|tox|nox|black|flake8|mypy|isort|pylint|bandit|pre-commit|ipython|ipykernel|jupyter(-.*)?|jupyterlab|notebook|nbconvert|nbformat|debugpy|rich|line-profiler|snakeviz|memory-profiler|mkdocs(-.*)?'

# 3) Herramientas de packaging/publicación (no necesarias en runtime)
PKG_TOOLS='pip|setuptools|wheel|build|twine|pkginfo|readme-renderer|keyring|requests-toolbelt|rfc3986|colorama'

# 4) Leer dinámicamente requirements/dev.txt (si existe) y excluir esos paquetes también
DEV_TXT_REGEX=''
if [[ -f "${REQ_DIR}/dev.txt" ]]; then
  # Extraer nombres de paquete (sin versiones ni extras)
  mapfile -t DEV_LIST < <(grep -E '^[a-zA-Z0-9_.-]+' "${REQ_DIR}/dev.txt" \
    | sed 's/\[.*\]//; s/[<>=!].*$//; s/[[:space:]]//g' | sort -u)
  if [[ "${#DEV_LIST[@]}" -gt 0 ]]; then
    DEV_TXT_REGEX="$(printf '%s|' "${DEV_LIST[@]}" | sed 's/|$//')"
  fi
fi

# Construir regex final de exclusión (línea comienza con cualquiera de estos paquetes)
# Nota: pip freeze lista como "package==version"; por eso usamos ^(pkg1|pkg2|...)
EXCLUDE_REGEX="^(${TF_STACK}"
if [[ -n "${DEV_TXT_REGEX}" ]]; then
  EXCLUDE_REGEX+="|${DEV_TXT_REGEX}"
fi
EXCLUDE_REGEX+="|${DEV_DEFAULT}|${PKG_TOOLS})"

echo "Excluyendo patrones en no-tf.txt:"
echo " - TF_STACK:      ${TF_STACK}"
echo " - DEV_DEFAULT:   ${DEV_DEFAULT}"
if [[ -n "${DEV_TXT_REGEX}" ]]; then
  echo " - DEV_TXT (dev): ${DEV_TXT_REGEX}"
fi
echo " - PKG_TOOLS:     ${PKG_TOOLS}"

# Generar prod-no-tf.txt filtrando tf-lock.txt
grep -vE "${EXCLUDE_REGEX}" "${REQ_DIR}/tf-lock.txt" > "${REQ_DIR}/prod-no-tf.txt"

echo "Archivos actualizados:"
echo " - ${REQ_DIR}/tf-lock.txt"
echo " - ${REQ_DIR}/prod-no-tf.txt"