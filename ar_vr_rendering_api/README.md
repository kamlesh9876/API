# AR/VR 3D Model Rendering API

A comprehensive API for creating, managing, and rendering 3D models for augmented and virtual reality applications.

## Features

- **3D Model Management**: Create, store, and manage 3D models with mesh data
- **Scene Composition**: Build complex scenes with multiple models and lighting
- **High-Quality Rendering**: Asynchronous rendering pipeline with multiple quality levels
- **AR Session Management**: Create AR sessions with tracking and anchor points
- **Multiple Formats**: Support for OBJ, GLTF, FBX, and DAE formats
- **Real-time Processing**: Background rendering jobs with progress tracking
- **Bounding Box Calculations**: Automatic spatial optimization
- **Material System**: Advanced material properties (PBR, glass, metal)

## API Endpoints

### 3D Models

#### Create Model
```http
POST /api/models?name=MyCube&format=obj&mesh_type=cube
```

#### Get All Models
```http
GET /api/models
```

#### Get Specific Model
```http
GET /api/models/{model_id}
```

### Scene Management

#### Create Scene
```http
POST /api/scenes
Content-Type: application/json

{
  "name": "My Scene",
  "model_ids": ["model_123", "model_456"],
  "environment": "studio"
}
```

#### Get All Scenes
```http
GET /api/scenes
```

#### Get Specific Scene
```http
GET /api/scenes/{scene_id}
```

### Rendering

#### Create Render Job
```http
POST /api/render
Content-Type: application/json

{
  "scene_id": "scene_123",
  "resolution": [1920, 1080],
  "quality": "high",
  "format": "png",
  "camera_position": {"x": 0, "y": 0, "z": 5},
  "camera_target": {"x": 0, "y": 0, "z": 0},
  "background_color": "#ffffff"
}
```

#### Get Render Job Status
```http
GET /api/render/{job_id}
```

#### Get Render Result
```http
GET /api/render/{job_id}/result
```

### AR Sessions

#### Create AR Session
```http
POST /api/ar/sessions?device_type=mobile&tracking_type=plane&duration_minutes=30
Content-Type: application/json

{
  "model_ids": ["model_123", "model_456"]
}
```

#### Get AR Session
```http
GET /api/ar/sessions/{session_id}
```

#### Add Anchor Point
```http
POST /api/ar/sessions/{session_id}/anchors
Content-Type: application/json

{
  "x": 1.5,
  "y": 0.0,
  "z": 2.0
}
```

### Statistics
```http
GET /api/stats
```

## Data Models

### 3D Model
```json
{
  "id": "model_123",
  "name": "My Cube",
  "format": "obj",
  "meshes": [
    {
      "id": "mesh_123",
      "vertices": [{"x": -1, "y": -1, "z": -1}, ...],
      "normals": [{"x": 0, "y": 0, "z": -1}, ...],
      "uvs": [[(0,0), (1,0), (1,1), (0,1)], ...],
      "indices": [0,1,2,0,2,3,...],
      "material": {
        "type": "standard",
        "color": "#4A90E2",
        "roughness": 0.5,
        "metalness": 0.1
      }
    }
  ],
  "position": {"x": 0, "y": 0, "z": 0},
  "rotation": {"w": 1, "x": 0, "y": 0, "z": 0},
  "scale": {"x": 1, "y": 1, "z": 1},
  "bounding_box": [
    {"x": -1, "y": -1, "z": -1},
    {"x": 1, "y": 1, "z": 1}
  ],
  "file_size": 1024,
  "created_at": "2024-01-01T12:00:00"
}
```

### Scene
```json
{
  "id": "scene_123",
  "name": "My Scene",
  "models": ["model_123", "model_456"],
  "environment": "studio",
  "lighting": {
    "ambient_intensity": 0.3,
    "directional_light": {
      "intensity": 1.0,
      "position": {"x": 1, "y": 1, "z": 1},
      "color": "#ffffff"
    }
  },
  "camera": {
    "position": {"x": 0, "y": 0, "z": 5},
    "target": {"x": 0, "y": 0, "z": 0},
    "fov": 60
  }
}
```

### Render Job
```json
{
  "id": "render_123",
  "status": "completed",
  "progress": 1.0,
  "request": {
    "scene_id": "scene_123",
    "resolution": [1920, 1080],
    "quality": "high",
    "format": "png"
  },
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:01:00",
  "result_url": "https://api.example.com/renders/render_123.png"
}
```

### AR Session
```json
{
  "id": "ar_123",
  "device_type": "mobile",
  "tracking_type": "plane",
  "anchor_points": [
    {"x": 1.5, "y": 0.0, "z": 2.0}
  ],
  "models": ["model_123"],
  "created_at": "2024-01-01T12:00:00",
  "expires_at": "2024-01-01T12:30:00"
}
```

## Supported Features

### 3D Model Types
- **Primitive Shapes**: Cube, Sphere, Cylinder, Cone
- **Complex Meshes**: Custom vertex/index data
- **Animated Models**: Skeletal animation support
- **Textured Models**: UV mapping and textures

### Materials
- **Basic**: Simple color materials
- **Standard**: Physically-based rendering
- **PBR**: Metallic-roughness workflow
- **Glass**: Transparent materials
- **Metal**: Metallic surfaces

### Environment Types
- **Studio**: Clean studio lighting
- **Outdoor**: Natural lighting simulation
- **Indoor**: Interior lighting setup
- **Space**: Space environment with stars

### AR Tracking Types
- **Plane**: Horizontal/vertical surface detection
- **Marker**: Image marker tracking
- **Face**: Facial landmark tracking
- **World**: SLAM world tracking

### Rendering Qualities
- **Low**: Fast preview quality
- **Medium**: Balanced quality/speed
- **High**: Production quality
- **Ultra**: Maximum quality with ray tracing

## Installation

```bash
pip install fastapi uvicorn
```

## Usage

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Example Usage

### Python Client
```python
import requests
import asyncio

# Create a 3D model
response = requests.post("http://localhost:8000/api/models", 
                        params={"name": "Test Cube", "mesh_type": "cube"})
model = response.json()
print(f"Created model: {model['id']}")

# Create a scene
scene_data = {
    "name": "Test Scene",
    "model_ids": [model["id"]],
    "environment": "studio"
}
response = requests.post("http://localhost:8000/api/scenes", json=scene_data)
scene = response.json()

# Start rendering
render_data = {
    "scene_id": scene["id"],
    "resolution": [1920, 1080],
    "quality": "high",
    "format": "png",
    "camera_position": {"x": 0, "y": 0, "z": 5},
    "camera_target": {"x": 0, "y": 0, "z": 0}
}
response = requests.post("http://localhost:8000/api/render", json=render_data)
render_job = response.json()

# Check render status
job_id = render_job["id"]
while True:
    response = requests.get(f"http://localhost:8000/api/render/{job_id}")
    job = response.json()
    print(f"Render progress: {job['progress']:.1%}")
    
    if job["status"] == "completed":
        result = requests.get(f"http://localhost:8000/api/render/{job_id}/result").json()
        print(f"Render completed: {result['result_url']}")
        break
    elif job["status"] == "failed":
        print(f"Render failed: {job['error_message']}")
        break
    
    asyncio.sleep(1)
```

### JavaScript Client
```javascript
// Create model
const modelResponse = await fetch('http://localhost:8000/api/models?name=MyCube&mesh_type=cube', {
  method: 'POST'
});
const model = await modelResponse.json();

// Create AR session
const arSession = await fetch('http://localhost:8000/api/ar/sessions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    device_type: 'mobile',
    tracking_type: 'plane',
    model_ids: [model.id]
  })
}).then(res => res.json());

// Add anchor point
await fetch(`http://localhost:8000/api/ar/sessions/${arSession.id}/anchors`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    x: 1.5, y: 0.0, z: 2.0
  })
});
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Rendering Settings
MAX_RENDER_RESOLUTION=4096
DEFAULT_RENDER_QUALITY=medium
RENDER_TIMEOUT=300

# Storage
MODEL_STORAGE_PATH=./models
RENDER_OUTPUT_PATH=./renders

# AR Settings
MAX_SESSION_DURATION=3600
ANCHOR_POINT_LIMIT=100

# Performance
MAX_CONCURRENT_RENDERS=5
MODEL_CACHE_SIZE=100
```

## Use Cases

- **E-commerce**: 3D product visualization and AR try-on
- **Architecture**: Building visualization and interior design
- **Gaming**: Asset management and scene rendering
- **Education**: Interactive 3D learning experiences
- **Manufacturing**: Product design and assembly visualization
- **Healthcare**: Medical imaging and surgical planning

## Advanced Features

### Advanced Lighting
- **HDR Lighting**: High dynamic range environment maps
- **Volumetric Lighting**: Atmospheric effects
- **Shadow Mapping**: Real-time shadow rendering
- **Global Illumination**: Indirect lighting simulation

### Animation System
- **Keyframe Animation**: Timeline-based animations
- **Physics Simulation**: Rigid body dynamics
- **Particle Systems**: Fire, smoke, water effects
- **Morph Targets**: Shape interpolation

### Performance Optimization
- **LOD System**: Level of detail optimization
- **Frustum Culling**: Viewport optimization
- **Occlusion Culling**: Hidden object removal
- **Texture Streaming**: On-demand texture loading

## Production Considerations

- **GPU Acceleration**: CUDA/OpenCL rendering support
- **Cloud Rendering**: Distributed rendering farms
- **CDN Integration**: Fast content delivery
- **Authentication**: API key-based access control
- **Rate Limiting**: Prevent abuse and overuse
- **Monitoring**: Performance metrics and health checks

## Integration Examples

### Unity Integration
```csharp
public class APIModelLoader : MonoBehaviour
{
    async void LoadModel(string modelId)
    {
        var response = await httpClient.GetAsync($"http://localhost:8000/api/models/{modelId}");
        var modelData = await response.Content.ReadAsStringAsync();
        // Parse and create Unity GameObject
    }
}
```

### Three.js Integration
```javascript
async function loadModel(modelId) {
    const response = await fetch(`http://localhost:8000/api/models/${modelId}`);
    const model = await response.json();
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(
        model.meshes[0].vertices.flatMap(v => [v.x, v.y, v.z]), 3
    ));
    
    const material = new THREE.MeshStandardMaterial({
        color: model.meshes[0].material.color
    });
    
    return new THREE.Mesh(geometry, material);
}
```
