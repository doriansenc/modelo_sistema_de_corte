#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    import streamlit as st
    print("✓ Streamlit imported successfully")
    
    import numpy as np
    print("✓ NumPy imported successfully")
    
    import pandas as pd
    print("✓ Pandas imported successfully")
    
    import plotly.graph_objects as go
    print("✓ Plotly imported successfully")
    
    import matplotlib.pyplot as plt
    print("✓ Matplotlib imported successfully")
    
    from scipy.integrate import solve_ivp
    print("✓ SciPy imported successfully")
    
    # Test main_model imports
    try:
        from main_model import run_simulation, create_default_params
        print("✓ main_model basic functions imported successfully")
    except ImportError as e:
        print(f"✗ Error importing from main_model: {e}")
    
    # Test if streamlit_app can be imported
    try:
        import streamlit_app
        print("✓ streamlit_app module can be imported")
    except Exception as e:
        print(f"✗ Error importing streamlit_app: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nAll imports completed!")
    
except Exception as e:
    print(f"Error during import testing: {e}")
    import traceback
    traceback.print_exc()
