from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import pickle
import base64
from datetime import datetime, timedelta
from enum import Enum
import random
import numpy as np

app = FastAPI(title="Machine Learning Model Training API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class ModelType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    SVM = "svm"
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"

class TrainingStatus(str, Enum):
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataType(str, Enum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "excel"

# Data models
class Dataset(BaseModel):
    id: str
    name: str
    description: str
    file_path: str
    data_type: DataType
    size: int  # bytes
    rows: int
    columns: int
    features: List[str]
    target_column: Optional[str] = None
    created_at: datetime
    is_processed: bool = False
    statistics: Optional[Dict[str, Any]] = None

class Model(BaseModel):
    id: str
    name: str
    model_type: ModelType
    dataset_id: str
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, float]
    training_status: TrainingStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_path: Optional[str] = None
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    training_time: Optional[float] = None

class TrainingJob(BaseModel):
    id: str
    model_id: str
    dataset_id: str
    status: TrainingStatus
    progress: float  # 0.0 to 1.0
    current_epoch: int
    total_epochs: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics_history: List[Dict[str, float]] = []

class PredictionRequest(BaseModel):
    model_id: str
    input_data: Dict[str, Any]
    return_probabilities: bool = False

class PredictionResult(BaseModel):
    model_id: str
    prediction: Union[int, float, str]
    probabilities: Optional[Dict[str, float]] = None
    confidence: float
    timestamp: datetime

class Hyperparameter(BaseModel):
    name: str
    value: Any
    type: str  # "int", "float", "categorical"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None

class ModelArchitecture(BaseModel):
    layers: List[Dict[str, Any]]
    input_shape: List[int]
    output_shape: List[int]
    total_parameters: int

# In-memory storage
datasets: Dict[str, Dataset] = {}
models: Dict[str, Model] = {}
training_jobs: Dict[str, TrainingJob] = {}
predictions: Dict[str, List[PredictionResult]] = {}

# Utility functions
def generate_dataset_id() -> str:
    """Generate unique dataset ID"""
    return f"dataset_{uuid.uuid4().hex[:8]}"

def generate_model_id() -> str:
    """Generate unique model ID"""
    return f"model_{uuid.uuid4().hex[:8]}"

def generate_job_id() -> str:
    """Generate unique job ID"""
    return f"job_{uuid.uuid4().hex[:8]}"

def calculate_dataset_statistics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate basic dataset statistics"""
    if not data:
        return {}
    
    stats = {
        "total_rows": len(data),
        "columns": list(data[0].keys()) if data else [],
        "data_types": {},
        "missing_values": {},
        "numeric_stats": {}
    }
    
    for column in stats["columns"]:
        column_data = [row.get(column) for row in data if column in row and row[column] is not None]
        
        # Data type detection
        if column_data:
            sample_value = column_data[0]
            if isinstance(sample_value, (int, float)):
                stats["data_types"][column] = "numeric"
                # Calculate numeric statistics
                stats["numeric_stats"][column] = {
                    "mean": np.mean(column_data),
                    "std": np.std(column_data),
                    "min": np.min(column_data),
                    "max": np.max(column_data),
                    "median": np.median(column_data)
                }
            elif isinstance(sample_value, str):
                stats["data_types"][column] = "string"
            else:
                stats["data_types"][column] = "other"
        
        # Missing values
        missing_count = sum(1 for row in data if column not in row or row[column] is None)
        stats["missing_values"][column] = missing_count
    
    return stats

def mock_train_model(model: Model, dataset: Dataset, job: TrainingJob):
    """Mock model training process"""
    epochs = model.hyperparameters.get("epochs", 10)
    
    for epoch in range(epochs):
        # Update training progress
        job.current_epoch = epoch + 1
        job.progress = (epoch + 1) / epochs
        
        # Simulate training metrics
        accuracy = 0.5 + (epoch + 1) * 0.05 + random.uniform(-0.02, 0.02)
        loss = 1.0 - (epoch + 1) * 0.08 + random.uniform(-0.05, 0.05)
        
        job.metrics_history.append({
            "epoch": epoch + 1,
            "accuracy": accuracy,
            "loss": loss,
            "val_accuracy": accuracy - random.uniform(0.01, 0.03),
            "val_loss": loss + random.uniform(0.01, 0.03)
        })
        
        # Simulate training time
        asyncio.sleep(0.1)
    
    # Update model with final metrics
    final_metrics = job.metrics_history[-1]
    model.accuracy = final_metrics["accuracy"]
    model.loss = final_metrics["loss"]
    model.training_status = TrainingStatus.COMPLETED
    model.completed_at = datetime.now()
    model.training_time = (datetime.now() - job.started_at).total_seconds()
    
    # Update job
    job.status = TrainingStatus.COMPLETED
    job.completed_at = datetime.now()

async def process_training_job(job_id: str):
    """Process model training job"""
    job = training_jobs.get(job_id)
    if not job:
        return
    
    model = models.get(job.model_id)
    dataset = datasets.get(job.dataset_id)
    
    if not model or not dataset:
        job.status = TrainingStatus.FAILED
        job.error_message = "Model or dataset not found"
        return
    
    try:
        job.status = TrainingStatus.TRAINING
        await asyncio.sleep(0.1)  # Simulate setup time
        
        mock_train_model(model, dataset, job)
        
    except Exception as e:
        job.status = TrainingStatus.FAILED
        job.error_message = str(e)
        model.training_status = TrainingStatus.FAILED

def create_mock_dataset(data_type: DataType, rows: int = 1000, columns: int = 10) -> List[Dict[str, Any]]:
    """Create mock dataset for demonstration"""
    data = []
    
    for i in range(rows):
        row = {}
        for j in range(columns):
            column_name = f"feature_{j}"
            if j < columns - 1:  # Features
                row[column_name] = random.uniform(0, 100)
            else:  # Target
                if data_type == DataType.CSV:
                    row["target"] = random.randint(0, 1)  # Binary classification
                else:
                    row["target"] = random.uniform(0, 100)  # Regression
        data.append(row)
    
    return data

# API Endpoints
@app.post("/api/datasets", response_model=Dataset)
async def upload_dataset(
    name: str,
    description: str,
    data_type: DataType,
    target_column: Optional[str] = None,
    file: Optional[UploadFile] = None
):
    """Upload and create dataset"""
    dataset_id = generate_dataset_id()
    
    if file:
        # In a real implementation, this would process the uploaded file
        file_path = f"uploads/{dataset_id}_{file.filename}"
        # Mock file processing
        data = create_mock_dataset(data_type)
    else:
        # Create mock dataset
        data = create_mock_dataset(data_type)
        file_path = f"mock_data/{dataset_id}.csv"
    
    # Calculate statistics
    statistics = calculate_dataset_statistics(data)
    
    dataset = Dataset(
        id=dataset_id,
        name=name,
        description=description,
        file_path=file_path,
        data_type=data_type,
        size=len(str(data)),  # Mock size calculation
        rows=len(data),
        columns=len(data[0]) if data else 0,
        features=[col for col in data[0].keys() if col != target_column] if data else [],
        target_column=target_column,
        created_at=datetime.now(),
        is_processed=True,
        statistics=statistics
    )
    
    datasets[dataset_id] = dataset
    return dataset

@app.get("/api/datasets", response_model=List[Dataset])
async def get_datasets(data_type: Optional[DataType] = None):
    """Get all datasets"""
    filtered_datasets = list(datasets.values())
    
    if data_type:
        filtered_datasets = [d for d in filtered_datasets if d.data_type == data_type]
    
    return filtered_datasets

@app.get("/api/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    """Get specific dataset"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets[dataset_id]

@app.post("/api/models", response_model=Model)
async def create_model(
    name: str,
    model_type: ModelType,
    dataset_id: str,
    hyperparameters: Dict[str, Any]
):
    """Create a new model"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    model_id = generate_model_id()
    
    model = Model(
        id=model_id,
        name=name,
        model_type=model_type,
        dataset_id=dataset_id,
        hyperparameters=hyperparameters,
        metrics={},
        training_status=TrainingStatus.PENDING,
        created_at=datetime.now()
    )
    
    models[model_id] = model
    return model

@app.get("/api/models", response_model=List[Model])
async def get_models(model_type: Optional[ModelType] = None, status: Optional[TrainingStatus] = None):
    """Get all models"""
    filtered_models = list(models.values())
    
    if model_type:
        filtered_models = [m for m in filtered_models if m.model_type == model_type]
    
    if status:
        filtered_models = [m for m in filtered_models if m.training_status == status]
    
    return filtered_models

@app.get("/api/models/{model_id}", response_model=Model)
async def get_model(model_id: str):
    """Get specific model"""
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    return models[model_id]

@app.post("/api/models/{model_id}/train", response_model=TrainingJob)
async def train_model(model_id: str, background_tasks: BackgroundTasks):
    """Start model training"""
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models[model_id]
    
    if model.training_status == TrainingStatus.TRAINING:
        raise HTTPException(status_code=400, detail="Model is already training")
    
    job_id = generate_job_id()
    
    job = TrainingJob(
        id=job_id,
        model_id=model_id,
        dataset_id=model.dataset_id,
        status=TrainingStatus.PENDING,
        progress=0.0,
        current_epoch=0,
        total_epochs=model.hyperparameters.get("epochs", 10),
        started_at=datetime.now()
    )
    
    training_jobs[job_id] = job
    model.training_status = TrainingStatus.PENDING
    
    # Start training asynchronously
    background_tasks.add_task(process_training_job, job_id)
    
    return job

@app.get("/api/training-jobs/{job_id}", response_model=TrainingJob)
async def get_training_job(job_id: str):
    """Get training job status"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    return training_jobs[job_id]

@app.post("/api/training-jobs/{job_id}/cancel")
async def cancel_training_job(job_id: str):
    """Cancel training job"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    model = models[job.model_id]
    
    if job.status in [TrainingStatus.COMPLETED, TrainingStatus.FAILED, TrainingStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    job.status = TrainingStatus.CANCELLED
    job.completed_at = datetime.now()
    model.training_status = TrainingStatus.CANCELLED
    
    return {"message": "Training job cancelled successfully"}

@app.post("/api/predict", response_model=PredictionResult)
async def predict(request: PredictionRequest):
    """Make prediction using trained model"""
    if request.model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models[request.model_id]
    
    if model.training_status != TrainingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Model is not trained")
    
    # Mock prediction
    if model.model_type in [ModelType.CLASSIFICATION, ModelType.LOGISTIC_REGRESSION]:
        prediction = random.randint(0, 1)
        probabilities = {"0": 1 - prediction, "1": prediction} if request.return_probabilities else None
        confidence = random.uniform(0.7, 0.95)
    elif model.model_type in [ModelType.REGRESSION, ModelType.LINEAR_REGRESSION]:
        prediction = random.uniform(0, 100)
        probabilities = None
        confidence = random.uniform(0.6, 0.9)
    else:
        prediction = random.randint(0, 4)  # Multi-class
        probabilities = {str(i): random.uniform(0, 1) for i in range(5)} if request.return_probabilities else None
        confidence = random.uniform(0.5, 0.85)
    
    result = PredictionResult(
        model_id=request.model_id,
        prediction=prediction,
        probabilities=probabilities,
        confidence=confidence,
        timestamp=datetime.now()
    )
    
    # Store prediction
    if request.model_id not in predictions:
        predictions[request.model_id] = []
    predictions[request.model_id].append(result)
    
    return result

@app.get("/api/models/{model_id}/predictions", response_model=List[PredictionResult])
async def get_model_predictions(model_id: str, limit: int = 50):
    """Get prediction history for model"""
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return predictions.get(model_id, [])[-limit:]

@app.get("/api/model-types")
async def get_supported_model_types():
    """Get supported model types and their default hyperparameters"""
    return {
        "classification": {
            "description": "Binary and multi-class classification",
            "algorithms": ["logistic_regression", "random_forest", "svm", "neural_network"],
            "default_hyperparameters": {
                "epochs": 10,
                "learning_rate": 0.001,
                "batch_size": 32
            }
        },
        "regression": {
            "description": "Continuous value prediction",
            "algorithms": ["linear_regression", "random_forest", "svm", "neural_network"],
            "default_hyperparameters": {
                "epochs": 10,
                "learning_rate": 0.001,
                "batch_size": 32
            }
        },
        "clustering": {
            "description": "Unsupervised clustering",
            "algorithms": ["kmeans", "hierarchical", "dbscan"],
            "default_hyperparameters": {
                "n_clusters": 3,
                "max_iter": 100
            }
        },
        "neural_network": {
            "description": "Deep neural networks",
            "algorithms": ["cnn", "rnn", "lstm", "transformer"],
            "default_hyperparameters": {
                "epochs": 20,
                "learning_rate": 0.001,
                "batch_size": 64,
                "hidden_layers": [128, 64, 32]
            }
        }
    }

@app.get("/api/stats")
async def get_ml_stats():
    """Get machine learning platform statistics"""
    total_datasets = len(datasets)
    total_models = len(models)
    total_jobs = len(training_jobs)
    
    # Model type distribution
    model_distribution = {}
    for model in models.values():
        model_type = model.model_type.value
        model_distribution[model_type] = model_distribution.get(model_type, 0) + 1
    
    # Training status distribution
    status_distribution = {}
    for job in training_jobs.values():
        status = job.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Average accuracy
    completed_models = [m for m in models.values() if m.accuracy is not None]
    avg_accuracy = sum(m.accuracy for m in completed_models) / len(completed_models) if completed_models else 0
    
    return {
        "total_datasets": total_datasets,
        "total_models": total_models,
        "total_training_jobs": total_jobs,
        "model_distribution": model_distribution,
        "status_distribution": status_distribution,
        "average_accuracy": avg_accuracy,
        "supported_model_types": [t.value for t in ModelType],
        "total_predictions": sum(len(preds) for preds in predictions.values())
    }

@app.get("/")
async def root():
    return {"message": "Machine Learning Model Training API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
