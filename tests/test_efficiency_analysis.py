#!/usr/bin/env python3
"""
Test script for the new efficiency analysis functionality
"""

import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from main_model import run_simulation, create_default_params

def test_efficiency_analysis():
    """Test the new efficiency analysis features"""
    
    print("=== TESTING EFFICIENCY ANALYSIS FUNCTIONALITY ===")
    print()
    
    # Test parameters
    mass = 15.0  # kg
    radius = 0.6  # m
    omega = 50.0  # rad/s
    
    print("1. Testing basic simulation with new metrics...")
    
    try:
        # Run a basic simulation
        results = run_simulation(
            mass=mass, 
            radius=radius, 
            omega=omega, 
            T_end=3.0, 
            dt=0.01
        )
        
        print("✅ Basic simulation completed successfully")
        
        # Check if advanced metrics are present
        if 'advanced_metrics' in results:
            print("✅ Advanced metrics found")
            
            adv_metrics = results['advanced_metrics']
            
            # Check for new efficiency metrics
            required_metrics = [
                'efficiency_instantaneous',
                'efficiency_average', 
                'E_losses',
                'power_total_series',
                'power_util_series',
                'time_series',
                'efficiency_peak',
                'efficiency_min',
                'high_efficiency_time_percent',
                'medium_efficiency_time_percent',
                'low_efficiency_time_percent'
            ]
            
            missing_metrics = []
            for metric in required_metrics:
                if metric not in adv_metrics:
                    missing_metrics.append(metric)
            
            if missing_metrics:
                print(f"❌ Missing metrics: {missing_metrics}")
                return False
            else:
                print("✅ All required efficiency metrics present")
            
            # Display some key metrics
            print(f"\n📊 Key Efficiency Metrics:")
            print(f"   Average Efficiency: {adv_metrics['efficiency_average']:.1f}%")
            print(f"   Peak Efficiency: {adv_metrics['efficiency_peak']:.1f}%")
            print(f"   Min Efficiency: {adv_metrics['efficiency_min']:.1f}%")
            print(f"   High Efficiency Time: {adv_metrics['high_efficiency_time_percent']:.1f}%")
            print(f"   Total Energy: {adv_metrics['E_total']:.1f} J")
            print(f"   Useful Energy: {adv_metrics['E_util']:.1f} J")
            print(f"   Energy Losses: {adv_metrics['E_losses']:.1f} J")
            
            # Verify data consistency
            if len(adv_metrics['time_series']) == len(adv_metrics['efficiency_instantaneous']):
                print("✅ Time series data consistency verified")
            else:
                print("❌ Time series data inconsistency detected")
                return False
            
            # Test with variable torque
            print("\n2. Testing with variable torque...")
            
            from main_model import tau_grass_sinusoidal, create_validated_params
            
            base_params = create_default_params(mass, radius, 200.0)
            tau_func = tau_grass_sinusoidal(amplitude=20.0, frequency=0.5, offset=25.0)
            
            variable_params = create_validated_params(
                base_params,
                tau_grass_func=tau_func
            )
            
            results_var = run_simulation(
                mass=mass,
                radius=radius, 
                omega=omega,
                T_end=3.0,
                dt=0.01,
                advanced_params=variable_params
            )
            
            if 'advanced_metrics' in results_var:
                adv_var = results_var['advanced_metrics']
                print(f"✅ Variable torque simulation completed")
                print(f"   Variable Torque Avg Efficiency: {adv_var['efficiency_average']:.1f}%")
                print(f"   Efficiency Range: {adv_var['efficiency_peak'] - adv_var['efficiency_min']:.1f}%")
            else:
                print("❌ Variable torque simulation failed")
                return False
            
            print("\n3. Testing efficiency analysis functions...")
            
            # Test the recommendation function
            try:
                # Import the function from streamlit_app
                from streamlit_app import generate_efficiency_recommendations
                
                recommendations = generate_efficiency_recommendations(adv_metrics)
                print(f"✅ Recommendations generated: {len(recommendations)} items")
                
                for rec_type, rec_text in recommendations.items():
                    print(f"   {rec_type}: {rec_text[:50]}...")
                
            except ImportError as e:
                print(f"⚠️  Could not test recommendations function: {e}")
            
            print("\n🎉 ALL TESTS PASSED!")
            print("The efficiency analysis functionality is working correctly.")
            return True
            
        else:
            print("❌ Advanced metrics not found in results")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_efficiency_analysis()
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
