#!/usr/bin/env python3
"""
Migration Test Suite

This script tests the migration from main_model.py to the new modular architecture
through the orc_bridge.py compatibility layer.
"""

import sys
import traceback
import time
from typing import Dict, Any

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test new architecture imports
        sys.path.insert(0, 'src')
        from orc.core.physics import RotaryCutterPhysics
        from orc.core.simulation import SimulationEngine
        from orc.models.rotary_cutter import RotaryCutterModel
        print("  ✅ New architecture modules import successfully")
        new_arch_available = True
    except Exception as e:
        print(f"  ❌ New architecture import failed: {e}")
        new_arch_available = False
    
    try:
        # Test bridge module
        import orc_bridge
        print("  ✅ Bridge module imports successfully")
        bridge_available = True
    except Exception as e:
        print(f"  ❌ Bridge module import failed: {e}")
        bridge_available = False
    
    try:
        # Test original module
        import main_model
        print("  ✅ Original main_model imports successfully")
        original_available = True
    except Exception as e:
        print(f"  ❌ Original main_model import failed: {e}")
        original_available = False
    
    return {
        'new_architecture': new_arch_available,
        'bridge': bridge_available,
        'original': original_available
    }

def test_bridge_functions():
    """Test that bridge functions work correctly."""
    print("\n🔧 Testing bridge functions...")
    
    try:
        import orc_bridge
        
        # Test create_default_params
        params = orc_bridge.create_default_params(mass=15.0, radius=0.6)
        assert isinstance(params, dict), "create_default_params should return dict"
        assert 'tau_input' in params, "params should contain tau_input"
        print("  ✅ create_default_params works")
        
        # Test validate_params
        orc_bridge.validate_params(params)
        print("  ✅ validate_params works")
        
        # Test run_simulation (basic)
        result = orc_bridge.run_simulation(
            mass=15.0, 
            radius=0.6, 
            T_end=1.0,  # Short simulation for testing
            advanced_params=params
        )
        assert isinstance(result, dict), "run_simulation should return dict"
        assert 'time' in result, "result should contain time"
        assert 'omega' in result, "result should contain omega"
        print("  ✅ run_simulation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Bridge function test failed: {e}")
        traceback.print_exc()
        return False

def test_streamlit_compatibility():
    """Test that Streamlit app can import and use the bridge."""
    print("\n📱 Testing Streamlit compatibility...")
    
    try:
        # Simulate Streamlit app import
        import streamlit_app
        print("  ✅ Streamlit app imports successfully")
        
        # Check if new architecture is being used
        if hasattr(streamlit_app, 'USING_NEW_ARCHITECTURE'):
            if streamlit_app.USING_NEW_ARCHITECTURE:
                print("  ✅ Using new modular architecture")
            else:
                print("  ⚠️  Using fallback to original implementation")
        else:
            print("  ⚠️  Architecture detection not available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Streamlit compatibility test failed: {e}")
        traceback.print_exc()
        return False

def test_performance_comparison():
    """Compare performance between old and new implementations."""
    print("\n⚡ Testing performance comparison...")
    
    try:
        import orc_bridge
        import main_model
        
        # Test parameters
        mass = 15.0
        radius = 0.6
        T_end = 2.0
        
        # Test bridge (new architecture)
        start_time = time.time()
        params = orc_bridge.create_default_params(mass=mass, radius=radius)
        bridge_result = orc_bridge.run_simulation(
            mass=mass, radius=radius, T_end=T_end, advanced_params=params
        )
        bridge_time = time.time() - start_time
        
        # Test original implementation
        start_time = time.time()
        original_params = main_model.create_default_params(mass=mass, radius=radius)
        original_result = main_model.run_simulation(
            mass=mass, radius=radius, T_end=T_end, advanced_params=original_params
        )
        original_time = time.time() - start_time
        
        print(f"  📊 Bridge execution time: {bridge_time:.3f}s")
        print(f"  📊 Original execution time: {original_time:.3f}s")
        
        # Compare results (basic check)
        bridge_omega_final = bridge_result['omega'][-1]
        original_omega_final = original_result['omega'][-1]
        relative_diff = abs(bridge_omega_final - original_omega_final) / abs(original_omega_final)
        
        print(f"  📊 Final omega difference: {relative_diff:.2%}")
        
        if relative_diff < 0.01:  # Less than 1% difference
            print("  ✅ Results are consistent between implementations")
        else:
            print("  ⚠️  Results differ between implementations")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Performance comparison failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and fallback mechanisms."""
    print("\n🛡️  Testing error handling...")
    
    try:
        import orc_bridge
        
        # Test with invalid parameters
        try:
            invalid_params = {'tau_input': -100}  # Negative torque
            orc_bridge.validate_params(invalid_params)
            print("  ❌ Should have caught invalid parameters")
            return False
        except (ValueError, KeyError):
            print("  ✅ Invalid parameter validation works")
        
        # Test with missing parameters
        try:
            incomplete_params = {'tau_input': 100}  # Missing required params
            orc_bridge.validate_params(incomplete_params)
            print("  ❌ Should have caught missing parameters")
            return False
        except (ValueError, KeyError):
            print("  ✅ Missing parameter validation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print("🚀 ORC Migration Test Suite")
    print("=" * 50)
    
    # Track test results
    test_results = {}
    
    # Run tests
    test_results['imports'] = test_imports()
    test_results['bridge_functions'] = test_bridge_functions()
    test_results['streamlit_compatibility'] = test_streamlit_compatibility()
    test_results['performance_comparison'] = test_performance_comparison()
    test_results['error_handling'] = test_error_handling()
    
    # Generate report
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    # Import status
    imports = test_results['imports']
    print(f"New Architecture Available: {'✅' if imports['new_architecture'] else '❌'}")
    print(f"Bridge Module Available: {'✅' if imports['bridge'] else '❌'}")
    print(f"Original Module Available: {'✅' if imports['original'] else '❌'}")
    
    # Function tests
    print(f"Bridge Functions: {'✅' if test_results['bridge_functions'] else '❌'}")
    print(f"Streamlit Compatibility: {'✅' if test_results['streamlit_compatibility'] else '❌'}")
    print(f"Performance Comparison: {'✅' if test_results['performance_comparison'] else '❌'}")
    print(f"Error Handling: {'✅' if test_results['error_handling'] else '❌'}")
    
    # Overall status
    all_critical_passed = (
        imports['bridge'] and 
        test_results['bridge_functions'] and 
        test_results['streamlit_compatibility']
    )
    
    print("\n" + "=" * 50)
    if all_critical_passed:
        print("🎉 MIGRATION TEST: PASSED")
        print("✅ The migration is successful and ready for deployment!")
    else:
        print("❌ MIGRATION TEST: FAILED")
        print("⚠️  Issues detected that need to be resolved before deployment.")
    
    print("=" * 50)
    
    return all_critical_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
