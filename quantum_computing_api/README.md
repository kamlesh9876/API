# Quantum Computing Simulation API

A comprehensive quantum computing simulation platform for creating, simulating, and analyzing quantum circuits and algorithms.

## Features

- **Quantum Circuit Design**: Create and manipulate quantum circuits with various gates
- **Algorithm Library**: Pre-built quantum algorithms (Grover, QFT, VQE, Bell states)
- **Circuit Simulation**: Full quantum circuit simulation with measurement
- **Gate Library**: Complete set of quantum gates (Hadamard, Pauli, CNOT, rotations)
- **Optimization Algorithms**: VQE for solving optimization problems
- **Measurement Analysis**: Detailed measurement probabilities and outcomes
- **Multi-qubit Support**: Support for up to 20 qubits in simulation
- **Real-time Results**: Fast circuit execution and result visualization

## API Endpoints

### Circuit Management

#### Create Circuit
```http
POST /api/circuits
Content-Type: application/json

{
  "id": "circuit_001",
  "name": "Test Circuit",
  "num_qubits": 2,
  "gates": [
    {
      "type": "H",
      "target_qubits": [0]
    },
    {
      "type": "CNOT",
      "target_qubits": [0, 1]
    }
  ],
  "depth": 2
}
```

#### Get All Circuits
```http
GET /api/circuits
```

#### Get Specific Circuit
```http
GET /api/circuits/{circuit_id}
```

### Circuit Simulation

#### Simulate Circuit
```http
POST /api/circuits/{circuit_id}/simulate?shots=1000
```

#### Get Simulation Results
```http
GET /api/circuits/{circuit_id}/results?limit=50
```

### Quantum Algorithms

#### Create Grover's Algorithm
```http
POST /api/algorithms/grover?num_qubits=3&target_state=101
```

#### Create Quantum Fourier Transform
```http
POST /api/algorithms/qft?num_qubits=4
```

#### Create Bell State
```http
POST /api/algorithms/bell
```

#### Run Algorithm
```http
POST /api/algorithms/{algorithm_id}/run?shots=1000
```

#### Get All Algorithms
```http
GET /api/algorithms?algorithm_type=grover
```

### Optimization

#### Run VQE Optimization
```http
POST /api/optimization/vqe
Content-Type: application/json

{
  "id": "max_cut_001",
  "type": "max_cut",
  "variables": ["x1", "x2", "x3", "x4"],
  "constraints": [],
  "objective_function": "maximize sum of edge weights"
}
```

### Reference

#### Get Supported Gates
```http
GET /api/gates
```

#### Get Statistics
```http
GET /api/stats
```

## Data Models

### Quantum Circuit
```json
{
  "id": "circuit_001",
  "name": "Bell State Circuit",
  "num_qubits": 2,
  "gates": [
    {
      "type": "H",
      "target_qubits": [0]
    },
    {
      "type": "CNOT",
      "target_qubits": [0, 1]
    }
  ],
  "depth": 2,
  "created_at": "2024-01-01T12:00:00"
}
```

### Quantum Gate
```json
{
  "type": "RY",
  "target_qubits": [0],
  "parameters": {
    "angle": 1.5708
  }
}
```

### Qubit State
```json
{
  "id": 0,
  "state_0": "0.707+0.000j",
  "state_1": "0.707+0.000j"
}
```

### Simulation Result
```json
{
  "circuit_id": "circuit_001",
  "measurements": [
    {
      "qubit_id": 0,
      "outcome": 0,
      "probability": 0.5
    },
    {
      "qubit_id": 1,
      "outcome": 0,
      "probability": 0.5
    }
  ],
  "final_state": [...],
  "probabilities": {
    "00": 0.5,
    "11": 0.5
  },
  "execution_time": 0.025,
  "shots": 1000,
  "timestamp": "2024-01-01T12:00:00"
}
```

### VQE Result
```json
{
  "algorithm_id": "vqe_001",
  "energy": -5.23,
  "optimal_parameters": {
    "theta_0": 1.234,
    "theta_1": 2.567
  },
  "convergence_history": [-10.5, -8.2, -6.1, -5.23],
  "iterations": 100,
  "execution_time": 2.45
}
```

## Supported Quantum Gates

### Single-Qubit Gates
- **H (Hadamard)**: Creates superposition states
- **X (Pauli-X)**: Bit flip gate
- **Y (Pauli-Y)**: Phase and bit flip
- **Z (Pauli-Z)**: Phase flip gate
- **RX**: Rotation around X-axis
- **RY**: Rotation around Y-axis
- **RZ**: Rotation around Z-axis
- **PHASE**: Phase gate

### Two-Qubit Gates
- **CNOT**: Controlled-NOT gate
- **CZ**: Controlled-Z gate
- **SWAP**: Swaps two qubit states

### Measurements
- **MEASURE**: Collapses qubit to classical state

## Quantum Algorithms

### 1. Grover's Search Algorithm
- **Purpose**: Search unsorted database in O(√N) time
- **Qubits**: Variable (typically log₂(N))
- **Oracle**: Marks target state
- **Amplitude Amplification**: Enhances target state probability

### 2. Quantum Fourier Transform (QFT)
- **Purpose**: Transform between computational and Fourier bases
- **Applications**: Period finding, phase estimation
- **Complexity**: O(n²) gates for n qubits
- **Structure**: Hadamard + controlled rotations + swaps

### 3. Bell State Preparation
- **Purpose**: Create maximally entangled states
- **Qubits**: 2
- **States**: |00⟩ + |11⟩ or |01⟩ + |10⟩
- **Applications**: Quantum teleportation, cryptography

### 4. Variational Quantum Eigensolver (VQE)
- **Purpose**: Find ground state energy of Hamiltonian
- **Method**: Hybrid classical-quantum optimization
- **Applications**: Chemistry, optimization problems
- **Convergence**: Iterative parameter optimization

## Installation

```bash
pip install fastapi uvicorn numpy
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
import json

# Create a Bell state circuit
circuit_data = {
    "id": "bell_circuit",
    "name": "Bell State",
    "num_qubits": 2,
    "gates": [
        {"type": "H", "target_qubits": [0]},
        {"type": "CNOT", "target_qubits": [0, 1]}
    ],
    "depth": 2
}

response = requests.post("http://localhost:8000/api/circuits", json=circuit_data)
circuit = response.json()
print(f"Created circuit: {circuit['id']}")

# Simulate the circuit
response = requests.post(f"http://localhost:8000/api/circuits/{circuit['id']}/simulate?shots=1000")
result = response.json()

print("Measurement results:")
for measurement in result['measurements']:
    print(f"Qubit {measurement['qubit_id']}: {measurement['outcome']} (p={measurement['probability']:.3f})")

print("\nState probabilities:")
for state, prob in result['probabilities'].items():
    print(f"|{state}⟩: {prob:.3f}")

# Create Grover's algorithm
response = requests.post("http://localhost:8000/api/algorithms/grover?num_qubits=3&target_state=101")
grover = response.json()

# Run the algorithm
response = requests.post(f"http://localhost:8000/api/algorithms/{grover['id']}/run?shots=1000")
result = response.json()

print(f"\nGrover's Algorithm Results:")
print(f"Target state probability: {result['probabilities'].get('101', 0):.3f}")
```

### JavaScript Client
```javascript
// Create Bell state circuit
const circuit = {
  id: 'bell_js',
  name: 'Bell State (JS)',
  num_qubits: 2,
  gates: [
    { type: 'H', target_qubits: [0] },
    { type: 'CNOT', target_qubits: [0, 1] }
  ],
  depth: 2
};

const circuitResponse = await fetch('http://localhost:8000/api/circuits', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(circuit)
});
const createdCircuit = await circuitResponse.json();

// Simulate circuit
const simResponse = await fetch(`http://localhost:8000/api/circuits/${createdCircuit.id}/simulate?shots=1000`);
const result = await simResponse.json();

console.log('Bell State Results:');
result.measurements.forEach(m => {
  console.log(`Qubit ${m.qubit_id}: ${m.outcome} (p=${m.probability.toFixed(3)})`);
});

// Create and run QFT
const qftResponse = await fetch('http://localhost:8000/api/algorithms/qft?num_qubits=4');
const qft = await qftResponse.json();

const qftRunResponse = await fetch(`http://localhost:8000/api/algorithms/${qft.id}/run?shots=1000`);
const qftResult = await qftRunResponse.json();

console.log('\nQFT Results:');
Object.entries(qftResult.probabilities).forEach(([state, prob]) => {
  console.log(`|${state}⟩: ${prob.toFixed(3)}`);
});
```

## Advanced Features

### Custom Gate Parameters
```json
{
  "type": "RY",
  "target_qubits": [0],
  "parameters": {
    "angle": 1.5708
  }
}
```

### Controlled Gates
```json
{
  "type": "CNOT",
  "target_qubits": [0, 1],
  "control_qubits": [0]
}
```

### Multi-qubit Operations
- **Toffoli Gate**: Three-qubit controlled operation
- **Fredkin Gate**: Controlled swap operation
- **Multi-controlled gates**: Arbitrary control patterns

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Simulation Settings
MAX_QUBITS=20
DEFAULT_SHOTS=1000
SIMULATION_TIMEOUT=30

# Performance
ENABLE_CACHING=true
CACHE_TTL=300
MAX_CONCURRENT_SIMULATIONS=10

# Results Storage
RESULT_RETENTION_HOURS=24
MAX_RESULTS_PER_CIRCUIT=100

# Logging
LOG_LEVEL=info
ENABLE_DETAILED_LOGGING=false
```

## Use Cases

- **Education**: Learn quantum computing concepts
- **Research**: Prototype quantum algorithms
- **Development**: Test quantum circuit designs
- **Optimization**: Solve combinatorial problems with VQE
- **Cryptography**: Study quantum cryptographic protocols
- **Simulation**: Benchmark quantum algorithm performance

## Quantum Computing Concepts

### Qubit States
- **Basis States**: |0⟩ and |1⟩
- **Superposition**: α|0⟩ + β|1⟩ where |α|² + |β|² = 1
- **Entanglement**: Correlated qubit states
- **Measurement**: Collapse to classical state

### Quantum Gates
- **Unitary Operations**: Reversible transformations
- **Matrix Representation**: 2ⁿ × 2ⁿ matrices for n qubits
- **Gate Composition**: Sequential gate application
- **Quantum Circuits**: Directed acyclic graphs of gates

### Measurement
- **Projective Measurement**: Standard computational basis
- **Probability**: |α|² for |0⟩, |β|² for |1⟩
- **State Collapse**: Post-measurement state update
- **Multiple Shots**: Statistical distribution

## Performance Considerations

- **Simulation Complexity**: O(2ⁿ) memory for n qubits
- **Gate Application**: Matrix multiplication overhead
- **Measurement Sampling**: Monte Carlo simulation
- **Optimization**: Classical-quantum hybrid algorithms

## Integration Examples

### Jupyter Notebook
```python
import requests
import matplotlib.pyplot as plt

# Create and simulate circuit
circuit = {...}
result = simulate_circuit(circuit)

# Visualize results
states = list(result['probabilities'].keys())
probs = list(result['probabilities'].values())

plt.bar(states, probs)
plt.title('Quantum State Probabilities')
plt.ylabel('Probability')
plt.show()
```

### Quantum Circuit Visualization
```javascript
// Generate circuit diagram
function visualizeCircuit(circuit) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  
  circuit.gates.forEach((gate, index) => {
    // Draw gate on circuit diagram
    const gateElement = drawGate(gate, index);
    svg.appendChild(gateElement);
  });
  
  return svg;
}
```

## Future Enhancements

- **Real Quantum Hardware**: Integration with IBM Q, Rigetti, etc.
- **Advanced Algorithms**: QAOA, Quantum Machine Learning
- **Error Correction**: Fault-tolerant quantum computing
- **Circuit Optimization**: Gate synthesis and minimization
- **Visualization**: Interactive circuit diagrams
- **Collaboration**: Shared circuits and algorithms
