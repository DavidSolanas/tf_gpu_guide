# Handling Models in CI/CD Without Git

Since model files (`*.keras`, `*.h5`) are large binary files that shouldn't be versioned in Git, here are the solutions for CI/CD workflows:

## ✅ Solution Implemented: Train Model During CI

**What we did:** Modified both workflows to train a dummy model before building the Docker image.

```yaml
- name: Train dummy model for CI
  run: |
    mkdir -p models
    pip install tensorflow==2.16.1
    python src/train_model.py --epochs 1
    ls -lh models/
```

**Pros:**
- ✅ No external dependencies
- ✅ Always uses latest training code
- ✅ Fast (1 epoch training takes ~5-10 seconds)
- ✅ Tests that training code works

**Cons:**
- ❌ Not the "real" production model
- ❌ Adds ~30 seconds to CI time

---

## Alternative Solutions

### Option 2: Git LFS (Large File Storage)

Store models in Git using Git LFS:

```bash
# Setup (one time)
git lfs install
git lfs track "*.keras"
git lfs track "*.h5"
git add .gitattributes
git commit -m "Track model files with LFS"

# Add model
git add models/model.keras
git commit -m "Add trained model"
git push
```

**Pros:**
- ✅ Models versioned alongside code
- ✅ Easy rollback to previous models
- ✅ No CI changes needed

**Cons:**
- ❌ Costs money (GitHub: 1GB free, then $5/50GB/month)
- ❌ Slower git operations
- ❌ Requires LFS setup for all contributors

---

### Option 3: Download from Cloud Storage

Store models in S3/GCS/Azure Blob and download during CI:

```yaml
- name: Download model from S3
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  run: |
    mkdir -p models
    aws s3 cp s3://my-bucket/models/model.keras models/model.keras
```

**Pros:**
- ✅ Centralized model storage
- ✅ Can use production models in CI
- ✅ Easy to update models independently

**Cons:**
- ❌ Requires cloud infrastructure
- ❌ Needs secrets management
- ❌ Network dependency

---

### Option 4: GitHub Releases / Artifacts

Upload models as GitHub release assets:

```yaml
- name: Download model from release
  run: |
    mkdir -p models
    gh release download v1.0.0 --pattern "model.keras" --dir models/
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Pros:**
- ✅ Free (part of GitHub)
- ✅ Version models with releases
- ✅ No external dependencies

**Cons:**
- ❌ Manual upload process
- ❌ 2GB file size limit
- ❌ Requires release workflow

---

### Option 5: Model Registry (MLflow, Weights & Biases)

Use a dedicated model registry:

```yaml
- name: Download model from MLflow
  run: |
    pip install mlflow
    python -c "
    import mlflow
    mlflow.set_tracking_uri('${{ secrets.MLFLOW_URI }}')
    model = mlflow.keras.load_model('models:/my-model/production')
    model.save('models/model.keras')
    "
```

**Pros:**
- ✅ Professional ML workflow
- ✅ Model versioning and metadata
- ✅ A/B testing support
- ✅ Model lineage tracking

**Cons:**
- ❌ Requires MLflow/W&B infrastructure
- ❌ More complex setup
- ❌ Overkill for simple projects

---

## Recommendation by Project Size

| Project Size | Recommended Solution |
|--------------|---------------------|
| **Small/Demo** | ✅ Train during CI (current) |
| **Medium** | Git LFS or GitHub Releases |
| **Large/Production** | Cloud Storage (S3/GCS) |
| **Enterprise ML** | Model Registry (MLflow) |

---

## Current Setup Summary

**For your project**, we're using **Option 1: Train during CI** because:
1. It's a demo/learning project
2. Training is fast (1 epoch)
3. No external dependencies needed
4. Tests that training code works

The workflows will:
1. ✅ Train a dummy model with 1 epoch
2. ✅ Build Docker image with that model
3. ✅ Run all tests
4. ✅ Verify the model exists in the image

This approach works great for CI/CD testing while keeping your repository clean!
