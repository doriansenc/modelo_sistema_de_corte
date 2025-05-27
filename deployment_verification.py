#!/usr/bin/env python3
"""
Deployment Verification Script

This script verifies that the ORC system is ready for deployment
with the new modular architecture and backward compatibility.
"""

import sys
import os
import time
import traceback
from pathlib import Path

def check_file_structure():
    """Verify that all required files are present."""
    print("📁 Checking file structure...")
    
    required_files = [
        'streamlit_app.py',
        'main_model.py',
        'orc_bridge.py',
        'requirements.txt',
        'MIGRATION_GUIDE.md'
    ]
    
    required_dirs = [
        'src/orc',
        'src/orc/core',
        'src/orc/models',
        'src/orc/analysis',
        'src/orc/config'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"  ✅ {file}")
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}/")
    
    if missing_files or missing_dirs:
        print(f"  ❌ Missing files: {missing_files}")
        print(f"  ❌ Missing directories: {missing_dirs}")
        return False
    
    print("  ✅ All required files and directories present")
    return True

def check_imports():
    """Verify that all imports work correctly."""
    print("\n🔍 Checking imports...")
    
    try:
        # Test Streamlit app import
        import streamlit_app
        print("  ✅ streamlit_app.py imports successfully")
        
        # Check architecture detection
        if hasattr(streamlit_app, 'USING_NEW_ARCHITECTURE'):
            arch_status = "new modular" if streamlit_app.USING_NEW_ARCHITECTURE else "original fallback"
            print(f"  ✅ Architecture: {arch_status}")
        
        # Test bridge import
        import orc_bridge
        print("  ✅ orc_bridge.py imports successfully")
        
        # Test original model import
        import main_model
        print("  ✅ main_model.py imports successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def check_api_compatibility():
    """Verify API compatibility between old and new implementations."""
    print("\n🔧 Checking API compatibility...")
    
    try:
        import orc_bridge
        import main_model
        
        # Test parameter creation
        bridge_params = orc_bridge.create_default_params(mass=15.0, radius=0.6)
        original_params = main_model.create_default_params(mass=15.0, radius=0.6)
        
        # Check that both return dictionaries with required keys
        required_keys = ['tau_input', 'R', 'm_c', 'I_plate']
        
        for key in required_keys:
            if key not in bridge_params:
                print(f"  ❌ Bridge missing key: {key}")
                return False
            if key not in original_params:
                print(f"  ❌ Original missing key: {key}")
                return False
        
        print("  ✅ Parameter creation API compatible")
        
        # Test validation
        orc_bridge.validate_params(bridge_params)
        main_model.validate_params(original_params)
        print("  ✅ Parameter validation API compatible")
        
        # Test simulation (quick test)
        bridge_result = orc_bridge.run_simulation(
            mass=15.0, radius=0.6, T_end=0.5, advanced_params=bridge_params
        )
        original_result = main_model.run_simulation(
            mass=15.0, radius=0.6, T_end=0.5, advanced_params=original_params
        )
        
        # Check result structure
        required_result_keys = ['time', 'omega', 'theta', 'torque']
        for key in required_result_keys:
            if key not in bridge_result:
                print(f"  ❌ Bridge result missing key: {key}")
                return False
            if key not in original_result:
                print(f"  ❌ Original result missing key: {key}")
                return False
        
        print("  ✅ Simulation API compatible")
        return True
        
    except Exception as e:
        print(f"  ❌ API compatibility check failed: {e}")
        traceback.print_exc()
        return False

def check_streamlit_cloud_compatibility():
    """Check Streamlit Cloud deployment compatibility."""
    print("\n☁️  Checking Streamlit Cloud compatibility...")
    
    # Check entry point
    if not Path('streamlit_app.py').exists():
        print("  ❌ streamlit_app.py not found (required entry point)")
        return False
    print("  ✅ streamlit_app.py exists as entry point")
    
    # Check requirements.txt
    if not Path('requirements.txt').exists():
        print("  ❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    required_packages = ['streamlit', 'pandas', 'numpy', 'scipy', 'plotly']
    for package in required_packages:
        if package not in requirements:
            print(f"  ❌ Missing required package: {package}")
            return False
    
    print("  ✅ requirements.txt contains required packages")
    
    # Check for optional dependencies
    optional_packages = ['pyyaml', 'python-dotenv']
    for package in optional_packages:
        if package in requirements:
            print(f"  ✅ Optional package included: {package}")
        else:
            print(f"  ⚠️  Optional package not included: {package}")
    
    # Check graceful fallback
    try:
        import streamlit_app
        print("  ✅ Streamlit app imports without errors")
        return True
    except Exception as e:
        print(f"  ❌ Streamlit app import failed: {e}")
        return False

def check_performance():
    """Basic performance check."""
    print("\n⚡ Checking performance...")
    
    try:
        import orc_bridge
        
        # Time a simulation
        start_time = time.time()
        params = orc_bridge.create_default_params(mass=15.0, radius=0.6)
        result = orc_bridge.run_simulation(
            mass=15.0, radius=0.6, T_end=2.0, advanced_params=params
        )
        execution_time = time.time() - start_time
        
        print(f"  📊 Simulation execution time: {execution_time:.3f}s")
        
        if execution_time > 10.0:
            print("  ⚠️  Simulation seems slow (>10s)")
        else:
            print("  ✅ Simulation performance acceptable")
        
        # Check result quality
        if len(result['time']) > 0 and len(result['omega']) > 0:
            print("  ✅ Simulation produces valid results")
            return True
        else:
            print("  ❌ Simulation produces empty results")
            return False
            
    except Exception as e:
        print(f"  ❌ Performance check failed: {e}")
        return False

def generate_deployment_report():
    """Generate a comprehensive deployment report."""
    print("\n" + "=" * 60)
    print("🚀 DEPLOYMENT VERIFICATION REPORT")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Imports", check_imports),
        ("API Compatibility", check_api_compatibility),
        ("Streamlit Cloud Compatibility", check_streamlit_cloud_compatibility),
        ("Performance", check_performance)
    ]
    
    results = {}
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
            if not results[check_name]:
                all_passed = False
        except Exception as e:
            print(f"\n❌ {check_name} check crashed: {e}")
            results[check_name] = False
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All checks passed. The system is ready for deployment.")
        print("\nNext steps:")
        print("1. Commit all changes to your repository")
        print("2. Push to your Streamlit Cloud connected repository")
        print("3. Streamlit Cloud will automatically deploy the new version")
        print("4. The application will use the new architecture with fallback safety")
    else:
        print("❌ DEPLOYMENT NOT READY")
        print("⚠️  Some checks failed. Please resolve issues before deployment.")
        print("\nRecommendations:")
        print("1. Review failed checks above")
        print("2. Fix any missing files or import errors")
        print("3. Re-run this verification script")
        print("4. Only deploy when all checks pass")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    print("🔍 ORC Deployment Verification")
    print("Verifying system readiness for Streamlit Cloud deployment...")
    print()
    
    success = generate_deployment_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
