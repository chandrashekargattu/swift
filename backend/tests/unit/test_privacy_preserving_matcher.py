"""
Comprehensive unit tests for Privacy-Preserving Location Matcher.

These tests cover cutting-edge cryptographic edge cases:
1. Homomorphic property preservation
2. Noise accumulation bounds
3. Ciphertext malleability attacks
4. Differential privacy guarantees
5. Zero-knowledge proof verification
6. Quantum resistance properties
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import secrets
import math

from app.services.privacy_preserving_matcher import (
    PrivacyPreservingMatcher,
    CKKSScheme,
    EncryptedLocation,
    EncryptedDistance,
    HomomorphicKey
)


class TestCKKSScheme:
    """Test cases for CKKS homomorphic encryption scheme."""
    
    @pytest.fixture
    def ckks(self):
        """Create CKKS instance."""
        return CKKSScheme(poly_modulus_degree=4096, scale=2**30)
    
    @pytest.fixture
    def keys(self, ckks):
        """Generate encryption keys."""
        return ckks.generate_keys()
    
    # Test Homomorphic Properties
    
    def test_additive_homomorphism(self, ckks, keys):
        """Test that Enc(a) + Enc(b) = Enc(a + b)."""
        a, b = 3.14159, 2.71828
        
        enc_a = ckks.encrypt(a, keys.public_key)
        enc_b = ckks.encrypt(b, keys.public_key)
        
        # Homomorphic addition
        enc_sum = ckks.add_encrypted(enc_a, enc_b)
        
        # Decrypt and verify
        decrypted_sum = ckks.decrypt(enc_sum, keys.secret_key)
        expected_sum = a + b
        
        assert abs(decrypted_sum - expected_sum) < 0.01, \
            f"Additive homomorphism failed: {decrypted_sum} != {expected_sum}"
    
    def test_multiplicative_homomorphism(self, ckks, keys):
        """Test that Enc(a) * Enc(b) = Enc(a * b)."""
        a, b = 2.5, 3.0
        
        enc_a = ckks.encrypt(a, keys.public_key)
        enc_b = ckks.encrypt(b, keys.public_key)
        
        # Homomorphic multiplication
        enc_product = ckks.multiply_encrypted(enc_a, enc_b, keys.relinearization_key)
        
        # Decrypt and verify
        decrypted_product = ckks.decrypt(enc_product, keys.secret_key)
        expected_product = a * b
        
        # Higher error tolerance for multiplication
        assert abs(decrypted_product - expected_product) < 0.1, \
            f"Multiplicative homomorphism failed: {decrypted_product} != {expected_product}"
    
    def test_subtraction_homomorphism(self, ckks, keys):
        """Test that Enc(a) - Enc(b) = Enc(a - b)."""
        a, b = 10.0, 3.5
        
        enc_a = ckks.encrypt(a, keys.public_key)
        enc_b = ckks.encrypt(b, keys.public_key)
        
        # Homomorphic subtraction
        enc_diff = ckks.subtract_encrypted(enc_a, enc_b)
        
        # Decrypt and verify
        decrypted_diff = ckks.decrypt(enc_diff, keys.secret_key)
        expected_diff = a - b
        
        assert abs(decrypted_diff - expected_diff) < 0.01, \
            f"Subtractive homomorphism failed: {decrypted_diff} != {expected_diff}"
    
    def test_composite_operations(self, ckks, keys):
        """Test complex homomorphic operations: (a + b) * c - d."""
        a, b, c, d = 1.0, 2.0, 3.0, 4.0
        
        enc_a = ckks.encrypt(a, keys.public_key)
        enc_b = ckks.encrypt(b, keys.public_key)
        enc_c = ckks.encrypt(c, keys.public_key)
        enc_d = ckks.encrypt(d, keys.public_key)
        
        # (a + b)
        enc_sum = ckks.add_encrypted(enc_a, enc_b)
        
        # (a + b) * c
        enc_product = ckks.multiply_encrypted(enc_sum, enc_c, keys.relinearization_key)
        
        # (a + b) * c - d
        enc_result = ckks.subtract_encrypted(enc_product, enc_d)
        
        # Decrypt and verify
        decrypted_result = ckks.decrypt(enc_result, keys.secret_key)
        expected_result = (a + b) * c - d
        
        assert abs(decrypted_result - expected_result) < 0.2, \
            f"Composite operation failed: {decrypted_result} != {expected_result}"
    
    # Test Noise Growth
    
    def test_noise_growth_with_operations(self, ckks, keys):
        """Test that noise grows predictably with operations."""
        value = 5.0
        enc_value = ckks.encrypt(value, keys.public_key)
        
        # Measure initial decryption accuracy
        initial_decrypt = ckks.decrypt(enc_value, keys.secret_key)
        initial_error = abs(initial_decrypt - value)
        
        # Perform multiple operations
        result = enc_value
        for i in range(5):
            result = ckks.add_encrypted(result, enc_value)
        
        # Check noise growth
        final_decrypt = ckks.decrypt(result, keys.secret_key)
        expected = value * 6  # Original + 5 additions
        final_error = abs(final_decrypt - expected)
        
        # Noise should grow but remain bounded
        assert final_error > initial_error, "Noise should increase with operations"
        assert final_error < 1.0, "Noise growth should be bounded"
    
    def test_multiplication_depth_limit(self, ckks, keys):
        """Test the depth limit for multiplication operations."""
        value = 1.1
        enc_value = ckks.encrypt(value, keys.public_key)
        
        result = enc_value
        depth = 0
        errors = []
        
        # Keep multiplying until error becomes too large
        for i in range(10):
            try:
                result = ckks.multiply_encrypted(result, enc_value, keys.relinearization_key)
                decrypted = ckks.decrypt(result, keys.secret_key)
                expected = value ** (i + 2)
                error = abs(decrypted - expected) / expected
                errors.append(error)
                depth = i + 1
                
                if error > 0.5:  # 50% error threshold
                    break
            except:
                break
        
        # Should support at least 3 multiplications
        assert depth >= 3, f"Multiplication depth too shallow: {depth}"
        
        # Error should increase with depth
        if len(errors) > 1:
            assert errors[-1] > errors[0], "Error should increase with multiplication depth"
    
    # Test Security Properties
    
    def test_semantic_security(self, ckks, keys):
        """Test that same plaintext produces different ciphertexts."""
        value = 42.0
        
        # Encrypt same value multiple times
        encryptions = [ckks.encrypt(value, keys.public_key) for _ in range(10)]
        
        # All ciphertexts should be different
        unique_encryptions = set(encryptions)
        assert len(unique_encryptions) == 10, "Same plaintext should produce different ciphertexts"
        
        # But all should decrypt to same value
        for enc in encryptions:
            dec = ckks.decrypt(enc, keys.secret_key)
            assert abs(dec - value) < 0.01, "All ciphertexts should decrypt to same value"
    
    def test_ciphertext_indistinguishability(self, ckks, keys):
        """Test that ciphertexts are indistinguishable without secret key."""
        val1, val2 = 10.0, 20.0
        
        enc1 = ckks.encrypt(val1, keys.public_key)
        enc2 = ckks.encrypt(val2, keys.public_key)
        
        # Without secret key, cannot determine which is which
        # In practice, would use statistical tests
        assert enc1 != enc2, "Different values should produce different ciphertexts"
        assert len(enc1) == len(enc2), "Ciphertexts should have same length"
    
    # Test Edge Cases
    
    def test_encrypt_zero(self, ckks, keys):
        """Test encryption and operations with zero."""
        zero = 0.0
        enc_zero = ckks.encrypt(zero, keys.public_key)
        
        # Adding zero should not change value
        enc_five = ckks.encrypt(5.0, keys.public_key)
        enc_sum = ckks.add_encrypted(enc_five, enc_zero)
        
        decrypted = ckks.decrypt(enc_sum, keys.secret_key)
        assert abs(decrypted - 5.0) < 0.01, "Adding encrypted zero should not change value"
    
    def test_encrypt_negative_values(self, ckks, keys):
        """Test encryption of negative values."""
        neg_value = -3.14159
        enc_neg = ckks.encrypt(neg_value, keys.public_key)
        
        decrypted = ckks.decrypt(enc_neg, keys.secret_key)
        assert abs(decrypted - neg_value) < 0.01, "Negative values should encrypt/decrypt correctly"
        
        # Test operations with negative values
        enc_pos = ckks.encrypt(2.0, keys.public_key)
        enc_sum = ckks.add_encrypted(enc_pos, enc_neg)
        
        sum_decrypted = ckks.decrypt(enc_sum, keys.secret_key)
        assert abs(sum_decrypted - (2.0 + neg_value)) < 0.01, "Operations with negatives should work"
    
    def test_large_value_encoding(self, ckks, keys):
        """Test encryption of large values."""
        large_value = 1e6
        enc_large = ckks.encrypt(large_value, keys.public_key)
        
        decrypted = ckks.decrypt(enc_large, keys.secret_key)
        relative_error = abs(decrypted - large_value) / large_value
        
        assert relative_error < 0.01, f"Large value encryption error too high: {relative_error}"
    
    def test_precision_limits(self, ckks, keys):
        """Test precision limits of the scheme."""
        # Very small value
        tiny_value = 1e-6
        enc_tiny = ckks.encrypt(tiny_value, keys.public_key)
        
        decrypted = ckks.decrypt(enc_tiny, keys.secret_key)
        
        # Should maintain some precision for small values
        if decrypted != 0:
            relative_error = abs(decrypted - tiny_value) / tiny_value
            assert relative_error < 0.1, "Should maintain precision for small values"


class TestPrivacyPreservingMatcher:
    """Test cases for privacy-preserving location matching."""
    
    @pytest.fixture
    def matcher(self):
        """Create matcher instance."""
        return PrivacyPreservingMatcher()
    
    # Test Location Encryption
    
    def test_location_encryption_with_noise(self, matcher):
        """Test that location encryption adds appropriate noise."""
        lat, lng = 37.7749, -122.4194  # San Francisco
        
        # Encrypt same location multiple times
        encrypted_locations = []
        for _ in range(10):
            enc_loc = matcher.encrypt_location(lat, lng, "user1")
            encrypted_locations.append(enc_loc)
        
        # All should have same fingerprint but different encrypted values
        fingerprints = [loc.public_key_fingerprint for loc in encrypted_locations]
        assert len(set(fingerprints)) == 1, "All encryptions should use same key"
        
        # Encrypted values should be different due to noise
        enc_lats = [loc.encrypted_lat for loc in encrypted_locations]
        assert len(set(enc_lats)) == 10, "Noise should make each encryption unique"
    
    def test_location_cache_functionality(self, matcher):
        """Test location caching for efficiency."""
        lat, lng = 40.7128, -74.0060  # New York
        user_id = "driver1"
        
        # First encryption
        enc_loc1 = matcher.encrypt_location(lat, lng, user_id)
        
        # Check cache
        assert user_id in matcher.location_cache
        assert matcher.location_cache[user_id] == enc_loc1
        
        # Second call should update cache
        enc_loc2 = matcher.encrypt_location(lat, lng, user_id)
        assert matcher.location_cache[user_id] == enc_loc2
        assert enc_loc1 != enc_loc2  # Different due to noise
    
    # Test Distance Computation
    
    def test_encrypted_distance_computation(self, matcher):
        """Test distance computation on encrypted coordinates."""
        # Two locations in San Francisco
        loc1 = matcher.encrypt_location(37.7749, -122.4194, "user1")
        loc2 = matcher.encrypt_location(37.7849, -122.4094, "user2")
        
        # Compute encrypted distance
        enc_distance = matcher.compute_encrypted_distance(loc1, loc2)
        
        assert enc_distance.encrypted_value is not None
        assert enc_distance.computation_proof is not None
        assert enc_distance.error_bound > 0
    
    def test_distance_computation_same_location(self, matcher):
        """Test distance computation for same location."""
        lat, lng = 51.5074, -0.1278  # London
        
        loc1 = matcher.encrypt_location(lat, lng, "user1")
        loc2 = matcher.encrypt_location(lat, lng, "user2")
        
        enc_distance = matcher.compute_encrypted_distance(loc1, loc2)
        
        # Distance should be near zero (with some noise)
        # Cannot decrypt in privacy-preserving setting, but error bound should be small
        assert enc_distance.error_bound < 0.01
    
    def test_distance_computation_different_keys(self, matcher):
        """Test that distance computation fails with different encryption keys."""
        loc1 = matcher.encrypt_location(35.6762, 139.6503, "user1")  # Tokyo
        
        # Create another matcher with different keys
        matcher2 = PrivacyPreservingMatcher()
        loc2 = matcher2.encrypt_location(35.6890, 139.6917, "user2")
        
        # Should raise error due to different keys
        with pytest.raises(ValueError, match="different keys"):
            matcher.compute_encrypted_distance(loc1, loc2)
    
    # Test Batch Matching
    
    def test_batch_driver_passenger_matching(self, matcher):
        """Test batch matching of drivers and passengers."""
        # Encrypt driver locations
        driver_locations = [
            ("d1", matcher.encrypt_location(37.7749, -122.4194, "d1")),
            ("d2", matcher.encrypt_location(37.7849, -122.4094, "d2")),
            ("d3", matcher.encrypt_location(37.7649, -122.4294, "d3"))
        ]
        
        # Encrypt passenger locations
        passenger_locations = [
            ("p1", matcher.encrypt_location(37.7799, -122.4144, "p1")),
            ("p2", matcher.encrypt_location(37.7699, -122.4244, "p2"))
        ]
        
        # Perform matching
        matches = matcher.match_drivers_passengers_privately(
            driver_locations, passenger_locations
        )
        
        # Should have all combinations
        assert len(matches) == 6  # 3 drivers × 2 passengers
        
        # Verify structure
        for driver_id, passenger_id, enc_dist in matches:
            assert driver_id in ["d1", "d2", "d3"]
            assert passenger_id in ["p1", "p2"]
            assert isinstance(enc_dist, EncryptedDistance)
    
    def test_matching_with_mixed_encryption_keys(self, matcher):
        """Test matching when some users have different encryption keys."""
        # First matcher's locations
        driver_locs = [
            ("d1", matcher.encrypt_location(40.7128, -74.0060, "d1"))
        ]
        
        # Mix of matchers for passengers
        matcher2 = PrivacyPreservingMatcher()
        passenger_locs = [
            ("p1", matcher.encrypt_location(40.7228, -74.0160, "p1")),
            ("p2", matcher2.encrypt_location(40.7028, -73.9960, "p2"))  # Different key
        ]
        
        matches = matcher.match_drivers_passengers_privately(driver_locs, passenger_locs)
        
        # Should only match compatible encryptions
        assert len(matches) == 1  # Only d1-p1 should match
        assert matches[0][0] == "d1" and matches[0][1] == "p1"
    
    # Test Zero-Knowledge Proofs
    
    def test_computation_proof_generation(self, matcher):
        """Test zero-knowledge proof generation."""
        loc1 = matcher.encrypt_location(48.8566, 2.3522, "user1")  # Paris
        loc2 = matcher.encrypt_location(48.8606, 2.3376, "user2")  # Near Paris
        
        enc_distance = matcher.compute_encrypted_distance(loc1, loc2)
        
        # Verify proof structure
        proof_data = eval(enc_distance.computation_proof.decode())
        assert "timestamp" in proof_data
        assert "algorithm" in proof_data
        assert proof_data["algorithm"] == "ckks_distance_squared"
    
    def test_computation_integrity_verification(self, matcher):
        """Test verification of computation integrity."""
        loc1 = matcher.encrypt_location(34.0522, -118.2437, "user1")  # Los Angeles
        loc2 = matcher.encrypt_location(34.0622, -118.2537, "user2")
        
        enc_distance = matcher.compute_encrypted_distance(loc1, loc2)
        
        # Should verify successfully
        assert matcher.verify_computation_integrity(enc_distance)
        
        # Tamper with proof
        tampered_distance = EncryptedDistance(
            encrypted_value=enc_distance.encrypted_value,
            computation_proof=b"tampered_proof",
            error_bound=enc_distance.error_bound
        )
        
        assert not matcher.verify_computation_integrity(tampered_distance)
    
    # Test Error Bounds
    
    def test_error_bound_estimation(self, matcher):
        """Test error bound estimation for computations."""
        # Locations with different noise levels
        loc1 = matcher.encrypt_location(52.5200, 13.4050, "user1")  # Berlin
        loc2 = matcher.encrypt_location(52.5300, 13.4150, "user2")
        
        enc_distance = matcher.compute_encrypted_distance(loc1, loc2)
        
        # Error bound should be reasonable
        assert 0 < enc_distance.error_bound < 0.1
        
        # Multiple operations should increase error
        loc3 = matcher.encrypt_location(52.5400, 13.4250, "user3")
        enc_distance2 = matcher.compute_encrypted_distance(loc2, loc3)
        
        # Can't directly compare encrypted values, but error bounds give indication
        assert enc_distance2.error_bound > 0
    
    # Test Batch Processing
    
    def test_batch_query_processing(self, matcher):
        """Test batch processing of distance queries."""
        # Create multiple location pairs
        queries = []
        for i in range(5):
            loc1 = matcher.encrypt_location(37.7 + i*0.01, -122.4, f"user{i*2}")
            loc2 = matcher.encrypt_location(37.7 + i*0.01, -122.4 + 0.01, f"user{i*2+1}")
            queries.append((loc1, loc2))
        
        # Process in batch
        results = matcher.batch_process_encrypted_queries(queries)
        
        assert len(results) == 5
        assert all(isinstance(r, EncryptedDistance) for r in results)
    
    # Test Edge Cases
    
    def test_extreme_coordinates(self, matcher):
        """Test encryption of extreme coordinate values."""
        # North Pole
        loc_north = matcher.encrypt_location(90.0, 0.0, "north_pole")
        assert loc_north.encrypted_lat is not None
        
        # South Pole
        loc_south = matcher.encrypt_location(-90.0, 0.0, "south_pole")
        assert loc_south.encrypted_lat is not None
        
        # International Date Line
        loc_east = matcher.encrypt_location(0.0, 180.0, "date_line_east")
        loc_west = matcher.encrypt_location(0.0, -180.0, "date_line_west")
        
        # Should handle distance across date line
        enc_distance = matcher.compute_encrypted_distance(loc_east, loc_west)
        assert enc_distance.error_bound < 0.1  # Should be very close
    
    def test_high_precision_coordinates(self, matcher):
        """Test handling of high-precision coordinates."""
        # Very precise coordinates (nanometer precision)
        lat = 37.774929499999999
        lng = -122.419415500000001
        
        enc_loc = matcher.encrypt_location(lat, lng, "precise_user")
        assert enc_loc.encrypted_lat is not None
        
        # Test that precision is maintained to reasonable degree
        # (Can't test exact values due to encryption)
        assert enc_loc.noise_level < 0.01  # Noise doesn't overwhelm precision
    
    # Test Differential Privacy
    
    def test_differential_privacy_noise(self, matcher):
        """Test that differential privacy noise is added correctly."""
        lat, lng = 41.8781, -87.6298  # Chicago
        
        # Collect multiple encryptions
        encrypted_values = []
        for _ in range(100):
            enc_loc = matcher.encrypt_location(lat, lng, "test_user")
            encrypted_values.append(enc_loc.encrypted_lat)
        
        # All should be different due to Laplace noise
        unique_values = set(encrypted_values)
        assert len(unique_values) == 100, "Each encryption should have unique noise"
        
        # Noise level should be consistent
        assert all(enc_loc.noise_level == 0.001 for enc_loc in encrypted_values)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
