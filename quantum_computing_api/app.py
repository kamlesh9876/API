from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Tuple, Union
import asyncio
import json
import uuid
import math
import random
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

app = FastAPI(title="Quantum Computing Simulation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class GateType(str, Enum):
    H = "H"  # Hadamard
    X = "X"  # Pauli-X
    Y = "Y"  # Pauli-Y
    Z = "Z"  # Pauli-Z
    CNOT = "CNOT"  # Controlled-NOT
    CZ = "CZ"  # Controlled-Z
    SWAP = "SWAP"
    RX = "RX"  # Rotation around X
    RY = "RY"  # Rotation around Y
    RZ = "RZ"  # Rotation around Z
    PHASE = "PHASE"
    MEASURE = "MEASURE"

class AlgorithmType(str, Enum):
    GROVER = "grover"
    SHOR = "shor"
    QFT = "qft"  # Quantum Fourier Transform
    VQE = "vqe"  # Variational Quantum Eigensolver
    QAOA = "qaoa"  # Quantum Approximate Optimization Algorithm
    TELEPORTATION = "teleportation"
    SUPERDENSE = "superdense"
    BELL = "bell"

# Data models
class Qubit(BaseModel):
    id: int
    state_0: complex  # amplitude for |0⟩ state
    state_1: complex  # amplitude for |1⟩ state

class QuantumGate(BaseModel):
    type: GateType
    target_qubits: List[int]
    control_qubits: Optional[List[int]] = None
    parameters: Optional[Dict[str, float]] = None  # For rotation gates
    matrix: Optional[List[List[complex]]] = None

class QuantumCircuit(BaseModel):
    id: str
    name: str
    num_qubits: int
    gates: List[QuantumGate]
    depth: int
    created_at: datetime

class MeasurementResult(BaseModel):
    qubit_id: int
    outcome: int  # 0 or 1
    probability: float

class SimulationResult(BaseModel):
    circuit_id: str
    measurements: List[MeasurementResult]
    final_state: List[Qubit]
    probabilities: Dict[str, float]  # State string to probability
    execution_time: float
    shots: int
    timestamp: datetime

class QuantumAlgorithm(BaseModel):
    id: str
    type: AlgorithmType
    name: str
    description: str
    parameters: Dict[str, Any]
    circuit: QuantumCircuit
    expected_result: Optional[str] = None

class OptimizationProblem(BaseModel):
    id: str
    type: str  # "max_cut", "tsp", "knapsack"
    variables: List[str]
    constraints: List[Dict[str, Any]]
    objective_function: str
    optimal_value: Optional[float] = None

class VQEResult(BaseModel):
    algorithm_id: str
    energy: float
    optimal_parameters: Dict[str, float]
    convergence_history: List[float]
    iterations: int
    execution_time: float

# In-memory storage
quantum_circuits: Dict[str, QuantumCircuit] = {}
simulation_results: Dict[str, List[SimulationResult]] = {}
quantum_algorithms: Dict[str, QuantumAlgorithm] = {}
optimization_problems: Dict[str, OptimizationProblem] = {}
vqe_results: Dict[str, VQEResult] = {}

# Quantum gate matrices
GATE_MATRICES = {
    GateType.H: [[1/np.sqrt(2), 1/np.sqrt(2)], [1/np.sqrt(2), -1/np.sqrt(2)]],
    GateType.X: [[0, 1], [1, 0]],
    GateType.Y: [[0, -1j], [1j, 0]],
    GateType.Z: [[1, 0], [0, -1]],
    GateType.CNOT: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
    GateType.CZ: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]],
    GateType.SWAP: [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]],
}

# Utility functions
def generate_circuit_id() -> str:
    """Generate unique circuit ID"""
    return f"circuit_{uuid.uuid4().hex[:8]}"

def generate_algorithm_id() -> str:
    """Generate unique algorithm ID"""
    return f"algo_{uuid.uuid4().hex[:8]}"

def initialize_qubits(num_qubits: int) -> List[Qubit]:
    """Initialize qubits in |0⟩ state"""
    qubits = []
    for i in range(num_qubits):
        qubits.append(Qubit(
            id=i,
            state_0=complex(1, 0),
            state_1=complex(0, 0)
        ))
    return qubits

def apply_gate_to_qubits(qubits: List[Qubit], gate: QuantumGate) -> List[Qubit]:
    """Apply quantum gate to qubits"""
    new_qubits = qubits.copy()
    
    if gate.type == GateType.MEASURE:
        # Measurement collapses the qubit state
        for qubit_id in gate.target_qubits:
            qubit = new_qubits[qubit_id]
            prob_0 = abs(qubit.state_0) ** 2
            prob_1 = abs(qubit.state_1) ** 2
            
            # Random measurement based on probabilities
            if random.random() < prob_0:
                qubit.state_0 = complex(1, 0)
                qubit.state_1 = complex(0, 0)
            else:
                qubit.state_0 = complex(0, 0)
                qubit.state_1 = complex(1, 0)
    
    elif gate.type in [GateType.H, GateType.X, GateType.Y, GateType.Z]:
        # Single-qubit gates
        matrix = np.array(GATE_MATRICES[gate.type], dtype=complex)
        
        for qubit_id in gate.target_qubits:
            qubit = new_qubits[qubit_id]
            state_vector = np.array([qubit.state_0, qubit.state_1])
            new_state = matrix @ state_vector
            
            qubit.state_0 = new_state[0]
            qubit.state_1 = new_state[1]
    
    elif gate.type in [GateType.CNOT, GateType.CZ, GateType.SWAP]:
        # Two-qubit gates
        if len(gate.target_qubits) == 2:
            q1, q2 = gate.target_qubits
            
            # Create combined state vector
            combined_state = np.array([
                new_qubits[q1].state_0 * new_qubits[q2].state_0,
                new_qubits[q1].state_0 * new_qubits[q2].state_1,
                new_qubits[q1].state_1 * new_qubits[q2].state_0,
                new_qubits[q1].state_1 * new_qubits[q2].state_1
            ], dtype=complex)
            
            # Apply gate matrix
            matrix = np.array(GATE_MATRICES[gate.type], dtype=complex)
            new_combined_state = matrix @ combined_state
            
            # Extract individual qubit states (simplified - would need proper state decomposition)
            # For simplicity, we'll just update the first qubit
            new_qubits[q1].state_0 = new_combined_state[0] + new_combined_state[1]
            new_qubits[q1].state_1 = new_combined_state[2] + new_combined_state[3]
    
    elif gate.type in [GateType.RX, GateType.RY, GateType.RZ]:
        # Rotation gates
        angle = gate.parameters.get("angle", 0) if gate.parameters else 0
        
        if gate.type == GateType.RX:
            matrix = np.array([
                [np.cos(angle/2), -1j*np.sin(angle/2)],
                [-1j*np.sin(angle/2), np.cos(angle/2)]
            ], dtype=complex)
        elif gate.type == GateType.RY:
            matrix = np.array([
                [np.cos(angle/2), -np.sin(angle/2)],
                [np.sin(angle/2), np.cos(angle/2)]
            ], dtype=complex)
        else:  # RZ
            matrix = np.array([
                [np.exp(-1j*angle/2), 0],
                [0, np.exp(1j*angle/2)]
            ], dtype=complex)
        
        for qubit_id in gate.target_qubits:
            qubit = new_qubits[qubit_id]
            state_vector = np.array([qubit.state_0, qubit.state_1])
            new_state = matrix @ state_vector
            
            qubit.state_0 = new_state[0]
            qubit.state_1 = new_state[1]
    
    return new_qubits

def get_measurement_probabilities(qubits: List[Qubit]) -> Dict[str, float]:
    """Calculate measurement probabilities for all qubits"""
    probabilities = {}
    num_qubits = len(qubits)
    
    # For simplicity, we'll calculate individual qubit probabilities
    # In a real implementation, this would involve the full state vector
    for i, qubit in enumerate(qubits):
        prob_0 = abs(qubit.state_0) ** 2
        prob_1 = abs(qubit.state_1) ** 2
        
        # Create state string for this qubit
        state_0 = "0" * (num_qubits - i - 1) + "0" + "0" * i
        state_1 = "0" * (num_qubits - i - 1) + "1" + "0" * i
        
        probabilities[state_0] = prob_0
        probabilities[state_1] = prob_1
    
    return probabilities

def simulate_circuit(circuit: QuantumCircuit, shots: int = 1000) -> SimulationResult:
    """Simulate quantum circuit execution"""
    start_time = datetime.now()
    
    # Initialize qubits
    qubits = initialize_qubits(circuit.num_qubits)
    
    # Apply all gates
    for gate in circuit.gates:
        qubits = apply_gate_to_qubits(qubits, gate)
    
    # Perform measurements
    measurements = []
    for i, qubit in enumerate(qubits):
        prob_0 = abs(qubit.state_0) ** 2
        prob_1 = abs(qubit.state_1) ** 2
        
        # Simulate measurement outcome
        outcome = 0 if random.random() < prob_0 else 1
        probability = prob_0 if outcome == 0 else prob_1
        
        measurements.append(MeasurementResult(
            qubit_id=i,
            outcome=outcome,
            probability=probability
        ))
    
    # Calculate final probabilities
    probabilities = get_measurement_probabilities(qubits)
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    return SimulationResult(
        circuit_id=circuit.id,
        measurements=measurements,
        final_state=qubits,
        probabilities=probabilities,
        execution_time=execution_time,
        shots=shots,
        timestamp=datetime.now()
    )

def create_grover_circuit(num_qubits: int, target_state: str) -> QuantumCircuit:
    """Create Grover's search algorithm circuit"""
    circuit_id = generate_circuit_id()
    gates = []
    
    # Initialize with Hadamard gates
    for i in range(num_qubits):
        gates.append(QuantumGate(
            type=GateType.H,
            target_qubits=[i]
        ))
    
    # Oracle (simplified - would mark the target state)
    # For demonstration, we'll use a phase flip on the target state
    gates.append(QuantumGate(
        type=GateType.Z,
        target_qubits=[0]  # Simplified oracle
    ))
    
    # Diffusion operator (simplified)
    for i in range(num_qubits):
        gates.append(QuantumGate(
            type=GateType.H,
            target_qubits=[i]
        ))
        gates.append(QuantumGate(
            type=GateType.Z,
            target_qubits=[i]
        ))
        gates.append(QuantumGate(
            type=GateType.H,
            target_qubits=[i]
        ))
    
    return QuantumCircuit(
        id=circuit_id,
        name=f"Grover's Algorithm ({num_qubits} qubits)",
        num_qubits=num_qubits,
        gates=gates,
        depth=len(gates),
        created_at=datetime.now()
    )

def create_qft_circuit(num_qubits: int) -> QuantumCircuit:
    """Create Quantum Fourier Transform circuit"""
    circuit_id = generate_circuit_id()
    gates = []
    
    # QFT implementation
    for i in range(num_qubits):
        # Hadamard gate
        gates.append(QuantumGate(
            type=GateType.H,
            target_qubits=[i]
        ))
        
        # Controlled phase rotations
        for j in range(i + 1, num_qubits):
            angle = math.pi / (2 ** (j - i))
            gates.append(QuantumGate(
                type=GateType.RZ,
                target_qubits=[j],
                control_qubits=[i],
                parameters={"angle": angle}
            ))
    
    # Swap qubits (optional for QFT)
    for i in range(num_qubits // 2):
        gates.append(QuantumGate(
            type=GateType.SWAP,
            target_qubits=[i, num_qubits - 1 - i]
        ))
    
    return QuantumCircuit(
        id=circuit_id,
        name=f"Quantum Fourier Transform ({num_qubits} qubits)",
        num_qubits=num_qubits,
        gates=gates,
        depth=len(gates),
        created_at=datetime.now()
    )

def create_bell_state_circuit() -> QuantumCircuit:
    """Create Bell state preparation circuit"""
    circuit_id = generate_circuit_id()
    gates = [
        QuantumGate(
            type=GateType.H,
            target_qubits=[0]
        ),
        QuantumGate(
            type=GateType.CNOT,
            target_qubits=[0, 1]
        )
    ]
    
    return QuantumCircuit(
        id=circuit_id,
        name="Bell State Preparation",
        num_qubits=2,
        gates=gates,
        depth=len(gates),
        created_at=datetime.now()
    )

async def run_vqe_algorithm(problem: OptimizationProblem, algorithm: QuantumAlgorithm) -> VQEResult:
    """Run Variational Quantum Eigensolver algorithm"""
    start_time = datetime.now()
    
    # Simplified VQE implementation
    # In reality, this would involve classical-quantum optimization loop
    
    iterations = 100
    energy_history = []
    current_energy = random.uniform(-10, 0)  # Random initial energy
    
    for iteration in range(iterations):
        # Simulate energy evaluation (would involve quantum circuit execution)
        # Add some noise and convergence
        noise = random.gauss(0, 0.1)
        current_energy = current_energy * 0.95 + noise * 0.05
        energy_history.append(current_energy)
        
        await asyncio.sleep(0.01)  # Simulate computation time
    
    # Generate optimal parameters (simplified)
    optimal_params = {}
    for i in range(10):  # Assume 10 parameters
        optimal_params[f"theta_{i}"] = random.uniform(0, 2 * math.pi)
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    return VQEResult(
        algorithm_id=algorithm.id,
        energy=current_energy,
        optimal_parameters=optimal_params,
        convergence_history=energy_history,
        iterations=iterations,
        execution_time=execution_time
    )

# API Endpoints
@app.post("/api/circuits", response_model=QuantumCircuit)
async def create_circuit(circuit: QuantumCircuit):
    """Create a new quantum circuit"""
    quantum_circuits[circuit.id] = circuit
    return circuit

@app.get("/api/circuits", response_model=List[QuantumCircuit])
async def get_circuits():
    """Get all quantum circuits"""
    return list(quantum_circuits.values())

@app.get("/api/circuits/{circuit_id}", response_model=QuantumCircuit)
async def get_circuit(circuit_id: str):
    """Get specific quantum circuit"""
    if circuit_id not in quantum_circuits:
        raise HTTPException(status_code=404, detail="Circuit not found")
    return quantum_circuits[circuit_id]

@app.post("/api/circuits/{circuit_id}/simulate", response_model=SimulationResult)
async def simulate_circuit_endpoint(circuit_id: str, shots: int = 1000):
    """Simulate quantum circuit execution"""
    if circuit_id not in quantum_circuits:
        raise HTTPException(status_code=404, detail="Circuit not found")
    
    circuit = quantum_circuits[circuit_id]
    result = simulate_circuit(circuit, shots)
    
    # Store result
    if circuit_id not in simulation_results:
        simulation_results[circuit_id] =oo
    simulation_results[circuit_id].append(result)
    
    return result

@app.get("/api/circuits/{circuit_id}/results", response_model=List[SimulationResult])
async def get_circuit_results(circuit_id: str, limit: int = 50):
    """Get simulation results for a circuit"""
    if circuit_id not in simulation_results:
        return []
    
    return simulation_results[circuit_id][-limit:]

@app.post("/api/algorithms/grover", response_model=QuantumAlgorithm)
async def create_grover_algorithm(num_qubits: int, target_state: str):
    """Create Grover's search algorithm"""
    circuit = create_grover_circuit(num_qubits, target_state)
    
    algorithm = QuantumAlgorithm(
        id=generate_algorithm_id(),
        type=AlgorithmType.GROVER,
        name=f"Grover's Search ({num_qubits} qubits)",
        description=f"Search algorithm for {num_qubits}-qubit database",
        parameters={"target_state": target_state, "num_qubits": num_qubits},
        circuit=circuit,
        expected_result=target_state
    )
    
    quantum_algorithms[algorithm.id] = algorithm
    return algorithm

@app.post("/api/algorithms/qft", response_model=QuantumAlgorithm)
async def create_qft_algorithm(num_qubits: int):
    """Create Quantum Fourier Transform algorithm"""
    circuit = create_qft_circuit(num_qubits)
    
    algorithm = QuantumAlgorithm(
        id=generate_algorithm_id(),
        type=AlgorithmType.QFT,
        name=f"Quantum Fourier Transform ({num_qubits} qubits)",
        description=f"QFT implementation on {num_qubits} qubits",
        parameters={"num_qubits": num_qubits},
        circuit=circuit
    )
    
    quantum_algorithms[algorithm.id] = algorithm
    return algorithm

@app.post("/api/algorithms/bell", response_model=QuantumAlgorithm)
async def create_bell_algorithm():
    """Create Bell state preparation algorithm"""
    circuit = create_bell_state_circuit()
    
    algorithm = QuantumAlgorithm(
        id=generate_algorithm_id(),
        type=AlgorithmType.BELL,
        name="Bell State Preparation",
        description="Create maximally entangled Bell state",
        parameters={},
        circuit=circuit,
        expected_result="00 or 11 with equal probability"
    )
    
    quantum_algorithms[algorithm.id] = algorithm
    return algorithm

@app.get("/api/algorithms", response_model=List[QuantumAlgorithm])
async def get_algorithms(algorithm_type: Optional[AlgorithmType] = None):
    """Get all quantum algorithms"""
    algorithms = list(quantum_algorithms.values())
    
    if algorithm_type:
        algorithms = [algo for algo in algorithms if algo.type == algorithm_type]
    
    return algorithms

@app.post("/api/algorithms/{algorithm_id}/run", response_model=SimulationResult)
async def run_algorithm(algorithm_id: str, shots: int = 1000):
    """Run a quantum algorithm"""
    if algorithm_id not in quantum_algorithms:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    algorithm = quantum_algorithms[algorithm_id]
    result = simulate_circuit(algorithm.circuit, shots)
    
    # Store result
    if algorithm_id not in simulation_results:
        simulation_results[algorithm_id] = []
    simulation_results[algorithm_id].append(result)
    
    return result

@app.post("/api/optimization/vqe", response_model=VQEResult)
async def run_vqe_optimization(problem: OptimizationProblem, background_tasks: BackgroundTasks):
    """Run VQE optimization algorithm"""
    # Create a simple VQE circuit (simplified)
    circuit_id = generate_circuit_id()
    gates = []
    
    # Create parameterized circuit
    num_qubits = len(problem.variables)
    for i in range(num_qubits):
        gates.append(QuantumGate(
            type=GateType.RY,
            target_qubits=[i],
            parameters={"angle": 0.0}  # Will be optimized
        ))
    
    circuit = QuantumCircuit(
        id=circuit_id,
        name=f"VQE Circuit for {problem.type}",
        num_qubits=num_qubits,
        gates=gates,
        depth=len(gates),
        created_at=datetime.now()
    )
    
    algorithm = QuantumAlgorithm(
        id=generate_algorithm_id(),
        type=AlgorithmType.VQE,
        name=f"VQE for {problem.type}",
        description=f"Variational Quantum Eigensolver for {problem.type} problem",
        parameters={"problem_id": problem.id},
        circuit=circuit
    )
    
    # Run VQE
    result = await run_vqe_algorithm(problem, algorithm)
    
    # Store results
    optimization_problems[problem.id] = problem
    quantum_algorithms[algorithm.id] = algorithm
    vqe_results[result.algorithm_id] = result
    
    return result

@app.get("/api/gates", response_model=Dict[str, Any])
async def get_supported_gates():
    """Get supported quantum gates"""
    return {
        "single_qubit": ["H", "X", "Y", "Z", "RX", "RY", "RZ", "PHASE"],
        "two_qubit": ["CNOT", "CZ", "SWAP"],
        "multi_qubit": ["Toffoli", "Fredkin"],
        "measurements": ["MEASURE"],
        "gate_matrices": {k: [[str(cell) for cell in row] for row in mat] 
                         for k, mat in GATE_MATRICES.items()}
    }

@app.get("/api/stats")
async def get_quantum_stats():
    """Get quantum computing statistics"""
    total_circuits = len(quantum_circuits)
    total_algorithms = len(quantum_algorithms)
    total_simulations = sum(len(results) for results in simulation_results.values())
    
    # Average circuit depth
    avg_depth = sum(circuit.depth for circuit in quantum_circuits.values()) / total_circuits if total_circuits > 0 else 0
    
    # Algorithm distribution
    algo_distribution = {}
    for algo in quantum_algorithms.values():
        algo_type = algo.type.value
        algo_distribution[algo_type] = algo_distribution.get(algo_type, 0) + 1
    
    return {
        "total_circuits": total_circuits,
        "total_algorithms": total_algorithms,
        "total_simulations": total_simulations,
        "average_circuit_depth": avg_depth,
        "algorithm_distribution": algo_distribution,
        "supported_algorithms": [algo.value for algo in AlgorithmType],
        "supported_gates": len(GATE_MATRICES),
        "max_qubits_supported": 20  # Simulation limit
    }

@app.get("/")
async def root():
    return {"message": "Quantum Computing Simulation API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
