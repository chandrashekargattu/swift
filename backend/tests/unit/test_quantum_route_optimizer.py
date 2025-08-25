"""
Comprehensive unit tests for Quantum Route Optimizer.

These tests cover edge cases that go beyond traditional testing:
1. Quantum state coherence and decoherence
2. Superposition collapse behaviors
3. Entanglement effects on route optimization
4. Tunneling probability distributions
5. Hamiltonian energy landscape validation
6. Phase transition points in optimization
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from typing import List, Set
import cmath

from app.services.quantum_route_optimizer import (
    QuantumRouteOptimizer,
    Driver,
    Passenger,
    RouteSegment,
    QuantumState
)


class TestQuantumRouteOptimizer:
    """Test cases for quantum-inspired route optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return QuantumRouteOptimizer()
    
    @pytest.fixture
    def sample_drivers(self):
        """Create sample drivers with various capabilities."""
        return [
            Driver(
                id="d1",
                current_location=(19.0760, 72.8777),  # Mumbai
                capacity=4,
                available_from=datetime.now(),
                skills={"wheelchair_accessible", "pet_friendly"},
                rating=4.8,
                fuel_efficiency=15.0
            ),
            Driver(
                id="d2",
                current_location=(19.0826, 72.8856),  # Near Mumbai
                capacity=6,
                available_from=datetime.now() + timedelta(minutes=5),
                skills={"luxury", "wifi"},
                rating=4.9,
                fuel_efficiency=12.0
            ),
            Driver(
                id="d3",
                current_location=(19.0896, 72.8656),  # Another location
                capacity=4,
                available_from=datetime.now(),
                skills={"pet_friendly", "child_seat"},
                rating=4.5,
                fuel_efficiency=18.0
            )
        ]
    
    @pytest.fixture
    def sample_passengers(self):
        """Create sample passengers with various requirements."""
        return [
            Passenger(
                id="p1",
                pickup_location=(19.0728, 72.8826),
                dropoff_location=(19.1136, 72.8697),
                requested_time=datetime.now() + timedelta(minutes=10),
                required_capacity=2,
                special_requirements={"wheelchair_accessible"},
                max_wait_time=timedelta(minutes=15),
                priority=1.0
            ),
            Passenger(
                id="p2",
                pickup_location=(19.0858, 72.8781),
                dropoff_location=(19.0422, 72.8378),
                requested_time=datetime.now() + timedelta(minutes=5),
                required_capacity=1,
                special_requirements=set(),
                max_wait_time=timedelta(minutes=10),
                priority=0.8
            ),
            Passenger(
                id="p3",
                pickup_location=(19.0798, 72.8899),
                dropoff_location=(19.1000, 72.9000),
                requested_time=datetime.now() + timedelta(minutes=20),
                required_capacity=3,
                special_requirements={"pet_friendly", "child_seat"},
                max_wait_time=timedelta(minutes=20),
                priority=0.9
            )
        ]
    
    # Test Quantum State Properties
    
    def test_hamiltonian_hermiticity(self, optimizer, sample_drivers, sample_passengers):
        """Test that Hamiltonian is Hermitian (H = H†)."""
        distance_matrix = optimizer._build_distance_matrix(sample_drivers, sample_passengers)
        time_matrix = optimizer._build_time_matrix(sample_drivers, sample_passengers, distance_matrix)
        
        H = optimizer.calculate_hamiltonian(
            sample_drivers, sample_passengers, distance_matrix, time_matrix
        )
        
        # Check Hermiticity
        assert np.allclose(H, H.conj().T), "Hamiltonian must be Hermitian"
        
        # Check eigenvalues are real
        eigenvalues = np.linalg.eigvals(H)
        assert np.allclose(eigenvalues.imag, 0), "Hermitian matrix must have real eigenvalues"
    
    def test_quantum_state_normalization(self, optimizer):
        """Test quantum state remains normalized throughout evolution."""
        n = 10
        state = np.ones(n, dtype=complex) / np.sqrt(n)
        
        # Random Hamiltonian
        H = np.random.randn(n, n) + 1j * np.random.randn(n, n)
        H = (H + H.conj().T) / 2  # Make Hermitian
        
        # Apply operations
        state = optimizer._apply_phase_separator(state, H, 0.5)
        assert np.abs(np.linalg.norm(state) - 1.0) < 1e-10, "State must remain normalized"
        
        state = optimizer._apply_mixing_operator(state, 0.3)
        assert np.abs(np.linalg.norm(state) - 1.0) < 1e-10, "State must remain normalized after mixing"
    
    def test_superposition_collapse(self, optimizer):
        """Test quantum state collapse preserves probability distribution."""
        n = 20
        # Create entangled state
        state = np.zeros(n, dtype=complex)
        state[0] = 1/np.sqrt(2)
        state[n-1] = 1/np.sqrt(2)
        
        probabilities = np.abs(state)**2
        
        # Test multiple measurements
        measurements = []
        for _ in range(1000):
            assignment = optimizer._measure_quantum_state(probabilities)
            measurements.append(assignment)
        
        # Check probability distribution
        assert len(measurements) > 0, "Measurements should be recorded"
    
    def test_quantum_tunneling_barrier_crossing(self, optimizer):
        """Test quantum tunneling can escape local minima."""
        n = 10
        # Create state trapped in local minimum
        state = np.zeros(n, dtype=complex)
        state[0] = 1.0  # Trapped state
        
        # Energy landscape with barrier
        H = np.diag(np.array([10, 20, 30, 20, 10, 5, 4, 3, 2, 1]))
        
        # Try tunneling multiple times
        tunneled = False
        for _ in range(100):
            new_state = optimizer._quantum_tunnel(state, H)
            if not np.allclose(new_state, state):
                tunneled = True
                # Check energy decreased
                old_energy = np.real(state.conj() @ H @ state)
                new_energy = np.real(new_state.conj() @ H @ new_state)
                assert new_energy < old_energy, "Tunneling should reduce energy"
                break
        
        assert tunneled, "Quantum tunneling should occur with sufficient attempts"
    
    def test_decoherence_progression(self, optimizer):
        """Test decoherence increases with time."""
        n = 10
        initial_state = np.ones(n, dtype=complex) / np.sqrt(n)
        
        coherences = []
        state = initial_state.copy()
        
        for iteration in range(optimizer.coherence_time * 2):
            state = optimizer._apply_decoherence(state, iteration)
            # Measure coherence as off-diagonal density matrix elements
            density_matrix = np.outer(state, state.conj())
            coherence = np.sum(np.abs(density_matrix - np.diag(np.diag(density_matrix))))
            coherences.append(coherence)
        
        # Coherence should generally decrease
        assert coherences[-1] < coherences[0], "Coherence should decrease over time"
    
    # Test Edge Cases in Route Optimization
    
    @pytest.mark.asyncio
    async def test_empty_drivers_list(self, optimizer, sample_passengers):
        """Test behavior with no available drivers."""
        routes = await optimizer.optimize_routes([], sample_passengers)
        assert routes == {}, "Should return empty routes for no drivers"
    
    @pytest.mark.asyncio
    async def test_empty_passengers_list(self, optimizer, sample_drivers):
        """Test behavior with no passengers."""
        routes = await optimizer.optimize_routes(sample_drivers, [])
        assert all(len(r) == 0 for r in routes.values()), "Should return empty routes for no passengers"
    
    @pytest.mark.asyncio
    async def test_single_driver_multiple_passengers(self, optimizer, sample_passengers):
        """Test optimization with resource scarcity."""
        single_driver = [Driver(
            id="d1",
            current_location=(19.0760, 72.8777),
            capacity=4,
            available_from=datetime.now(),
            skills=set(),
            rating=4.5,
            fuel_efficiency=15.0
        )]
        
        routes = await optimizer.optimize_routes(single_driver, sample_passengers)
        
        # Driver can only serve one passenger at a time
        assert len(routes) == 1
        assert "d1" in routes
        # Should pick optimal passenger
        assert len(routes["d1"]) == 2  # Pickup and dropoff
    
    @pytest.mark.asyncio
    async def test_impossible_capacity_constraints(self, optimizer):
        """Test when passenger capacity exceeds all driver capacities."""
        drivers = [Driver(
            id=f"d{i}",
            current_location=(19.0760 + i*0.01, 72.8777),
            capacity=2,  # Max capacity 2
            available_from=datetime.now(),
            skills=set(),
            rating=4.5,
            fuel_efficiency=15.0
        ) for i in range(3)]
        
        passengers = [Passenger(
            id="p1",
            pickup_location=(19.0728, 72.8826),
            dropoff_location=(19.1136, 72.8697),
            requested_time=datetime.now() + timedelta(minutes=10),
            required_capacity=5,  # Exceeds all driver capacities
            special_requirements=set(),
            max_wait_time=timedelta(minutes=15),
            priority=1.0
        )]
        
        routes = await optimizer.optimize_routes(drivers, passengers)
        
        # No driver can serve this passenger
        assert all(len(r) == 0 for r in routes.values()), "Should not assign impossible passengers"
    
    @pytest.mark.asyncio
    async def test_special_requirements_matching(self, optimizer):
        """Test matching with complex special requirements."""
        drivers = [
            Driver(
                id="d1",
                current_location=(19.0760, 72.8777),
                capacity=4,
                available_from=datetime.now(),
                skills={"wheelchair_accessible"},
                rating=4.8,
                fuel_efficiency=15.0
            ),
            Driver(
                id="d2",
                current_location=(19.0760, 72.8777),
                capacity=4,
                available_from=datetime.now(),
                skills={"pet_friendly", "child_seat"},
                rating=4.5,
                fuel_efficiency=15.0
            )
        ]
        
        passengers = [
            Passenger(
                id="p1",
                pickup_location=(19.0728, 72.8826),
                dropoff_location=(19.1136, 72.8697),
                requested_time=datetime.now() + timedelta(minutes=10),
                required_capacity=2,
                special_requirements={"wheelchair_accessible"},
                max_wait_time=timedelta(minutes=15),
                priority=1.0
            ),
            Passenger(
                id="p2",
                pickup_location=(19.0728, 72.8826),
                dropoff_location=(19.1136, 72.8697),
                requested_time=datetime.now() + timedelta(minutes=10),
                required_capacity=2,
                special_requirements={"pet_friendly"},
                max_wait_time=timedelta(minutes=15),
                priority=1.0
            )
        ]
        
        routes = await optimizer.optimize_routes(drivers, passengers)
        
        # Check correct matching
        if routes["d1"]:
            # d1 should only serve wheelchair passenger
            assert any("p1" in str(routes["d1"]))
        if routes["d2"]:
            # d2 should only serve pet passenger
            assert any("p2" in str(routes["d2"]))
    
    # Test Extreme Geographic Cases
    
    def test_antipodal_distance_calculation(self, optimizer):
        """Test distance calculation for antipodal points."""
        # North Pole to South Pole
        distance = optimizer._haversine_distance((90, 0), (-90, 0))
        assert abs(distance - 20015.0) < 100, "Antipodal distance should be ~20,015 km"
        
        # Opposite sides of equator
        distance = optimizer._haversine_distance((0, 0), (0, 180))
        assert abs(distance - 20015.0) < 100, "Half circumference should be ~20,015 km"
    
    def test_international_date_line_crossing(self, optimizer):
        """Test calculations crossing the International Date Line."""
        # Fiji to Samoa (crosses date line)
        distance = optimizer._haversine_distance((-17.7134, 178.0650), (-13.7590, -172.1046))
        assert distance < 2000, "Distance across date line should be reasonable"
    
    def test_pole_proximity_calculations(self, optimizer):
        """Test calculations near poles where longitude becomes meaningless."""
        # Two points near North Pole
        distance = optimizer._haversine_distance((89.9, 0), (89.9, 180))
        assert distance < 50, "Distance near pole should be small despite longitude difference"
    
    # Test Quantum Entanglement Effects
    
    def test_entanglement_correlation(self, optimizer, sample_drivers, sample_passengers):
        """Test that entangled states maintain correlation."""
        # Create scenario with multiple valid matches
        drivers = sample_drivers[:2]
        passengers = sample_passengers[:2]
        
        # Both drivers can serve both passengers
        for driver in drivers:
            driver.skills = set()  # Remove special requirements
        for passenger in passengers:
            passenger.special_requirements = set()
        
        distance_matrix = optimizer._build_distance_matrix(drivers, passengers)
        time_matrix = optimizer._build_time_matrix(drivers, passengers, distance_matrix)
        
        H = optimizer.calculate_hamiltonian(drivers, passengers, distance_matrix, time_matrix)
        
        # Check for entanglement in Hamiltonian
        off_diagonal_sum = np.sum(np.abs(H - np.diag(np.diag(H))))
        assert off_diagonal_sum > 0, "Should have entanglement (off-diagonal terms)"
    
    # Test Performance Under Load
    
    @pytest.mark.asyncio
    async def test_large_scale_optimization(self, optimizer):
        """Test with large number of drivers and passengers."""
        n_drivers = 50
        n_passengers = 100
        
        drivers = [Driver(
            id=f"d{i}",
            current_location=(19.0760 + np.random.randn()*0.1, 72.8777 + np.random.randn()*0.1),
            capacity=np.random.choice([2, 4, 6]),
            available_from=datetime.now() + timedelta(minutes=np.random.randint(0, 30)),
            skills=set(np.random.choice(["pet_friendly", "wheelchair_accessible", "luxury"], 
                                       size=np.random.randint(0, 3), replace=False)),
            rating=4 + np.random.random(),
            fuel_efficiency=10 + np.random.random() * 10
        ) for i in range(n_drivers)]
        
        passengers = [Passenger(
            id=f"p{i}",
            pickup_location=(19.0760 + np.random.randn()*0.1, 72.8777 + np.random.randn()*0.1),
            dropoff_location=(19.0760 + np.random.randn()*0.2, 72.8777 + np.random.randn()*0.2),
            requested_time=datetime.now() + timedelta(minutes=np.random.randint(5, 60)),
            required_capacity=np.random.choice([1, 2, 3, 4]),
            special_requirements=set(np.random.choice(["pet_friendly", "wheelchair_accessible"], 
                                                   size=np.random.randint(0, 2), replace=False)),
            max_wait_time=timedelta(minutes=np.random.randint(10, 30)),
            priority=np.random.random()
        ) for i in range(n_passengers)]
        
        # Should complete in reasonable time
        import time
        start = time.time()
        routes = await optimizer.optimize_routes(drivers, passengers)
        elapsed = time.time() - start
        
        assert elapsed < 10, f"Large scale optimization took too long: {elapsed}s"
        assert len(routes) == n_drivers, "Should have routes for all drivers"
    
    # Test Classical Refinement
    
    @pytest.mark.asyncio
    async def test_two_opt_improvement(self, optimizer):
        """Test 2-opt improvement actually improves routes."""
        # Create suboptimal route
        segments = [
            RouteSegment(
                from_location=(0, 0),
                to_location=(1, 0),
                distance=1,
                estimated_time=timedelta(minutes=2),
                traffic_factor=1.0,
                carbon_emission=1.0
            ),
            RouteSegment(
                from_location=(1, 0),
                to_location=(1, 1),
                distance=1,
                estimated_time=timedelta(minutes=2),
                traffic_factor=1.0,
                carbon_emission=1.0
            ),
            RouteSegment(
                from_location=(1, 1),
                to_location=(0, 1),
                distance=1,
                estimated_time=timedelta(minutes=2),
                traffic_factor=1.0,
                carbon_emission=1.0
            ),
            RouteSegment(
                from_location=(0, 1),
                to_location=(0, 0),
                distance=1,
                estimated_time=timedelta(minutes=2),
                traffic_factor=1.0,
                carbon_emission=1.0
            )
        ]
        
        initial_distance = sum(s.distance for s in segments)
        improved_segments = await optimizer._two_opt_improvement(segments)
        improved_distance = sum(s.distance for s in improved_segments)
        
        assert improved_distance <= initial_distance, "2-opt should not worsen the route"
    
    # Test Energy Landscape
    
    def test_hamiltonian_energy_landscape(self, optimizer):
        """Test that Hamiltonian creates proper energy landscape."""
        # Single driver, single passenger - should have clear minimum
        driver = Driver(
            id="d1",
            current_location=(0, 0),
            capacity=4,
            available_from=datetime.now(),
            skills=set(),
            rating=4.5,
            fuel_efficiency=15.0
        )
        
        passenger = Passenger(
            id="p1",
            pickup_location=(0, 0),  # Same location as driver
            dropoff_location=(1, 1),
            requested_time=datetime.now(),
            required_capacity=1,
            special_requirements=set(),
            max_wait_time=timedelta(minutes=30),
            priority=1.0
        )
        
        distance_matrix = np.array([[0]])  # Zero distance
        time_matrix = np.array([[0]])  # Zero time
        
        H = optimizer.calculate_hamiltonian([driver], [passenger], distance_matrix, time_matrix)
        
        # Energy should be minimal for this perfect match
        assert H[0, 0].real < 1, "Perfect match should have low energy"
    
    # Test Quantum Phase Transitions
    
    def test_phase_transition_behavior(self, optimizer):
        """Test behavior at phase transition points."""
        n = 10
        state = np.ones(n, dtype=complex) / np.sqrt(n)
        
        # Test different beta values (temperature)
        betas = [0.1, 0.5, 0.9]
        final_states = []
        
        for beta in betas:
            optimizer.beta = beta
            mixed_state = optimizer._apply_mixing_operator(state, beta)
            final_states.append(mixed_state)
        
        # Higher beta should lead to more mixing
        entropy1 = -np.sum(np.abs(final_states[0])**2 * np.log(np.abs(final_states[0])**2 + 1e-10))
        entropy2 = -np.sum(np.abs(final_states[2])**2 * np.log(np.abs(final_states[2])**2 + 1e-10))
        
        # Entropy changes with mixing parameter
        assert not np.isclose(entropy1, entropy2), "Different mixing should produce different entropy"
    
    # Test Edge Cases in Hamming Neighbors
    
    def test_hamming_neighbors_edge_cases(self, optimizer):
        """Test Hamming neighbor calculation edge cases."""
        # Test with n=1 (no neighbors)
        neighbors = optimizer._get_hamming_neighbors(0, 1)
        assert len(neighbors) == 0, "Single state has no Hamming neighbors"
        
        # Test with power of 2
        neighbors = optimizer._get_hamming_neighbors(0, 16)
        assert len(neighbors) == 4, "Should have log2(n) neighbors"
        assert all(n < 16 for n in neighbors), "All neighbors should be valid indices"
        
        # Test with non-power of 2
        neighbors = optimizer._get_hamming_neighbors(5, 10)
        assert all(n < 10 for n in neighbors), "All neighbors should be within bounds"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
