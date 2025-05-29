import streamlit as st

# Configuración de la página - DEBE SER EL PRIMER COMANDO DE STREAMLIT
st.set_page_config(
    page_title="ORC - Optimización de Rotary Cutter",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from datetime import datetime
import sys
import os

# Importar matplotlib con manejo de errores
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Backend no interactivo para Streamlit
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# Agregar el directorio src al path para importar el nuevo paquete orc
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importar funciones del modelo - usando bridge para compatibilidad
try:
    # Intentar importar desde la nueva estructura modular
    from orc_bridge import (
        run_simulation, create_default_params, create_validated_params,
        validate_params, analyze_performance, compute_metrics,
        # Funciones de torque temporal
        tau_grass_sinusoidal, tau_grass_step, tau_grass_ramp, tau_grass_exponential,
        # Funciones de torque espacial
        tau_grass_spatial_zones, tau_grass_spatial_gaussian_patches,
        tau_grass_spatial_sigmoid_transition, tau_grass_spatial_sinusoidal,
        tau_grass_spatial_complex_terrain,
        # Funciones de condiciones iniciales
        create_initial_conditions, initial_conditions_from_rpm,
        initial_conditions_blade_angle, initial_conditions_spinning,
        # Configuration Wrapper
        RotaryCutterConfig, ConfigurationManager
    )
    USING_NEW_ARCHITECTURE = True
except ImportError:
    # Fallback al modelo original
    from main_model import (
        run_simulation, create_default_params, create_validated_params,
        validate_params, analyze_performance, compute_metrics,
        # Funciones de torque temporal
        tau_grass_sinusoidal, tau_grass_step, tau_grass_ramp, tau_grass_exponential,
        # Funciones de torque espacial
        tau_grass_spatial_zones, tau_grass_spatial_gaussian_patches,
        tau_grass_spatial_sigmoid_transition, tau_grass_spatial_sinusoidal,
        tau_grass_spatial_complex_terrain,
        # Funciones de condiciones iniciales
        create_initial_conditions, initial_conditions_from_rpm,
        initial_conditions_blade_angle, initial_conditions_spinning,
        # Configuration Wrapper
        RotaryCutterConfig, ConfigurationManager
    )
    USING_NEW_ARCHITECTURE = False



# CSS personalizado para diseño sobrio y profesional
st.markdown("""
<style>
    /* Variables CSS para colores consistentes */
    :root {
        --primary-blue: #1e3a8a;
        --secondary-blue: #3b82f6;
        --light-gray: #f8fafc;
        --medium-gray: #e2e8f0;
        --dark-gray: #475569;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --shadow-subtle: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-medium: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Fondo general de la aplicación */
    .stApp {
        background-color: var(--light-gray);
    }

    /* Header principal con degradado sobrio */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        border-radius: 16px;
        box-shadow: var(--shadow-medium);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }

    /* Headers de sección con iconos SVG */
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, white 0%, var(--light-gray) 100%);
        border-radius: 12px;
        border-left: 4px solid var(--secondary-blue);
        box-shadow: var(--shadow-subtle);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    /* Tarjetas de métricas con tamaño equilibrado */
    .metric-card {
        background: white;
        padding: 1.25rem 1rem;
        border-radius: 12px;
        border: 1px solid var(--medium-gray);
        box-shadow: var(--shadow-subtle);
        margin: 0.75rem 0;
        transition: all 0.2s ease;
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-card:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-1px);
    }

    /* Mejoras para métricas de Streamlit */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--medium-gray);
        box-shadow: var(--shadow-subtle);
        margin: 0.5rem 0;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .stMetric > div {
        padding: 0.25rem 0;
    }

    .stMetric [data-testid="metric-container"] {
        padding: 0.75rem;
        min-height: 70px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid var(--medium-gray);
    }

    /* Botones principales con tamaño equilibrado */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        min-height: 2.5rem;
        box-shadow: var(--shadow-subtle);
        transition: all 0.2s ease;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .stButton > button:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-1px);
    }

    /* Mensajes de estado */
    .success-message {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
        box-shadow: var(--shadow-subtle);
    }

    .warning-message {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
        box-shadow: var(--shadow-subtle);
    }

    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
        box-shadow: var(--shadow-subtle);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--light-gray);
        border-radius: 8px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 6px;
        color: var(--text-secondary);
        font-weight: 500;
        border: 1px solid var(--medium-gray);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        color: white;
        border: 1px solid var(--secondary-blue);
    }

    /* Inputs styling con espaciado equilibrado */
    .stNumberInput > div > div > input {
        border-radius: 6px;
        border: 1px solid var(--medium-gray);
        padding: 0.5rem 0.75rem;
        min-height: 2.2rem;
        font-size: 0.9rem;
    }

    .stSelectbox > div > div > div {
        border-radius: 6px;
        border: 1px solid var(--medium-gray);
        padding: 0.5rem 0.75rem;
        min-height: 2.2rem;
        font-size: 0.9rem;
    }

    /* Mejoras específicas para sliders */
    .stSlider {
        padding: 0.5rem 0;
    }

    .stSlider > div > div > div > div {
        padding: 0.5rem 0;
    }

    .stSlider > div > div > div {
        padding: 0.25rem 0;
    }

    /* Mejorar el track del slider */
    .stSlider > div > div > div > div > div {
        height: 4px;
        background: var(--medium-gray);
        border-radius: 2px;
    }

    /* Mejorar el thumb del slider */
    .stSlider > div > div > div > div > div > div {
        width: 16px;
        height: 16px;
        background: var(--primary-blue);
        border: 2px solid white;
        box-shadow: var(--shadow-subtle);
    }

    /* Labels de sliders */
    .stSlider > label {
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    /* Mejoras para expandir elementos con tamaño equilibrado */
    .stExpander > div > div > div {
        padding: 1rem;
    }

    .stExpander [data-testid="stExpander"] {
        border: 1px solid var(--medium-gray);
        border-radius: 8px;
        box-shadow: var(--shadow-subtle);
        margin: 0.75rem 0;
    }

    /* Mejoras para text areas */
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid var(--medium-gray);
        padding: 0.75rem;
        min-height: 100px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
    }

    /* Status indicators con tamaño equilibrado */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 1rem;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
        min-height: 2rem;
        min-width: 100px;
        text-align: center;
        white-space: nowrap;
        box-shadow: var(--shadow-subtle);
        transition: all 0.2s ease;
    }

    .status-indicator:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-medium);
    }

    .status-success {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        border: 1px solid #22c55e;
    }

    .status-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        border: 1px solid #f59e0b;
    }

    .status-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        border: 1px solid #ef4444;
    }

    .status-info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        border: 1px solid #3b82f6;
    }

    /* Iconos SVG personalizados */
    .icon-settings::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-rocket::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M4.5 16.5c-1.5 1.5-1.5 4.5 0 6s4.5 1.5 6 0l.5-.5c1.5-1.5 1.5-4.5 0-6s-4.5-1.5-6 0l-.5.5z'/%3E%3Cpath d='M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z'/%3E%3Cpath d='M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0'/%3E%3Cpath d='M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-chart::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M3 3v18h18'/%3E%3Cpath d='M18.7 8l-5.1 5.2-2.8-2.7L7 14.3'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-play::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpolygon points='5,3 19,12 5,21'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-target::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-database::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cellipse cx='12' cy='5' rx='9' ry='3'/%3E%3Cpath d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'/%3E%3Cpath d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-cpu::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Crect x='4' y='4' width='16' height='16' rx='2'/%3E%3Crect x='9' y='9' width='6' height='6'/%3E%3Cpath d='M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-layers::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpolygon points='12,2 2,7 12,12 22,7 12,2'/%3E%3Cpolyline points='2,17 12,22 22,17'/%3E%3Cpolyline points='2,12 12,17 22,12'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-tool::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-leaf::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M17 8c0-3.87-3.13-7-7-7s-7 3.13-7 7c0 3.87 3.13 7 7 7 1.93 0 3.68-.79 4.95-2.05L20 18l-2-2-5.05-5.05C14.21 11.68 15 13.43 15 15.3c0 1.93-.79 3.68-2.05 4.95'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-check::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2322c55e' stroke-width='2'%3E%3Cpolyline points='20,6 9,17 4,12'/%3E%3C/svg%3E");
        margin-right: 6px;
    }

    .icon-x::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='2'%3E%3Cline x1='18' y1='6' x2='6' y2='18'/%3E%3Cline x1='6' y1='6' x2='18' y2='18'/%3E%3C/svg%3E");
        margin-right: 6px;
    }

    .icon-alert::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23f59e0b' stroke-width='2'%3E%3Cpath d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3Cline x1='12' y1='9' x2='12' y2='13'/%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'/%3E%3C/svg%3E");
        margin-right: 6px;
    }

    .icon-book::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M4 19.5A2.5 2.5 0 0 1 6.5 17H20'/%3E%3Cpath d='M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-microscope::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M6 18h8'/%3E%3Cpath d='M3 22h18'/%3E%3Cpath d='M14 22a7 7 0 1 0 0-14h-1'/%3E%3Cpath d='M9 14h.01'/%3E%3Cpath d='M15 6h.01'/%3E%3Cpath d='M12 6h.01'/%3E%3Cpath d='M12 10h.01'/%3E%3Cpath d='M9 10h.01'/%3E%3Cpath d='M12 14h.01'/%3E%3Cpath d='M15 10h.01'/%3E%3Cpath d='M9 6h.01'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    /* Professional icons for efficiency analysis */
    .icon-efficiency::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M3 3v18h18'/%3E%3Cpath d='M18.7 8l-5.1 5.2-2.8-2.7L7 14.3'/%3E%3Ccircle cx='18.7' cy='8' r='2'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-power::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M18.36 6.64a9 9 0 1 1-12.73 0'/%3E%3Cline x1='12' y1='2' x2='12' y2='12'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-trend::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpolyline points='22,12 18,12 15,21 9,3 6,12 2,12'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-pie::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M21.21 15.89A10 10 0 1 1 8 2.83'/%3E%3Cpath d='M22 12A10 10 0 0 0 12 2v10z'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-summary::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14,2 14,8 20,8'/%3E%3Cline x1='16' y1='13' x2='8' y2='13'/%3E%3Cline x1='16' y1='17' x2='8' y2='17'/%3E%3Cpolyline points='10,9 9,9 8,9'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-metrics::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Crect x='3' y='3' width='18' height='18' rx='2' ry='2'/%3E%3Crect x='7' y='7' width='3' height='9'/%3E%3Crect x='14' y='7' width='3' height='5'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-time::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpolyline points='12,6 12,12 16,14'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-recommendations::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Cpath d='M9 11H5a2 2 0 0 0-2 2v3c0 1.1.9 2 2 2h4m6-6h4a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-4m-6-6V9a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m-6 0V9a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    .icon-guide::before {
        content: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3'/%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'/%3E%3C/svg%3E");
        margin-right: 8px;
    }

    /* Professional status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem 0;
    }

    .status-excellent {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }

    .status-good {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }

    .status-poor {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }

    .status-info {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }

    /* Mejoras para DataFrames y tablas */
    .stDataFrame {
        border: 1px solid var(--medium-gray);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: var(--shadow-subtle);
        margin: 1rem 0;
    }

    .stDataFrame > div {
        padding: 0;
    }

    .stDataFrame table {
        border-collapse: collapse;
        width: 100%;
    }

    .stDataFrame th {
        background: linear-gradient(135deg, var(--light-gray) 0%, var(--medium-gray) 100%);
        padding: 0.75rem 0.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-primary);
        border-bottom: 2px solid var(--medium-gray);
    }

    .stDataFrame td {
        padding: 0.5rem;
        font-size: 0.85rem;
        border-bottom: 1px solid var(--medium-gray);
        vertical-align: middle;
    }

    .stDataFrame tr:hover {
        background-color: var(--light-gray);
    }

    /* Mejoras para código con tamaño equilibrado */
    .stCode {
        border: 1px solid var(--medium-gray);
        border-radius: 8px;
        box-shadow: var(--shadow-subtle);
        margin: 0.75rem 0;
    }

    .stCode > div {
        padding: 1rem;
        font-size: 0.85rem;
    }

    /* Mejoras para alertas y mensajes */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        border-left: 4px solid;
        font-size: 0.9rem;
    }

    .stSuccess {
        border-left-color: #22c55e;
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
    }

    .stWarning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    }

    .stError {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    }

    .stInfo {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    }

    /* Mejoras para columnas y espaciado */
    .stColumn {
        padding: 0 0.5rem;
    }

    .stColumn > div {
        padding: 0.25rem 0;
    }

    /* Espaciado entre secciones */
    .section-header {
        margin: 1.5rem 0 1rem 0;
    }

    /* Mejoras para number inputs en columnas */
    .stColumn .stNumberInput {
        margin-bottom: 1rem;
    }

    .stColumn .stSelectbox {
        margin-bottom: 1rem;
    }

    .stColumn .stSlider {
        margin-bottom: 1rem;
    }

    /* Mejoras para labels */
    .stNumberInput > label,
    .stSelectbox > label,
    .stSlider > label {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    /* Contenedor principal más espacioso */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Mejoras para subsecciones */
    .stMarkdown h4,
    .stMarkdown strong {
        color: var(--text-primary);
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
    }

    /* Espaciado entre filas de parámetros */
    .stMarkdown p strong {
        display: block;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid var(--light-gray);
        font-size: 0.95rem;
    }

    /* Reducir espaciado excesivo en métricas */
    .stMetric {
        margin-bottom: 0.5rem;
    }

    /* Mejorar espaciado en expandir */
    .stExpander [data-testid="stExpanderDetails"] {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Verificar disponibilidad de matplotlib después de la configuración de página
if not MATPLOTLIB_AVAILABLE:
    st.error("Matplotlib no está disponible. Instala matplotlib para ver gráficos.")

def load_configuration_from_file(uploaded_file):
    """
    Carga configuración de parámetros desde archivo Excel o CSV.

    Args:
        uploaded_file: Archivo cargado por el usuario

    Returns:
        dict: Diccionario con parámetros cargados o None si hay error
    """
    try:
        # Determinar el tipo de archivo
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            # Leer archivo CSV
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            # Leer archivo Excel
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_extension}")

        # Buscar columnas de parámetros y valores
        param_col = None
        value_col = None

        # Buscar columnas que contengan parámetros y valores
        for col in df.columns:
            col_lower = str(col).lower()
            if 'param' in col_lower or 'nombre' in col_lower or 'name' in col_lower:
                param_col = col
            elif 'valor' in col_lower or 'value' in col_lower or 'val' in col_lower:
                value_col = col

        # Si no se encuentran columnas específicas, usar las dos primeras
        if param_col is None or value_col is None:
            if len(df.columns) >= 2:
                param_col = df.columns[0]
                value_col = df.columns[1]
            else:
                raise ValueError("El archivo debe tener al menos 2 columnas (parámetro, valor)")

        # Crear diccionario de parámetros
        params = {}

        # Mapeo de nombres de parámetros
        param_mapping = {
            'masa': 'mass',
            'mass': 'mass',
            'torque': 'tau_input',
            'tau_input': 'tau_input',
            'torque_motor': 'tau_input',
            'radio': 'R',
            'radius': 'R',
            'r': 'R',
            'cuchillas': 'n_blades',
            'n_blades': 'n_blades',
            'numero_cuchillas': 'n_blades',
            'velocidad_angular': 'omega_ref',
            'omega': 'omega_ref',
            'omega_ref': 'omega_ref',
            'masa_plato_percent': 'mass_plate_percent',
            'mass_plate_percent': 'mass_plate_percent',
            'longitud_percent': 'L_percent',
            'l_percent': 'L_percent',
            'friccion': 'b',
            'b': 'b',
            'friccion_viscosa': 'b',
            'arrastre': 'c_drag',
            'c_drag': 'c_drag',
            'arrastre_aerodinamico': 'c_drag',
            'densidad_vegetal': 'rho_veg',
            'rho_veg': 'rho_veg',
            'densidad': 'rho_veg',
            'velocidad_avance': 'v_avance',
            'v_avance': 'v_avance',
            'velocidad': 'v_avance',
            'resistencia_vegetal': 'k_grass',
            'k_grass': 'k_grass',
            'resistencia': 'k_grass',
            'ancho': 'w',
            'w': 'w',
            'ancho_corte': 'w'
        }

        # Procesar cada fila del DataFrame
        for _, row in df.iterrows():
            param_name = str(row[param_col]).strip().lower()
            param_value = row[value_col]

            # Buscar el parámetro en el mapeo
            mapped_param = None
            for key, mapped in param_mapping.items():
                if key in param_name or param_name in key:
                    mapped_param = mapped
                    break

            if mapped_param and pd.notna(param_value):
                try:
                    # Convertir a número si es posible
                    if isinstance(param_value, str):
                        param_value = param_value.replace(',', '.')  # Manejar decimales con coma
                    params[mapped_param] = float(param_value)
                except (ValueError, TypeError):
                    # Si no se puede convertir a número, mantener como string
                    params[mapped_param] = param_value

        return params if params else None

    except Exception as e:
        raise Exception(f"Error al procesar archivo: {str(e)}")


def load_multiple_configurations_from_file(uploaded_file):
    """
    Carga múltiples configuraciones desde archivo Excel usando Configuration Wrapper.

    Args:
        uploaded_file: Archivo cargado por el usuario

    Returns:
        ConfigurationManager: Gestor con configuraciones cargadas o None si hay error
    """
    try:
        # Determinar el tipo de archivo
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_extension}")

        # Debug: mostrar información del DataFrame cargado
        with st.expander("Debug - Información del archivo cargado"):
            st.write(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            st.write("**Columnas encontradas:**", list(df.columns))
            st.write("**Primeras 3 filas:**")
            st.dataframe(df.head(3))

        # Verificar si el archivo tiene formato de múltiples configuraciones
        if len(df.columns) < 3:
            st.warning(f"El archivo tiene solo {len(df.columns)} columnas. Se necesitan al menos 3 para múltiples configuraciones.")
            return None

        # Crear gestor de configuraciones
        config_manager = ConfigurationManager()

        # Cargar configuraciones usando el wrapper
        config_manager.load_from_dataframe(df)

        # Mostrar resumen del procesamiento
        if len(config_manager) > 0:
            with st.expander("Debug - Configuraciones procesadas"):
                summary_df = config_manager.get_summary_dataframe()
                st.dataframe(summary_df)
                st.write(f"**Total configuraciones válidas:** {len(config_manager)}")

            return config_manager
        else:
            st.warning("No se pudieron procesar configuraciones válidas del archivo")
            return None

    except Exception as e:
        raise Exception(f"Error al procesar archivo de múltiples configuraciones: {str(e)}")


def show_physical_model_explanation():
    """Muestra la explicación detallada del modelo físico"""

    st.markdown('<div class="main-header">Modelo Físico del Rotary Cutter</div>',
                unsafe_allow_html=True)

    # Botón para volver a la interfaz principal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Volver a Simulación", use_container_width=True):
            st.session_state.show_model_explanation = False
            st.rerun()

    # Crear pestañas para organizar la información
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Fundamentos Teóricos",
        "Ecuaciones Diferenciales",
        "Parámetros Físicos",
        "Método Numérico",
        "Métricas de Rendimiento"
    ])

    with tab1:
        show_theoretical_foundations()

    with tab2:
        show_differential_equations()

    with tab3:
        show_physical_parameters()

    with tab4:
        show_numerical_method()

    with tab5:
        show_performance_metrics()


def show_theoretical_foundations():
    """Muestra los fundamentos teóricos del modelo"""

    st.markdown("## Fundamentos Teóricos del Sistema")

    st.markdown("""
    ### Principios Físicos Fundamentales

    El modelo del rotary cutter se basa en los principios fundamentales de la **mecánica rotacional**
    y la **dinámica de sistemas mecánicos**. El sistema se modela como un **cuerpo rígido rotante**
    sometido a múltiples torques que actúan sobre él.
    """)

    # Diagrama conceptual usando texto
    st.markdown("""
    ### Diagrama Conceptual del Sistema

    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                    ROTARY CUTTER SYSTEM                    │
    │                                                             │
    │    Motor ──→ τ_input ──→ [PLATO + CUCHILLAS] ──→ Corte     │
    │                              │                              │
    │                              ↓                              │
    │                         Resistencias:                      │
    │                         • Fricción viscosa (b·ω)           │
    │                         • Arrastre aerodinámico (c·ω²)     │
    │                         • Resistencia vegetal (τ_grass)    │
    └─────────────────────────────────────────────────────────────┘
    ```
    """)

    st.markdown("""
    ### Ley Fundamental: Segunda Ley de Newton para Rotación

    El comportamiento dinámico del sistema se rige por la **segunda ley de Newton para movimiento rotacional**:

    **I · α = Σ τ**

    Donde:
    - **I**: Momento de inercia total del sistema [kg·m²]
    - **α**: Aceleración angular [rad/s²]
    - **Σ τ**: Suma algebraica de todos los torques actuantes [N·m]
    """)

    st.markdown("""
    ### Componentes del Sistema

    #### 1. **Momento de Inercia Total (I_total)**
    El sistema está compuesto por:
    - **Plato central**: Disco de masa concentrada
    - **Cuchillas**: Masas puntuales en los extremos

    #### 2. **Torques Actuantes**
    - **τ_input**: Torque motor (entrada de energía)
    - **τ_friction**: Fricción viscosa en rodamientos
    - **τ_drag**: Arrastre aerodinámico
    - **τ_grass**: Resistencia por corte de vegetación
    """)


def show_differential_equations():
    """Muestra las ecuaciones diferenciales del sistema"""

    st.markdown("## Sistema de Ecuaciones Diferenciales")

    st.markdown("""
    ### Variables de Estado

    El sistema se describe mediante **dos variables de estado**:

    - **θ(t)**: Posición angular del plato [rad]
    - **ω(t)**: Velocidad angular del plato [rad/s]
    """)

    st.markdown("""
    ### Sistema de EDOs de Primer Orden

    El modelo se formula como un sistema de ecuaciones diferenciales ordinarias de primer orden:
    """)

    # Mostrar las ecuaciones principales
    st.latex(r'''
    \begin{cases}
    \frac{d\theta}{dt} = \omega \\[0.5em]
    \frac{d\omega}{dt} = \frac{\tau_{input} - \tau_{friction} - \tau_{drag} - \tau_{grass}}{I_{total}}
    \end{cases}
    ''')

    st.markdown("""
    ### Desglose de Cada Término

    #### **1. Momento de Inercia Total**
    """)

    st.latex(r'''
    I_{total} = I_{plate} + n_{blades} \cdot m_c \cdot (R + L)^2
    ''')

    st.markdown("""
    Donde:
    - **I_plate**: Momento de inercia del plato central
    - **n_blades**: Número de cuchillas
    - **m_c**: Masa de cada cuchilla
    - **R**: Radio al punto de fijación de la cuchilla
    - **L**: Longitud de la cuchilla desde el punto de fijación
    """)

    st.markdown("""
    #### **2. Torque de Fricción Viscosa**
    """)

    st.latex(r'''
    \tau_{friction} = b \cdot \omega
    ''')

    st.markdown("""
    - **b**: Coeficiente de fricción viscosa [N·m·s/rad]
    - Representa pérdidas en rodamientos y sellos
    - **Proporcional a la velocidad angular**
    """)

    st.markdown("""
    #### **3. Torque de Arrastre Aerodinámico**
    """)

    st.latex(r'''
    \tau_{drag} = c_{drag} \cdot \omega^2 \cdot \text{sign}(\omega)
    ''')

    st.markdown("""
    - **c_drag**: Coeficiente de arrastre aerodinámico [N·m·s²/rad²]
    - Representa resistencia del aire
    - **Proporcional al cuadrado de la velocidad angular**
    - La función sign() preserva la dirección del torque resistivo
    """)

    st.markdown("""
    #### **4. Torque de Resistencia Vegetal**

    **Modelo Constante:**
    """)

    st.latex(r'''
    \tau_{grass} = k_{grass} \cdot \rho_{veg} \cdot v_{avance} \cdot R
    ''')

    st.markdown("""
    **Modelo Variable Espacial:**
    """)

    st.latex(r'''
    \tau_{grass}(t) = k_{grass} \cdot \rho(x(t)) \cdot R
    ''')

    st.latex(r'''
    \text{donde } x(t) = v_{avance} \cdot t
    ''')

    st.markdown("""
    - **k_grass**: Constante de resistencia vegetal [N·s/m]
    - **ρ_veg** o **ρ(x)**: Densidad de vegetación [kg/m²]
    - **v_avance**: Velocidad de avance del equipo [m/s]
    - **R**: Radio efectivo de corte [m]
    """)


def show_physical_parameters():
    """Muestra la explicación detallada de los parámetros físicos"""

    st.markdown("## Parámetros Físicos del Sistema")

    st.markdown("""
    ### Clasificación de Parámetros

    Los parámetros del modelo se clasifican en **cuatro categorías principales**:
    """)

    # Crear pestañas para organizar los parámetros
    tab1, tab2, tab3, tab4 = st.tabs([
        "Geométricos",
        "Másicos e Inerciales",
        "Vegetación y Corte",
        "Dinámicos"
    ])

    with tab1:
        show_geometric_parameters()

    with tab2:
        show_mass_inertial_parameters()

    with tab3:
        show_vegetation_parameters()

    with tab4:
        show_dynamic_parameters()


def show_geometric_parameters():
    """Muestra los parámetros geométricos del sistema"""

    st.markdown("### Parámetros Geométricos")

    st.markdown("""
    #### **R - Radio Principal [m]**
    - **Definición**: Radio desde el centro del plato hasta el punto de fijación de las cuchillas
    - **Rango típico**: 0.3 - 1.2 m
    - **Impacto**: Determina el momento de inercia y la velocidad lineal de corte
    - **Relación**: Velocidad lineal = ω × R
    """)

    st.latex(r"v_{linear} = \omega \times R")

    st.markdown("""
    #### **L - Longitud de Cuchilla [m]**
    - **Definición**: Longitud de cada cuchilla desde el punto de fijación hasta la punta
    - **Cálculo**: L = R × (L_percent / 100)
    - **Rango típico**: 10% - 100% del radio principal
    - **Impacto**: Afecta el momento de inercia de las cuchillas y el ancho de corte efectivo
    """)

    st.latex(r"I_{blades} = n_{blades} \times m_c \times (R + L)^2")

    st.markdown("""
    #### **w - Ancho de Corte [m]**
    - **Definición**: Ancho total de la franja cortada por el equipo
    - **Rango típico**: 1.5 - 3.0 m (equipos agrícolas estándar)
    - **Impacto**: Determina el área cortada por unidad de tiempo
    - **Relación**: Área cortada = w × v_avance × t
    """)


def show_mass_inertial_parameters():
    """Muestra los parámetros másicos e inerciales"""

    st.markdown("### Parámetros Másicos e Inerciales")

    st.markdown("""
    #### **Distribución de Masa**

    El sistema divide la masa total en dos componentes principales:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Plato Central:**
        - Masa: m_plate = mass × (mass_plate_percent / 100)
        - Momento de inercia: I_plate = 0.5 × m_plate × R²
        - Modelo: Disco sólido uniforme
        """)

    with col2:
        st.markdown("""
        **Cuchillas:**
        - Masa total: m_blades = mass - m_plate
        - Masa por cuchilla: m_c = m_blades / n_blades
        - Modelo: Masas puntuales en los extremos
        """)

    st.markdown("""
    #### **I_total - Momento de Inercia Total [kg·m²]**

    El momento de inercia total combina las contribuciones del plato y las cuchillas:
    """)

    st.latex(r"I_{total} = I_{plate} + I_{blades}")
    st.latex(r"I_{total} = \frac{1}{2} m_{plate} R^2 + n_{blades} \times m_c \times (R + L)^2")

    st.markdown("""
    **Justificación del Modelo:**
    - **Plato**: Se modela como disco sólido porque la masa está distribuida uniformemente
    - **Cuchillas**: Se modelan como masas puntuales porque son delgadas y la masa se concentra en los extremos
    - **Teorema de Steiner**: Las cuchillas están a distancia (R + L) del centro de rotación
    """)

    st.markdown("""
    #### **n_blades - Número de Cuchillas**
    - **Rango típico**: 2 - 12 cuchillas
    - **Impacto**: Afecta el momento de inercia total y la distribución de masa
    - **Consideración**: Más cuchillas = mayor inercia pero mejor distribución de carga
    """)


def show_vegetation_parameters():
    """Muestra los parámetros de vegetación y corte"""

    st.markdown("### Parámetros de Vegetación y Corte")

    st.markdown("""
    #### **ρ_veg - Densidad de Vegetación [kg/m²]**
    - **Definición**: Masa de vegetación por unidad de área
    - **Rango típico**: 0.5 - 3.0 kg/m² (pasto, maleza ligera a densa)
    - **Variabilidad**: Puede ser constante o variable espacialmente
    - **Impacto**: Determina directamente la resistencia al corte
    """)

    st.markdown("""
    #### **k_grass - Constante de Resistencia Vegetal [N·s/m]**
    - **Definición**: Factor que relaciona la densidad vegetal con el torque resistivo
    - **Rango típico**: 10 - 30 N·s/m
    - **Dependencias**: Tipo de vegetación, humedad, altura, dureza
    - **Calibración**: Se determina experimentalmente para cada tipo de cultivo
    """)

    st.markdown("""
    #### **v_avance - Velocidad de Avance [m/s]**
    - **Definición**: Velocidad de desplazamiento del equipo sobre el terreno
    - **Rango típico**: 1.5 - 6.0 m/s (5.4 - 21.6 km/h)
    - **Impacto**: Afecta la tasa de encuentro con nueva vegetación
    - **Relación**: Potencia requerida ∝ v_avance
    """)

    st.markdown("""
    #### **Modelo de Resistencia Vegetal**

    **Modelo Básico (Constante):**
    """)

    st.latex(r"\tau_{grass} = k_{grass} \times \rho_{veg} \times v_{avance} \times R")

    st.markdown("""
    **Modelo Avanzado (Variable Espacial):**
    """)

    st.latex(r"\tau_{grass}(t) = k_{grass} \times \rho(x(t)) \times R")
    st.latex(r"\text{donde } x(t) = v_{avance} \times t")

    st.markdown("""
    **Justificación Física:**
    - El torque es proporcional a la densidad de vegetación encontrada
    - La velocidad de avance determina la tasa de encuentro con nueva vegetación
    - El radio R amplifica el efecto debido al brazo de palanca
    """)


def show_dynamic_parameters():
    """Muestra los parámetros dinámicos del sistema"""

    st.markdown("### Parámetros Dinámicos")

    st.markdown("""
    #### **τ_input - Torque del Motor [N·m]**
    - **Definición**: Torque de entrada proporcionado por el motor
    - **Rango típico**: 100 - 500 N·m (equipos agrícolas)
    - **Características**: Generalmente constante o controlado
    - **Limitaciones**: Potencia máxima del motor, eficiencia de transmisión
    """)

    st.markdown("""
    #### **b - Coeficiente de Fricción Viscosa [N·m·s/rad]**
    - **Definición**: Resistencia proporcional a la velocidad angular
    - **Fuentes físicas**: Rodamientos, sellos, lubricación
    - **Rango típico**: 0.1 - 1.0 N·m·s/rad
    - **Modelo**: τ_friction = b × ω
    """)

    st.latex(r"\tau_{friction} = b \times \omega")

    st.markdown("""
    **Justificación:** La fricción viscosa es dominante a altas velocidades y es característica de sistemas con lubricación.
    """)

    st.markdown("""
    #### **c_drag - Coeficiente de Arrastre Aerodinámico [N·m·s²/rad²]**
    - **Definición**: Resistencia proporcional al cuadrado de la velocidad angular
    - **Fuentes físicas**: Resistencia del aire, turbulencia
    - **Rango típico**: 0.01 - 0.1 N·m·s²/rad²
    - **Modelo**: τ_drag = c_drag × ω² × sign(ω)
    """)

    st.latex(r"\tau_{drag} = c_{drag} \times \omega^2 \times \text{sign}(\omega)")

    st.markdown("""
    **Justificación:** El arrastre aerodinámico sigue la ley cuadrática típica de la mecánica de fluidos.
    """)

    st.markdown("""
    ### Interacciones Entre Parámetros

    #### **Acoplamiento Geométrico-Inercial**
    - Radio mayor → Mayor momento de inercia → Mayor inercia rotacional
    - Más cuchillas → Mayor inercia → Respuesta más lenta

    #### **Acoplamiento Dinámico-Operacional**
    - Mayor velocidad de avance → Mayor resistencia vegetal → Mayor torque requerido
    - Mayor densidad vegetal → Mayor carga → Menor velocidad angular final

    #### **Compromiso de Diseño**
    - **Eficiencia vs. Robustez**: Sistemas ligeros son más eficientes pero menos robustos
    - **Velocidad vs. Calidad**: Mayor velocidad reduce calidad de corte
    - **Potencia vs. Consumo**: Mayor potencia permite mayor productividad pero aumenta consumo
    """)


def show_numerical_method():
    """Muestra la explicación del método numérico utilizado"""

    st.markdown("## Método Numérico de Integración")

    st.markdown("""
    ### Selección del Método: Runge-Kutta de 4º/5º Orden (RK45)

    El sistema utiliza el método **RK45** implementado en `scipy.integrate.solve_ivp` para resolver
    el sistema de ecuaciones diferenciales ordinarias.
    """)

    # Crear pestañas para organizar la información
    tab1, tab2, tab3, tab4 = st.tabs([
        "¿Por qué RK45?",
        "Fundamento Matemático",
        "Implementación",
        "Ventajas y Limitaciones"
    ])

    with tab1:
        show_rk45_justification()

    with tab2:
        show_rk45_mathematics()

    with tab3:
        show_rk45_implementation()

    with tab4:
        show_rk45_advantages()


def show_rk45_justification():
    """Explica por qué se eligió el método RK45"""

    st.markdown("### Justificación de la Selección del Método")

    st.markdown("""
    #### **Características del Problema**

    Nuestro sistema de EDOs presenta las siguientes características:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Propiedades del Sistema:**
        - Sistema de 2 EDOs de primer orden
        - No lineal (términos cuadráticos en ω)
        - No rígido (stiff) en condiciones normales
        - Solución suave y continua
        - Condiciones iniciales bien definidas
        """)

    with col2:
        st.markdown("""
        **Requerimientos Numéricos:**
        - Alta precisión (errores < 0.1%)
        - Eficiencia computacional
        - Estabilidad numérica
        - Control automático del paso
        - Robustez ante cambios de parámetros
        """)

    st.markdown("""
    #### **Comparación de Métodos**
    """)

    # Crear tabla comparativa
    comparison_data = {
        "Método": ["Euler", "RK2 (Heun)", "RK4 Clásico", "RK45 Adaptativo", "Adams-Bashforth"],
        "Orden": ["1", "2", "4", "4/5", "Variable"],
        "Precisión": ["Baja", "Media", "Alta", "Muy Alta", "Alta"],
        "Eficiencia": ["Alta", "Media", "Media", "Muy Alta", "Alta"],
        "Control de Error": ["No", "No", "No", "Sí", "Limitado"],
        "Recomendado": ["No", "No", "Sí", "Recomendado", "No"]
    }

    import pandas as pd
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)

    st.markdown("""
    #### **Decisión Final: RK45**

    **Razones principales:**
    1. **Control automático de error**: Ajusta el paso de tiempo automáticamente
    2. **Eficiencia**: Reutiliza evaluaciones de función entre pasos
    3. **Robustez**: Maneja bien cambios abruptos en las funciones de torque
    4. **Precisión**: Error local de orden O(h⁶)
    5. **Implementación madura**: scipy.integrate.solve_ivp es altamente optimizado
    """)


def show_rk45_mathematics():
    """Explica el fundamento matemático del método RK45"""

    st.markdown("### Fundamento Matemático del Método RK45")

    st.markdown("""
    #### **Formulación del Problema**

    Nuestro sistema de EDOs se expresa como:
    """)

    st.latex(r"""
    \frac{d\mathbf{y}}{dt} = \mathbf{f}(t, \mathbf{y})
    """)

    st.markdown("""
    Donde:
    """)

    st.latex(r"""
    \mathbf{y} = \begin{pmatrix} \theta \\ \omega \end{pmatrix}, \quad
    \mathbf{f}(t, \mathbf{y}) = \begin{pmatrix}
    \omega \\
    \frac{\tau_{input} - \tau_{friction} - \tau_{drag} - \tau_{grass}}{I_{total}}
    \end{pmatrix}
    """)

    st.markdown("""
    #### **Método de Runge-Kutta de 4º Orden (Base)**

    El método RK4 clásico utiliza la fórmula:
    """)

    st.latex(r"""
    \mathbf{y}_{n+1} = \mathbf{y}_n + \frac{h}{6}(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4)
    """)

    st.markdown("""
    Donde las pendientes se calculan como:
    """)

    st.latex(r"""
    \begin{align}
    \mathbf{k}_1 &= \mathbf{f}(t_n, \mathbf{y}_n) \\
    \mathbf{k}_2 &= \mathbf{f}(t_n + \frac{h}{2}, \mathbf{y}_n + \frac{h}{2}\mathbf{k}_1) \\
    \mathbf{k}_3 &= \mathbf{f}(t_n + \frac{h}{2}, \mathbf{y}_n + \frac{h}{2}\mathbf{k}_2) \\
    \mathbf{k}_4 &= \mathbf{f}(t_n + h, \mathbf{y}_n + h\mathbf{k}_3)
    \end{align}
    """)

    st.markdown("""
    #### **Extensión RK45: Control de Error**

    El método RK45 combina dos estimaciones:
    - **4º orden**: Estimación principal (como RK4)
    - **5º orden**: Estimación de mayor precisión

    **Error local estimado:**
    """)

    st.latex(r"""
    \mathbf{e}_{n+1} = \mathbf{y}_{5} - \mathbf{y}_{4}
    """)

    st.markdown("""
    **Control adaptativo del paso:**
    """)

    st.latex(r"""
    h_{nuevo} = h_{actual} \times \min\left(5, \max\left(0.2, 0.9 \times \left(\frac{tol}{\|\mathbf{e}\|}\right)^{1/5}\right)\right)
    """)

    st.markdown("""
    #### **Tolerancias Utilizadas**

    En nuestro sistema configuramos:
    - **rtol = 1e-8**: Tolerancia relativa (0.000001%)
    - **atol = 1e-10**: Tolerancia absoluta (muy pequeña)

    **Criterio de aceptación:**
    """)

    st.latex(r"""
    \|\mathbf{e}\| \leq rtol \times \|\mathbf{y}\| + atol
    """)


def show_rk45_implementation():
    """Muestra detalles de la implementación"""

    st.markdown("### Implementación en el Sistema")

    st.markdown("""
    #### **Configuración de solve_ivp**

    El sistema utiliza la siguiente configuración:
    """)

    st.code("""
    sol = solve_ivp(
        fun=lambda t, y: rotary_cutter_system(t, y, params),
        t_span=(0, t_max),
        y0=y0,
        method='RK45',
        t_eval=t_eval,
        vectorized=False,
        rtol=1e-8,
        atol=1e-10
    )
    """, language="python")

    st.markdown("""
    #### **Parámetros de Configuración**
    """)

    config_data = {
        "Parámetro": ["method", "rtol", "atol", "vectorized", "t_eval", "t_span"],
        "Valor": ["'RK45'", "1e-8", "1e-10", "False", "np.linspace(0, t_max, 1000)", "(0, t_max)"],
        "Propósito": [
            "Método de integración adaptativo",
            "Tolerancia relativa (precisión)",
            "Tolerancia absoluta (estabilidad)",
            "Evaluación escalar (más estable)",
            "Puntos de salida uniformes",
            "Intervalo de integración"
        ]
    }

    df_config = pd.DataFrame(config_data)
    st.dataframe(df_config, use_container_width=True)

    st.markdown("""
    #### **Función del Sistema**

    La función `rotary_cutter_system(t, y, params)` implementa:
    """)

    st.code("""
    def rotary_cutter_system(t, y, params):
        theta, omega = y

        # Calcular momento de inercia total
        I_total = params['I_plate'] + params['n_blades'] * params['m_c'] * (params['R'] + params['L'])**2

        # Calcular torques resistivos
        friction = params['b'] * omega
        drag = params['c_drag'] * omega**2 * np.sign(omega)

        # Torque vegetal (constante o variable)
        if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
            tau_grass = params['tau_grass_func'](t)
        else:
            tau_grass = params['k_grass'] * params['rho_veg'] * params['v_avance'] * params['R']

        # Ecuación de movimiento
        domega_dt = (params['tau_input'] - friction - drag - tau_grass) / I_total

        return np.array([omega, domega_dt])
    """, language="python")

    st.markdown("""
    #### **Manejo de Errores**

    El sistema incluye verificación de convergencia:
    """)

    st.code("""
    if not sol.success:
        raise RuntimeError(f"La integración falló: {sol.message}")
    """, language="python")


def show_rk45_advantages():
    """Muestra ventajas y limitaciones del método"""

    st.markdown("### Ventajas y Limitaciones del Método RK45")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### **Ventajas**

        **Precisión:**
        - Error local O(h⁶)
        - Control automático de error
        - Tolerancias configurables

        **Eficiencia:**
        - Paso adaptativo
        - Reutilización de evaluaciones
        - Optimización automática

        **Robustez:**
        - Maneja discontinuidades suaves
        - Estable para sistemas no rígidos
        - Implementación madura

        **Facilidad de uso:**
        - Interfaz estándar
        - Configuración automática
        - Diagnósticos integrados
        """)

    with col2:
        st.markdown("""
        #### **Limitaciones**

        **Sistemas rígidos:**
        - No optimizado para stiff ODEs
        - Puede requerir pasos muy pequeños

        **Discontinuidades:**
        - Problemas con saltos abruptos
        - Requiere detección de eventos

        **Memoria:**
        - Almacena múltiples evaluaciones
        - Mayor uso de memoria que métodos simples

        **Complejidad:**
        - Más complejo que métodos básicos
        - Parámetros internos no controlables
        """)

    st.markdown("""
    #### **Alternativas Consideradas**

    **Para sistemas rígidos:**
    - Radau, BDF: Métodos implícitos para sistemas stiff
    - LSODA: Detección automática de rigidez

    **Para alta precisión:**
    - DOP853: Runge-Kutta de 8º orden
    - Métodos de extrapolación

    **Para tiempo real:**
    - RK4 con paso fijo
    - Métodos explícitos simples

    #### **Validación del Método**

    **Pruebas realizadas:**
    1. **Convergencia**: Verificación con diferentes tolerancias
    2. **Conservación**: Verificación de propiedades físicas
    3. **Estabilidad**: Pruebas con parámetros extremos
    4. **Comparación**: Validación contra soluciones analíticas simples

    **Criterios de aceptación:**
    - Error relativo < 0.01% en casos de prueba
    - Conservación de energía en sistemas conservativos
    - Estabilidad numérica en simulaciones largas
    - Tiempo de cómputo razonable (< 1 segundo para 10 segundos de simulación)
    """)


def show_performance_metrics():
    """Muestra la explicación de las métricas de rendimiento"""

    st.markdown("## Métricas de Rendimiento del Sistema")

    st.markdown("""
    ### Clasificación de Métricas

    El sistema calcula múltiples métricas para evaluar el rendimiento del rotary cutter
    desde diferentes perspectivas: **energética**, **operacional** y **de calidad**.
    """)

    # Crear pestañas para organizar las métricas
    tab1, tab2, tab3, tab4 = st.tabs([
        "Métricas Energéticas",
        "Métricas Operacionales",
        "Métricas de Calidad",
        "Cálculo e Interpretación"
    ])

    with tab1:
        show_energy_metrics()

    with tab2:
        show_operational_metrics()

    with tab3:
        show_quality_metrics()

    with tab4:
        show_metrics_calculation()


def show_energy_metrics():
    """Explica las métricas energéticas"""

    st.markdown("### Métricas Energéticas")

    st.markdown("""
    #### **E_total - Energía Total Consumida [J]**

    **Definición:** Energía total suministrada por el motor durante la operación.
    """)

    st.latex(r"E_{total} = \int_0^T \tau_{input} \times \omega(t) \, dt")

    st.markdown("""
    **Interpretación:**
    - Representa el consumo energético total del sistema
    - Incluye energía útil y pérdidas
    - Fundamental para análisis de eficiencia energética
    - Unidades: Joules [J] o Watt-hora [Wh]
    """)

    st.markdown("""
    #### **E_util - Energía Útil de Corte [J]**

    **Definición:** Energía efectivamente utilizada para el corte de vegetación.
    """)

    st.latex(r"E_{util} = \int_0^T \tau_{grass}(t) \times \omega(t) \, dt")

    st.markdown("""
    **Interpretación:**
    - Energía directamente relacionada con el trabajo de corte
    - Excluye pérdidas por fricción y arrastre aerodinámico
    - Indicador de la efectividad del proceso de corte
    - Base para el cálculo de eficiencia
    """)

    st.markdown("""
    #### **η - Eficiencia Energética [%]**

    **Definición:** Relación entre energía útil y energía total consumida.
    """)

    st.latex(r"\eta = \frac{E_{util}}{E_{total}} \times 100\%")

    st.markdown("""
    **Interpretación:**
    - **η > 70%**: Excelente eficiencia
    - **50% < η < 70%**: Buena eficiencia
    - **30% < η < 50%**: Eficiencia moderada
    - **η < 30%**: Baja eficiencia (revisar parámetros)

    **Factores que afectan la eficiencia:**
    - Fricción viscosa (b): Mayor fricción → Menor eficiencia
    - Arrastre aerodinámico (c_drag): Mayor arrastre → Menor eficiencia
    - Velocidad de operación: Velocidades muy altas reducen eficiencia
    - Densidad vegetal: Densidades muy bajas reducen eficiencia relativa
    """)


def show_operational_metrics():
    """Explica las métricas operacionales"""

    st.markdown("### Métricas Operacionales")

    st.markdown("""
    #### **A_total - Área Total Cortada [m²]**

    **Definición:** Área total de vegetación procesada durante la operación.
    """)

    st.latex(r"A_{total} = w \times v_{avance} \times T")

    st.markdown("""
    **Donde:**
    - **w**: Ancho de corte [m]
    - **v_avance**: Velocidad de avance [m/s]
    - **T**: Tiempo total de operación [s]

    **Interpretación:**
    - Indicador directo de productividad
    - Base para cálculo de rendimiento por unidad de tiempo
    - Fundamental para análisis económico
    """)

    st.markdown("""
    #### **Velocidad Angular Final [rad/s]**

    **Definición:** Velocidad angular alcanzada al final de la simulación.
    """)

    st.latex(r"\omega_{final} = \omega(T)")

    st.markdown("""
    **Interpretación:**
    - Indicador de estabilidad del sistema
    - Relacionado con la calidad de corte
    - **ω_final ≈ ω_steady**: Sistema estable
    - **ω_final << ω_steady**: Sistema sobrecargado
    - **ω_final >> ω_steady**: Sistema subcargado
    """)

    st.markdown("""
    #### **Velocidad Angular Promedio [rad/s]**

    **Definición:** Velocidad angular promedio durante toda la operación.
    """)

    st.latex(r"\bar{\omega} = \frac{1}{T} \int_0^T \omega(t) \, dt")

    st.markdown("""
    **Interpretación:**
    - Indicador de rendimiento operacional promedio
    - Útil para comparar diferentes configuraciones
    - Relacionado con la productividad efectiva
    """)

    st.markdown("""
    #### **Torque RMS [N·m]**

    **Definición:** Valor RMS (Root Mean Square) del torque neto.
    """)

    st.latex(r"\tau_{RMS} = \sqrt{\frac{1}{T} \int_0^T \tau_{net}(t)^2 \, dt}")

    st.markdown("""
    **Interpretación:**
    - Indicador de la carga promedio del sistema
    - Útil para dimensionamiento de componentes
    - Relacionado con el desgaste y vida útil
    """)


def show_quality_metrics():
    """Explica las métricas de calidad"""

    st.markdown("### Métricas de Calidad")

    st.markdown("""
    #### **Estabilidad de Velocidad Angular**

    **Definición:** Medida de la variabilidad de la velocidad angular.
    """)

    st.latex(r"\sigma_\omega = \sqrt{\frac{1}{T} \int_0^T (\omega(t) - \bar{\omega})^2 \, dt}")

    st.markdown("""
    **Interpretación:**
    - **σ_ω < 5% de ω_avg**: Excelente estabilidad
    - **5% < σ_ω < 15%**: Buena estabilidad
    - **σ_ω > 15%**: Estabilidad deficiente

    **Factores que afectan:**
    - Variabilidad de la vegetación
    - Inercia del sistema (I_total)
    - Características del control de torque
    """)

    st.markdown("""
    #### **Uniformidad de Corte**

    **Definición:** Consistencia en la velocidad de corte a lo largo del tiempo.
    """)

    st.latex(r"v_{corte}(t) = \omega(t) \times R")

    st.markdown("""
    **Criterios de calidad:**
    - **Velocidad óptima**: 15-25 m/s en la punta de las cuchillas
    - **Variación < 10%**: Corte uniforme
    - **Variación > 20%**: Calidad de corte deficiente
    """)

    st.markdown("""
    #### **Factor de Carga**

    **Definición:** Relación entre torque resistivo y torque disponible.
    """)

    st.latex(r"FC = \frac{\tau_{resistivo}}{\tau_{input}} \times 100\%")

    st.markdown("""
    **Interpretación:**
    - **FC < 60%**: Sistema subcargado (ineficiente)
    - **60% < FC < 85%**: Carga óptima
    - **FC > 85%**: Sistema sobrecargado (riesgo de parada)
    """)


def show_metrics_calculation():
    """Explica el cálculo e interpretación de métricas"""

    st.markdown("### Cálculo e Interpretación de Métricas")

    st.markdown("""
    #### **Implementación Numérica**

    Las métricas se calculan usando integración numérica discreta:
    """)

    st.code("""
    def compute_metrics(sol, params):
        t = sol.t                         # Vector de tiempo
        omega = sol.y[1]                  # Velocidad angular
        dt = np.diff(t)                  # Diferenciales de tiempo

        # Promedio para integración trapezoidal
        omega_avg = (omega[:-1] + omega[1:]) / 2

        # Energía total
        power_total = params['tau_input'] * omega_avg
        E_total = np.sum(power_total * dt)

        # Energía útil
        if 'tau_grass_func' in params:
            tau_grass_values = [params['tau_grass_func'](t_i) for t_i in t[:-1]]
            power_util = np.array(tau_grass_values) * omega_avg
        else:
            tau_grass = params['k_grass'] * params['rho_veg'] * params['v_avance'] * params['R']
            power_util = tau_grass * omega_avg

        E_util = np.sum(power_util * dt)

        # Área cortada
        A_total = params['w'] * params['v_avance'] * t[-1]

        # Eficiencia
        eta = E_util / E_total if E_total > 0 else 0

        return {
            'E_total': E_total,
            'E_util': E_util,
            'A_total': A_total,
            'eta': eta
        }
    """, language="python")

    st.markdown("""
    #### **Interpretación Conjunta de Métricas**

    **Análisis de Rendimiento Óptimo:**
    """)

    # Crear tabla de interpretación
    interpretation_data = {
        "Métrica": ["Eficiencia (η)", "Velocidad Final", "Estabilidad", "Factor Carga", "Área/Tiempo"],
        "Óptimo": ["> 70%", "85-95% nominal", "< 5% variación", "60-85%", "> 1000 m²/h"],
        "Aceptable": ["50-70%", "70-85% nominal", "5-15% variación", "50-60% o 85-90%", "500-1000 m²/h"],
        "Deficiente": ["< 50%", "< 70% nominal", "> 15% variación", "< 50% o > 90%", "< 500 m²/h"]
    }

    df_interpretation = pd.DataFrame(interpretation_data)
    st.dataframe(df_interpretation, use_container_width=True)

    st.markdown("""
    #### **Diagnóstico de Problemas**

    **Baja Eficiencia (η < 50%):**
    - Verificar fricción viscosa (b) - puede ser excesiva
    - Revisar arrastre aerodinámico (c_drag)
    - Evaluar velocidad de operación
    - Considerar densidad vegetal muy baja

    **Velocidad Final Baja:**
    - Aumentar torque del motor (τ_input)
    - Reducir resistencia vegetal
    - Verificar momento de inercia total
    - Revisar parámetros de fricción

    **Alta Variabilidad:**
    - Aumentar inercia del sistema
    - Suavizar variaciones de vegetación
    - Mejorar control de torque
    - Verificar estabilidad numérica

    **Sobrecarga del Sistema:**
    - Reducir velocidad de avance
    - Aumentar potencia del motor
    - Optimizar geometría de cuchillas
    - Considerar vegetación menos densa
    """)

    st.markdown("""
    #### **Optimización Basada en Métricas**

    **Proceso de optimización:**
    1. **Definir objetivos**: Priorizar métricas según aplicación
    2. **Identificar restricciones**: Límites físicos y operacionales
    3. **Análisis de sensibilidad**: Evaluar impacto de cada parámetro
    4. **Optimización multiobjetivo**: Balancear eficiencia vs. productividad
    5. **Validación**: Verificar resultados en condiciones reales

    **Ejemplo de función objetivo:**
    """)

    st.latex(r"F_{obj} = w_1 \cdot \eta + w_2 \cdot \frac{A_{total}}{T} + w_3 \cdot (1 - \sigma_\omega)")

    st.markdown("""
    Donde w₁, w₂, w₃ son pesos que reflejan la importancia relativa de cada métrica.
    """)


def show_mass_comparison():
    """Muestra la interfaz de comparación masiva usando Configuration Wrapper"""

    st.markdown('<div class="main-header">Comparación Masiva de Configuraciones</div>',
                unsafe_allow_html=True)

    # Botón para volver a la interfaz principal
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Volver a Configuración Individual", use_container_width=True):
            st.session_state.show_comparison = False
            st.session_state.multiple_configs = None
            st.rerun()

    config_manager = st.session_state.multiple_configs

    # Mostrar resumen de configuraciones
    st.markdown("### Resumen de Configuraciones Cargadas")

    # Usar el DataFrame del gestor de configuraciones
    summary_df = config_manager.get_summary_dataframe()
    st.dataframe(summary_df, use_container_width=True)

    # Selector de configuraciones para comparar
    st.markdown("### Seleccionar Configuraciones para Simular")

    config_names = [config.name for config in config_manager]
    selected_configs = st.multiselect(
        "Selecciona las configuraciones a simular:",
        options=config_names,
        default=config_names[:min(5, len(config_names))],  # Máximo 5 por defecto
        help="Selecciona hasta 10 configuraciones para comparar"
    )

    if len(selected_configs) > 10:
        st.warning("Se recomienda seleccionar máximo 10 configuraciones para mejor rendimiento")
        selected_configs = selected_configs[:10]

    # Configuración de simulación común
    st.markdown("### Parámetros de Simulación Común")

    col1, col2, col3 = st.columns(3)
    with col1:
        sim_time = st.number_input("Tiempo de simulación (s)", min_value=1.0, max_value=60.0, value=10.0)
    with col2:
        time_step = st.number_input("Paso de tiempo (s)", min_value=0.001, max_value=0.1, value=0.01, format="%.3f")
    with col3:
        torque_type = st.selectbox(
            "Tipo de torque",
            ["Constante (Modelo Clásico)", "Sinusoidal Temporal", "Escalón Temporal", "Rampa Temporal"]
        )

    # Botón para ejecutar simulaciones
    if st.button("Ejecutar Simulaciones Masivas", use_container_width=True, type="primary"):
        if selected_configs:
            execute_mass_simulations_wrapper(config_manager, selected_configs, sim_time, time_step, torque_type)
        else:
            st.warning("Selecciona al menos una configuración para simular")


def execute_mass_simulations_wrapper(config_manager, selected_names, sim_time, time_step, torque_type):
    """Ejecuta simulaciones masivas usando Configuration Wrapper"""

    st.markdown("### Resultados de Simulaciones Masivas")

    # Configurar función de torque
    torque_func = None
    if torque_type != "Constante (Modelo Clásico)":
        torque_func = create_default_temporal_function(torque_type)

    # Aplicar función de torque a configuraciones seleccionadas
    for config_name in selected_names:
        config = config_manager.get_config_by_name(config_name)
        if config and torque_func:
            config.set_torque_function(torque_func)

    # Ejecutar simulaciones usando el gestor
    sim_kwargs = {
        't_max': sim_time,
        't_eval': np.arange(0, sim_time + time_step, time_step),
        'y0': [0.0, 0.0]
    }

    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Ejecutando simulaciones...")

    try:
        results = config_manager.simulate_all(selected_names, **sim_kwargs)

        progress_bar.progress(1.0)
        status_text.text("Simulaciones completadas!")

        # Debug: mostrar información de resultados
        st.write(f"**Debug**: Se obtuvieron {len(results)} resultados")
        for name, result_data in results.items():
            if 'error' in result_data:
                st.error(f"Error en {name}: {result_data['error']}")
            else:
                st.success(f"Simulación exitosa para {name}")

        # Procesar y mostrar resultados
        if results:
            show_comparison_results_wrapper(results)
        else:
            st.warning("No se pudieron generar resultados válidos.")

    except Exception as e:
        progress_bar.progress(1.0)
        status_text.text("Error en simulaciones!")
        st.error(f"Error durante las simulaciones: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def execute_mass_simulations(all_configs, selected_names, sim_time, time_step, torque_type):
    """Ejecuta simulaciones masivas y muestra resultados comparativos"""

    # Filtrar configuraciones seleccionadas
    selected_configs = [config for config in all_configs if config['name'] in selected_names]

    st.markdown("### Resultados de Simulaciones Masivas")

    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    results = []

    for i, config in enumerate(selected_configs):
        status_text.text(f"Simulando: {config['name']} ({i+1}/{len(selected_configs)})")
        progress_bar.progress((i + 1) / len(selected_configs))

        try:
            # Debug: mostrar configuración que se está procesando
            st.write(f"**Procesando: {config['name']}**")

            # Mostrar configuración cargada
            with st.expander(f"Configuración de {config['name']}"):
                st.json(config)

            # Crear parámetros base desde la configuración
            base_params = create_default_params(
                config.get('mass', 15.0),
                config.get('R', 0.6),
                config.get('tau_input', 200.0)
            )

            st.write(f"Parámetros base creados para {config['name']}")

            # Actualizar con parámetros de la configuración
            updated_count = 0
            for key, value in config.items():
                if key in base_params and key != 'name':
                    base_params[key] = value
                    updated_count += 1

            st.write(f"Actualizados {updated_count} parámetros desde configuración")

            # Configurar función de torque (simplificada para comparación masiva)
            if torque_type == "Constante (Modelo Clásico)":
                tau_grass_func = None
                st.write("Usando torque constante")
            else:
                # Usar valores por defecto para funciones temporales
                tau_grass_func = create_default_temporal_function(torque_type)
                st.write(f"Usando función temporal: {torque_type}")

            # Ejecutar simulación
            try:
                from main_model import simulate_advanced_configuration
                st.write("Función simulate_advanced_configuration importada correctamente")
            except ImportError as ie:
                st.error(f"Error de importación: {ie}")
                raise

            # Preparar parámetros para simulate_advanced_configuration
            final_params = base_params.copy()
            if tau_grass_func is not None:
                final_params['tau_grass_func'] = tau_grass_func

            st.write("Parámetros finales preparados")

            # Mostrar parámetros clave
            key_params = ['mass', 'R', 'tau_input', 'I_plate', 'm_c', 'L']
            st.write("**Parámetros clave:**")
            for param in key_params:
                if param in final_params:
                    st.write(f"  {param}: {final_params[param]}")

            # Usar simulate_advanced_configuration directamente
            st.write("Iniciando simulación...")
            result = simulate_advanced_configuration(
                params=final_params,
                t_max=sim_time,
                t_eval=np.arange(0, sim_time + time_step, time_step),
                y0=[0.0, 0.0]
            )
            st.write("Simulación completada exitosamente")

            # Extraer datos del resultado
            time = result['time']
            omega = result['omega']  # Ya está disponible directamente
            theta = result['theta']  # Ya está disponible directamente

            # Usar las métricas avanzadas que ya están calculadas
            advanced_metrics = result.get('advanced_metrics', {})

            # Extraer métricas con valores por defecto
            energy_total = advanced_metrics.get('E_total', 0)
            efficiency = advanced_metrics.get('eta', 0) * 100  # Convertir a porcentaje
            cut_area = advanced_metrics.get('A_total', 0)
            useful_energy = advanced_metrics.get('E_util', 0)

            # Verificar que tenemos datos válidos
            if len(omega) > 0 and len(time) > 0:
                # Guardar resultado
                result_summary = {
                    'name': config['name'],
                    'final_omega': omega[-1],
                    'max_omega': np.max(omega),
                    'avg_omega': np.mean(omega),
                    'energy_total': energy_total,
                    'efficiency': efficiency,
                    'cut_area': cut_area,
                    'useful_energy': useful_energy,
                    'mass': config.get('mass', 15.0),
                    'tau_input': config.get('tau_input', 200.0),
                    'R': config.get('R', 0.6),
                    'result': {'t': time, 'omega': omega, 'theta': theta}
                }
            else:
                # Datos inválidos, crear resultado con ceros
                result_summary = {
                    'name': config['name'],
                    'final_omega': 0,
                    'max_omega': 0,
                    'avg_omega': 0,
                    'energy_total': 0,
                    'efficiency': 0,
                    'cut_area': 0,
                    'useful_energy': 0,
                    'mass': config.get('mass', 15.0),
                    'tau_input': config.get('tau_input', 200.0),
                    'R': config.get('R', 0.6),
                    'result': {'t': [0], 'omega': [0], 'theta': [0]}
                }
            results.append(result_summary)

        except Exception as e:
            st.error(f"Error en simulación de {config['name']}: {str(e)}")
            # Agregar información de debug
            with st.expander(f"Debug info para {config['name']}"):
                st.write("**Configuración:**")
                st.json(config)
                st.write("**Error:**")
                st.code(str(e))

    status_text.text("Simulaciones completadas!")
    progress_bar.progress(1.0)

    if results:
        show_comparison_results(results)
    else:
        st.warning("No se pudieron generar resultados válidos. Revisa las configuraciones y parámetros.")


def create_default_temporal_function(torque_type):
    """Crea función temporal por defecto para comparación masiva"""
    if torque_type == "Sinusoidal Temporal":
        return lambda t: 50.0 + 30.0 * np.sin(2 * np.pi * 0.5 * t)
    elif torque_type == "Escalón Temporal":
        return lambda t: 50.0 if t < 5.0 else 80.0
    elif torque_type == "Rampa Temporal":
        return lambda t: 50.0 + (80.0 - 50.0) * np.clip((t - 2.0) / (8.0 - 2.0), 0, 1)
    return None


def show_comparison_results_wrapper(results):
    """Muestra los resultados de la comparación masiva usando Configuration Wrapper"""

    # Convertir resultados del wrapper al formato esperado
    converted_results = []

    for config_name, result_data in results.items():
        if 'error' in result_data:
            st.error(f"Error en {config_name}: {result_data['error']}")
            continue

        result = result_data['result']
        summary = result_data['summary']

        # Extraer métricas avanzadas
        advanced_metrics = result.get('advanced_metrics', {})

        converted_result = {
            'name': config_name,
            'final_omega': result['omega'][-1] if len(result['omega']) > 0 else 0,
            'max_omega': np.max(result['omega']) if len(result['omega']) > 0 else 0,
            'avg_omega': np.mean(result['omega']) if len(result['omega']) > 0 else 0,
            'energy_total': advanced_metrics.get('E_total', 0),
            'efficiency': advanced_metrics.get('eta', 0) * 100,
            'cut_area': advanced_metrics.get('A_total', 0),
            'useful_energy': advanced_metrics.get('E_util', 0),
            'mass': summary['mass_total'],
            'tau_input': summary['tau_input'],
            'R': summary['radius'],
            'result': {
                't': result['time'],
                'omega': result['omega'],
                'theta': result['theta']
            }
        }
        converted_results.append(converted_result)

    # Usar la función original con resultados convertidos
    if converted_results:
        show_comparison_results(converted_results)
    else:
        st.warning("No hay resultados válidos para mostrar")


def show_comparison_results(results):
    """Muestra los resultados de la comparación masiva"""

    # Crear DataFrame con resultados
    df_results = pd.DataFrame([
        {
            'Configuración': r['name'],
            'Velocidad Final (rad/s)': f"{r['final_omega']:.2f}",
            'Velocidad Máxima (rad/s)': f"{r['max_omega']:.2f}",
            'Velocidad Promedio (rad/s)': f"{r['avg_omega']:.2f}",
            'Eficiencia (%)': f"{r['efficiency']:.1f}",
            'Área de Corte (m²)': f"{r['cut_area']:.2f}",
            'Energía Total (J)': f"{r['energy_total']:.1f}",
            'Energía Útil (J)': f"{r['useful_energy']:.1f}",
            'Masa (kg)': f"{r['mass']:.1f}",
            'Torque Motor (Nm)': f"{r['tau_input']:.1f}",
            'Radio (m)': f"{r['R']:.2f}"
        }
        for r in results
    ])

    # Mostrar tabla de resultados
    st.markdown("#### Tabla Comparativa de Resultados")
    st.dataframe(df_results, use_container_width=True)

    # Gráficos comparativos
    st.markdown("#### Gráficos Comparativos")

    # Crear gráficos
    if not MATPLOTLIB_AVAILABLE:
        st.error("Matplotlib no está disponible. No se pueden mostrar gráficos.")
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # Gráfico 1: Velocidad angular vs tiempo
    ax1 = axes[0, 0]
    for r in results:
        if len(r['result']['t']) > 0 and len(r['result']['omega']) > 0:
            ax1.plot(r['result']['t'], r['result']['omega'], label=r['name'], linewidth=2)
    ax1.set_xlabel('Tiempo (s)')
    ax1.set_ylabel('Velocidad Angular (rad/s)')
    ax1.set_title('Evolución de Velocidad Angular')
    if len(results) <= 10:  # Solo mostrar leyenda si no hay demasiadas líneas
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Gráfico 2: Eficiencia comparativa
    ax2 = axes[0, 1]
    names = [r['name'] for r in results]
    efficiencies = [max(0, r['efficiency']) for r in results]  # Asegurar valores no negativos

    if len(names) > 0 and any(eff > 0 for eff in efficiencies):
        bars = ax2.bar(range(len(names)), efficiencies, color='skyblue', alpha=0.7)
        ax2.set_xlabel('Configuración')
        ax2.set_ylabel('Eficiencia (%)')
        ax2.set_title('Comparación de Eficiencia')
        ax2.set_xticks(range(len(names)))
        ax2.set_xticklabels(names, rotation=45, ha='right')

        # Agregar valores en las barras
        for bar, eff in zip(bars, efficiencies):
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(height*0.01, 0.5),
                        f'{eff:.1f}%', ha='center', va='bottom')
    else:
        ax2.text(0.5, 0.5, 'Sin datos de eficiencia', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Comparación de Eficiencia - Sin Datos')

    # Gráfico 3: Energía total vs útil
    ax3 = axes[1, 0]
    total_energies = [max(0, r['energy_total']) for r in results]
    useful_energies = [max(0, r['useful_energy']) for r in results]
    x = np.arange(len(names))
    width = 0.35

    if len(names) > 0 and (any(e > 0 for e in total_energies) or any(e > 0 for e in useful_energies)):
        ax3.bar(x - width/2, total_energies, width, label='Energía Total', alpha=0.7)
        ax3.bar(x + width/2, useful_energies, width, label='Energía Útil', alpha=0.7)
        ax3.set_xlabel('Configuración')
        ax3.set_ylabel('Energía (J)')
        ax3.set_title('Comparación Energética')
        ax3.set_xticks(x)
        ax3.set_xticklabels(names, rotation=45, ha='right')
        ax3.legend()
    else:
        ax3.text(0.5, 0.5, 'Sin datos de energía', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Comparación Energética - Sin Datos')

    # Gráfico 4: Área de corte
    ax4 = axes[1, 1]
    cut_areas = [max(0, r['cut_area']) for r in results]

    if len(names) > 0 and any(area > 0 for area in cut_areas):
        bars = ax4.bar(range(len(names)), cut_areas, color='lightgreen', alpha=0.7)
        ax4.set_xlabel('Configuración')
        ax4.set_ylabel('Área de Corte (m²)')
        ax4.set_title('Comparación de Área de Corte')
        ax4.set_xticks(range(len(names)))
        ax4.set_xticklabels(names, rotation=45, ha='right')

        # Agregar valores en las barras
        for bar, area in zip(bars, cut_areas):
            height = bar.get_height()
            if height > 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height + max(height*0.01, 0.01),
                        f'{area:.2f}', ha='center', va='bottom')
    else:
        ax4.text(0.5, 0.5, 'Sin datos de área', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Comparación de Área de Corte - Sin Datos')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Ranking de configuraciones
    st.markdown("#### Ranking de Configuraciones")

    # Filtrar resultados válidos para ranking
    valid_results = [r for r in results if r['efficiency'] > 0 or r['final_omega'] > 0]

    if valid_results:
        # Ranking por eficiencia
        ranking_efficiency = sorted(valid_results, key=lambda x: x['efficiency'], reverse=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top 5 por Eficiencia:**")
            for i, r in enumerate(ranking_efficiency[:5], 1):
                st.write(f"{i}. {r['name']}: {r['efficiency']:.1f}%")

        # Ranking por velocidad final
        ranking_speed = sorted(valid_results, key=lambda x: x['final_omega'], reverse=True)
        with col2:
            st.markdown("**Top 5 por Velocidad Final:**")
            for i, r in enumerate(ranking_speed[:5], 1):
                st.write(f"{i}. {r['name']}: {r['final_omega']:.2f} rad/s")
    else:
        st.warning("No hay resultados válidos para generar rankings.")

    # Exportar resultados
    st.markdown("#### Exportar Resultados de Comparación")

    if st.button("Exportar Tabla Comparativa a CSV", use_container_width=True):
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name=f"comparacion_masiva_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def main():
    """Función principal de la aplicación Streamlit"""

    # CSS personalizado para diseño profesional
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .section-header {
        background: linear-gradient(90deg, #374151 0%, #6b7280 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1.5rem 0;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: white;
        border-radius: 10px;
        color: #475569;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
        transform: translateY(-1px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%) !important;
        color: white !important;
        border: 2px solid #1e40af !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3) !important;
    }

    /* Iconos profesionales */
    .icon-settings::before {
        content: "⚙";
        margin-right: 10px;
        font-size: 1.1em;
        opacity: 0.9;
    }
    .icon-play::before {
        content: "▶";
        margin-right: 10px;
        font-size: 1.1em;
        opacity: 0.9;
    }
    .icon-chart::before {
        content: "";
        margin-right: 10px;
        font-size: 1.1em;
        opacity: 0.9;
    }
    .icon-initial::before {
        content: "";
        margin-right: 10px;
        font-size: 1.1em;
        opacity: 0.9;
    }

    /* Mejoras en botones */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
    }

    /* Mejoras en alertas */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Expanders mejorados */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Título principal
    st.markdown('<div class="main-header">ORC - Sistema de Optimización de Rotary Cutter</div>',
                unsafe_allow_html=True)

    # Inicializar estado de la sesión
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    if 'last_params' not in st.session_state:
        st.session_state.last_params = None
    if 'multiple_configs' not in st.session_state:
        st.session_state.multiple_configs = None
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False
    if 'show_model_explanation' not in st.session_state:
        st.session_state.show_model_explanation = False

    # Verificar si se debe mostrar la explicación del modelo físico
    if st.session_state.show_model_explanation:
        show_physical_model_explanation()
        return

    # Verificar si se debe mostrar la comparación masiva
    if st.session_state.show_comparison and st.session_state.multiple_configs:
        show_mass_comparison()
        return

    # Sidebar para configuración
    with st.sidebar:
        st.markdown('<div class="section-header icon-settings">Configuración del Sistema</div>',
                    unsafe_allow_html=True)

        # Carga de configuración desde archivo
        st.markdown("### Carga de Configuración")

        uploaded_file = st.file_uploader(
            "Cargar configuración",
            type=['xlsx', 'csv'],
            help="Carga parámetros desde archivo Excel (.xlsx) o CSV (.csv)"
        )

        # Botón para descargar archivo de ejemplo
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Descargar Ejemplo CSV", use_container_width=True):
                # Crear archivo de ejemplo
                example_data = """Parametro,Valor
mass,15.0
tau_input,200.0
n_blades,4
R,0.6
omega_ref,60.0
mass_plate_percent,65.0
L_percent,35.0
b,0.25
c_drag,0.06
rho_veg,1.2
v_avance,3.5
k_grass,18.0
w,2.0"""

                st.download_button(
                    label="Descargar",
                    data=example_data,
                    file_name="ejemplo_configuracion.csv",
                    mime="text/csv",
                    help="Descarga un archivo de ejemplo con la estructura correcta"
                )

        # Botón para descargar ejemplo de múltiples configuraciones
        if st.button("Descargar Ejemplo Múltiples Configuraciones", use_container_width=True):
            # Crear archivo de ejemplo con múltiples configuraciones
            multiple_example = """Nombre,mass,tau_input,n_blades,R,omega_ref,rho_veg,v_avance,k_grass,w
Config_Ligera,12.0,180.0,3,0.5,55.0,1.0,3.0,15.0,1.8
Config_Estandar,15.0,200.0,4,0.6,60.0,1.2,3.5,18.0,2.0
Config_Pesada,18.0,220.0,5,0.7,65.0,1.4,4.0,20.0,2.2
Config_Rapida,14.0,250.0,4,0.55,70.0,1.1,4.5,16.0,1.9
Config_Potente,20.0,280.0,6,0.75,75.0,1.5,3.8,22.0,2.4
Config_Eficiente,13.0,190.0,3,0.58,58.0,1.0,3.2,17.0,1.7
Config_Robusta,22.0,300.0,6,0.8,80.0,1.6,4.2,25.0,2.6
Config_Compacta,10.0,160.0,3,0.45,50.0,0.9,2.8,14.0,1.5
Config_Industrial,25.0,350.0,8,0.9,85.0,1.8,4.5,28.0,3.0
Config_Agricola,16.0,210.0,4,0.65,62.0,1.3,3.6,19.0,2.1"""

            st.download_button(
                label="Descargar Ejemplo Múltiple",
                data=multiple_example,
                file_name="ejemplo_multiples_configuraciones.csv",
                mime="text/csv",
                help="Descarga un archivo de ejemplo con múltiples configuraciones para comparación masiva"
            )

        with col2:
            if st.button("Ayuda Formato", use_container_width=True):
                st.info("""
                **Formato del archivo:**
                - **CSV:** Dos columnas (Parametro, Valor)
                - **Excel:** Misma estructura en cualquier hoja
                - **Parámetros soportados:** mass, tau_input, n_blades, R, omega_ref, mass_plate_percent, L_percent, b, c_drag, rho_veg, v_avance, k_grass, w
                """)

        # Procesar archivo cargado
        loaded_params = None
        multiple_configs = None

        if uploaded_file is not None:
            try:
                # Intentar cargar como múltiples configuraciones primero
                multiple_configs = load_multiple_configurations_from_file(uploaded_file)

                if multiple_configs:
                    st.success("Múltiples configuraciones cargadas correctamente")
                    st.info(f"{len(multiple_configs)} configuraciones encontradas")

                    # Mostrar vista previa de configuraciones
                    with st.expander("Vista Previa de Configuraciones"):
                        config_names = [config.name for config in multiple_configs]
                        st.write("**Configuraciones encontradas:**")
                        for i, name in enumerate(config_names, 1):
                            st.write(f"{i}. {name}")

                    # Agregar botón para ir a comparación masiva
                    if st.button("Ir a Comparación Masiva", use_container_width=True):
                        st.session_state.multiple_configs = multiple_configs
                        st.session_state.show_comparison = True
                        st.rerun()

                else:
                    # Intentar cargar como configuración única
                    loaded_params = load_configuration_from_file(uploaded_file)
                    if loaded_params:
                        st.success("Configuración cargada correctamente")
                        st.info(f"{len(loaded_params)} parámetros cargados")
                    else:
                        st.warning("No se encontraron parámetros válidos en el archivo")

            except Exception as e:
                st.error(f"Error al cargar archivo: {str(e)}")

        # Parámetros físicos básicos con organización equilibrada
        st.markdown('<div class="section-header icon-layers">Parámetros Físicos Básicos</div>', unsafe_allow_html=True)

        # Organizar en 3 columnas para mejor balance
        col1, col2, col3 = st.columns(3)

        # Usar parámetros cargados si están disponibles
        mass_default = loaded_params.get('mass', 10.0) if loaded_params else 10.0
        tau_input_default = loaded_params.get('tau_input', 150.0) if loaded_params else 150.0
        n_blades_default = loaded_params.get('n_blades', 2) if loaded_params else 2
        radius_default = loaded_params.get('R', 0.5) if loaded_params else 0.5
        omega_default = loaded_params.get('omega_ref', 50.0) if loaded_params else 50.0
        mass_plate_percent_default = loaded_params.get('mass_plate_percent', 60.0) if loaded_params else 60.0

        with col1:
            mass = st.number_input(
                "Masa Total (kg)",
                min_value=1.0, max_value=1000.0,
                value=float(mass_default), step=0.5,
                help="Masa total aproximada del sistema rotary cutter"
            )

            radius = st.number_input(
                "Radio Principal (m)",
                min_value=0.1, max_value=5.0,
                value=float(radius_default), step=0.05,
                help="Radio principal del rotary cutter"
            )

        with col2:
            tau_input = st.number_input(
                "Torque Motor (Nm)",
                min_value=10.0, max_value=10000.0,
                value=float(tau_input_default), step=10.0,
                help="Torque de entrada del motor"
            )

            n_blades_index = [1, 2, 3, 4, 5, 6, 8, 10, 12].index(n_blades_default) if n_blades_default in [1, 2, 3, 4, 5, 6, 8, 10, 12] else 1
            n_blades = st.selectbox(
                "Número de Cuchillas",
                options=[1, 2, 3, 4, 5, 6, 8, 10, 12],
                index=n_blades_index,
                help="Número de cuchillas del rotary cutter"
            )

        with col3:
            omega_ref = st.slider(
                "Velocidad Angular (rad/s)",
                min_value=1.0, max_value=200.0,
                value=float(omega_default), step=1.0,
                help="Velocidad angular de referencia"
            )

            mass_plate_percent = st.slider(
                "Masa del Plato (%)",
                min_value=10.0, max_value=90.0,
                value=float(mass_plate_percent_default), step=5.0,
                help="Porcentaje de la masa total correspondiente al plato"
            )

        # Parámetros avanzados organizados en una sola sección
        st.markdown('<div class="section-header icon-cpu">Parámetros Dinámicos y de Vegetación</div>', unsafe_allow_html=True)

        # Usar parámetros cargados si están disponibles
        L_percent_default = loaded_params.get('L_percent', 30.0) if loaded_params else 30.0
        b_default = loaded_params.get('b', 0.2) if loaded_params else 0.2
        c_drag_default = loaded_params.get('c_drag', 0.05) if loaded_params else 0.05
        rho_veg_default = loaded_params.get('rho_veg', 1.0) if loaded_params else 1.0
        v_avance_default = loaded_params.get('v_avance', 3.0) if loaded_params else 3.0
        k_grass_default = loaded_params.get('k_grass', 15.0) if loaded_params else 15.0

        # Primera fila: Parámetros dinámicos
        st.markdown("**Parámetros Dinámicos**")
        col1, col2, col3 = st.columns(3)

        with col1:
            L_percent = st.slider(
                "Longitud de cuchilla (%)",
                min_value=10.0, max_value=100.0,
                value=float(L_percent_default), step=5.0,
                help="Longitud de cada cuchilla como porcentaje del radio"
            )

        with col2:
            b = st.number_input(
                "Fricción viscosa",
                min_value=0.0, max_value=10.0,
                value=float(b_default), step=0.05,
                format="%.3f",
                help="Coeficiente de fricción viscosa [N⋅m⋅s/rad]"
            )

        with col3:
            c_drag = st.number_input(
                "Arrastre aerodinámico",
                min_value=0.0, max_value=1.0,
                value=float(c_drag_default), step=0.01,
                format="%.3f",
                help="Coeficiente de arrastre aerodinámico [N⋅m⋅s²/rad²]"
            )

        # Segunda fila: Parámetros de vegetación
        st.markdown("**Parámetros de Vegetación**")
        col1, col2, col3 = st.columns(3)

        with col1:
            rho_veg = st.number_input(
                "Densidad vegetal (kg/m²)",
                min_value=0.1, max_value=10.0,
                value=float(rho_veg_default), step=0.1,
                help="Densidad base de la vegetación"
            )

        with col2:
            v_avance = st.number_input(
                "Velocidad de avance (m/s)",
                min_value=0.1, max_value=20.0,
                value=float(v_avance_default), step=0.1,
                help="Velocidad de avance de la cortadora"
            )

        with col3:
            k_grass = st.number_input(
                "Resistencia vegetal",
                min_value=1.0, max_value=100.0,
                value=float(k_grass_default), step=1.0,
                help="Constante de resistencia de la vegetación [N⋅s/m]"
            )

        # Parámetros calculados automáticamente con layout optimizado
        with st.expander("Parámetros Calculados", expanded=False):
            # Calcular parámetros derivados
            L = radius * (L_percent / 100.0)  # Longitud de cuchilla en metros
            mass_plate = mass * (mass_plate_percent / 100.0)  # Masa del plato
            mass_blades = mass - mass_plate  # Masa total de cuchillas
            m_c = mass_blades / n_blades  # Masa por cuchilla
            I_plate = mass_plate * radius**2 * 0.5  # Momento de inercia del plato (disco)
            w = loaded_params.get('w', 1.8) if loaded_params else 1.8  # Ancho de corte
            v_tip = omega_default * (radius + L)  # Velocidad lineal en la punta

            # Mostrar métricas en 2 filas de 3 columnas para mejor distribución
            st.markdown("**Parámetros Geométricos**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Longitud de cuchilla", f"{L:.3f} m", help="Longitud efectiva de cada cuchilla")

            with col2:
                st.metric("Ancho de corte", f"{w:.1f} m", help="Ancho total de la franja cortada")

            with col3:
                st.metric("Velocidad punta", f"{v_tip:.1f} m/s", help="Velocidad lineal en la punta de las cuchillas")

            st.markdown("**Parámetros Másicos e Inerciales**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Masa del plato", f"{mass_plate:.2f} kg", help="Masa concentrada en el plato central")

            with col2:
                st.metric("Masa por cuchilla", f"{m_c:.2f} kg", help="Masa individual de cada cuchilla")

            with col3:
                st.metric("Momento inercia plato", f"{I_plate:.3f} kg⋅m²", help="Inercia rotacional del plato")

        # Dashboard de estado del sistema
        st.markdown('<div class="section-header icon-database">Estado del Sistema</div>', unsafe_allow_html=True)

        # Crear indicadores de estado
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Validar parámetros básicos
            params_ok = mass > 0 and radius > 0 and tau_input > 0
            status_class = "status-success" if params_ok else "status-error"
            status_icon = '<span class="icon-check"></span>' if params_ok else '<span class="icon-x"></span>'
            st.markdown(f'<div class="status-indicator {status_class}">{status_icon} Parámetros Básicos</div>',
                       unsafe_allow_html=True)

        with col2:
            # Validar configuración dinámica
            dynamics_ok = b >= 0 and c_drag >= 0 and L_percent > 0
            status_class = "status-success" if dynamics_ok else "status-warning"
            status_icon = '<span class="icon-check"></span>' if dynamics_ok else '<span class="icon-alert"></span>'
            st.markdown(f'<div class="status-indicator {status_class}">{status_icon} Dinámicas</div>',
                       unsafe_allow_html=True)

        with col3:
            # Validar vegetación
            veg_ok = rho_veg > 0 and v_avance > 0 and k_grass > 0
            status_class = "status-success" if veg_ok else "status-error"
            status_icon = '<span class="icon-check"></span>' if veg_ok else '<span class="icon-x"></span>'
            st.markdown(f'<div class="status-indicator {status_class}">{status_icon} Vegetación</div>',
                       unsafe_allow_html=True)

        with col4:
            # Estado general del sistema
            system_ok = params_ok and dynamics_ok and veg_ok
            status_class = "status-success" if system_ok else "status-error"
            status_icon = '<span class="icon-check"></span>' if system_ok else '<span class="icon-tool"></span>'
            status_text = "Listo" if system_ok else "Revisar"
            st.markdown(f'<div class="status-indicator {status_class}">{status_icon} Sistema {status_text}</div>',
                       unsafe_allow_html=True)

        # Botón para acceder a la explicación del modelo físico
        st.markdown('<div class="section-header icon-book">Documentación del Modelo</div>', unsafe_allow_html=True)
        if st.button("Ver Explicación del Modelo Físico", use_container_width=True, type="secondary"):
            st.session_state.show_model_explanation = True
            st.rerun()

    # Área principal dividida en tabs con iconos profesionales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Configuración de Torque",
        "Condiciones Iniciales",
        "Simulación",
        "Resultados y Análisis",
        "Análisis de Eficiencia"
    ])

    # Crear parámetros base
    try:
        base_params = {
            'I_plate': I_plate,
            'm_c': m_c,
            'R': radius,
            'L': L,
            'n_blades': n_blades,
            'tau_input': tau_input,
            'b': b,
            'c_drag': c_drag,
            'rho_veg': rho_veg,
            'k_grass': k_grass,
            'v_avance': v_avance,
            'w': w
        }

        # Validar parámetros base
        validate_params(base_params)
        params_valid = True

    except Exception as e:
        st.error(f"Error en parámetros: {str(e)}")
        params_valid = False
        base_params = create_default_params(mass, radius, tau_input)

    # Tab 1: Configuración de Torque
    with tab1:
        configure_torque_tab(base_params, params_valid)

    # Tab 2: Condiciones Iniciales
    with tab2:
        configure_initial_conditions_tab()

    # Tab 3: Simulación
    with tab3:
        simulation_tab(base_params, params_valid)

    # Tab 4: Resultados y Análisis
    with tab4:
        results_analysis_tab()

    # Tab 5: Análisis de Eficiencia
    with tab5:
        efficiency_analysis_tab()

def configure_torque_tab(base_params, params_valid):
    """Configuración del tipo de función de torque resistivo"""

    st.markdown('<div class="section-header icon-settings">Configuración de Torque Resistivo</div>',
                unsafe_allow_html=True)

    if not params_valid:
        st.warning("Corrige los parámetros básicos antes de configurar el torque")
        return

    # Selector del tipo de torque
    torque_type = st.selectbox(
        "Tipo de Función de Torque",
        options=[
            "Constante (Modelo Clásico)",
            "Temporal - Sinusoidal",
            "Temporal - Escalón",
            "Temporal - Rampa",
            "Temporal - Exponencial",
            "Espacial - Zonas Alternadas",
            "Espacial - Parches Gaussianos",
            "Espacial - Transición Sigmoide",
            "Espacial - Sinusoidal",
            "Espacial - Terreno Complejo"
        ],
        index=0,
        help="Selecciona el tipo de función para modelar la resistencia vegetal"
    )

    # Almacenar el tipo seleccionado en session_state
    st.session_state.torque_type = torque_type

    # Configuración específica según el tipo
    if torque_type == "Constante (Modelo Clásico)":
        st.info("Usando el modelo clásico:")
        st.latex(r"\tau_{grass} = k_{grass} \times \rho_{veg} \times v_{avance} \times R")
        st.session_state.tau_grass_func = None

    elif "Temporal" in torque_type:
        configure_temporal_torque(torque_type, base_params)

    elif "Espacial" in torque_type:
        configure_spatial_torque(torque_type, base_params)

def configure_temporal_torque(torque_type, base_params):
    """Configuración de funciones de torque temporal"""

    st.markdown("#### Parámetros de Torque Temporal")

    if "Sinusoidal" in torque_type:
        col1, col2, col3 = st.columns(3)

        with col1:
            amplitude = st.number_input(
                "Amplitud (Nm)",
                min_value=1.0, max_value=100.0,
                value=15.0, step=1.0,
                help="Amplitud de la variación sinusoidal"
            )

        with col2:
            frequency = st.number_input(
                "Frecuencia (Hz)",
                min_value=0.1, max_value=10.0,
                value=0.5, step=0.1,
                help="Frecuencia de la variación"
            )

        with col3:
            offset = st.number_input(
                "Offset (Nm)",
                min_value=5.0, max_value=100.0,
                value=20.0, step=1.0,
                help="Valor base del torque"
            )

        # Crear función y almacenar en session_state
        st.session_state.tau_grass_func = tau_grass_sinusoidal(amplitude, frequency, offset)

        # Mostrar ecuación
        st.markdown("**Ecuación:**")
        st.latex(f"\\tau_{{grass}}(t) = {offset} + {amplitude} \\sin(2\\pi \\cdot {frequency} \\cdot t)")

        # Mostrar preview visual
        with st.expander("Vista Previa de la Función"):
            import matplotlib.pyplot as plt
            t_preview = np.linspace(0, 4/frequency, 200)
            tau_preview = offset + amplitude * np.sin(2 * np.pi * frequency * t_preview)

            fig_preview, ax = plt.subplots(figsize=(8, 3))
            ax.plot(t_preview, tau_preview, 'b-', linewidth=2)
            ax.set_xlabel('Tiempo (s)')
            ax.set_ylabel('τ_grass (Nm)')
            ax.set_title('Vista Previa de la Función de Torque')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig_preview)
            plt.close()

    elif "Escalón" in torque_type:
        col1, col2, col3 = st.columns(3)

        with col1:
            t_change = st.number_input(
                "Tiempo de Cambio (s)",
                min_value=0.1, max_value=10.0,
                value=1.0, step=0.1,
                help="Momento del cambio de torque"
            )

        with col2:
            tau_initial = st.number_input(
                "Torque Inicial (Nm)",
                min_value=1.0, max_value=100.0,
                value=10.0, step=1.0,
                help="Torque antes del cambio"
            )

        with col3:
            tau_final = st.number_input(
                "Torque Final (Nm)",
                min_value=1.0, max_value=100.0,
                value=40.0, step=1.0,
                help="Torque después del cambio"
            )

        st.session_state.tau_grass_func = tau_grass_step(t_change, tau_initial, tau_final)

        # Mostrar descripción
        st.info(f"Torque = {tau_initial} Nm para t < {t_change} s, luego {tau_final} Nm")

    elif "Rampa" in torque_type:
        col1, col2 = st.columns(2)

        with col1:
            t_start = st.number_input(
                "Tiempo Inicio (s)",
                min_value=0.0, max_value=5.0,
                value=0.5, step=0.1,
                help="Inicio de la rampa"
            )

            t_end = st.number_input(
                "Tiempo Final (s)",
                min_value=t_start + 0.1, max_value=10.0,
                value=2.0, step=0.1,
                help="Final de la rampa"
            )

        with col2:
            tau_initial = st.number_input(
                "Torque Inicial (Nm)",
                min_value=1.0, max_value=100.0,
                value=5.0, step=1.0,
                help="Torque al inicio"
            )

            tau_final = st.number_input(
                "Torque Final (Nm)",
                min_value=1.0, max_value=100.0,
                value=35.0, step=1.0,
                help="Torque al final"
            )

        st.session_state.tau_grass_func = tau_grass_ramp(t_start, t_end, tau_initial, tau_final)

        # Mostrar descripción
        st.info(f"Rampa de {tau_initial} a {tau_final} Nm entre t={t_start} y t={t_end} s")

    elif "Exponencial" in torque_type:
        col1, col2, col3 = st.columns(3)

        with col1:
            tau_base = st.number_input(
                "Torque Base (Nm)",
                min_value=1.0, max_value=100.0,
                value=10.0, step=1.0,
                help="Torque inicial"
            )

        with col2:
            tau_max = st.number_input(
                "Torque Máximo (Nm)",
                min_value=tau_base + 1.0, max_value=200.0,
                value=50.0, step=1.0,
                help="Torque asintótico máximo"
            )

        with col3:
            time_constant = st.number_input(
                "Constante Tiempo (s)",
                min_value=0.1, max_value=10.0,
                value=1.0, step=0.1,
                help="Constante de tiempo exponencial"
            )

        st.session_state.tau_grass_func = tau_grass_exponential(tau_base, tau_max, time_constant)

        # Mostrar ecuación
        st.markdown("**Ecuación:**")
        st.latex(f"\\tau_{{grass}}(t) = {tau_base} + {tau_max - tau_base} \\left(1 - e^{{-t/{time_constant}}}\\right)")

        # Mostrar preview visual
        with st.expander("Vista Previa de la Función"):
            import matplotlib.pyplot as plt
            t_preview = np.linspace(0, 5*time_constant, 200)
            tau_preview = tau_base + (tau_max - tau_base) * (1 - np.exp(-t_preview/time_constant))

            fig_preview, ax = plt.subplots(figsize=(8, 3))
            ax.plot(t_preview, tau_preview, 'r-', linewidth=2)
            ax.axhline(y=tau_max, color='r', linestyle='--', alpha=0.7, label=f'Asíntota: {tau_max} Nm')
            ax.set_xlabel('Tiempo (s)')
            ax.set_ylabel('τ_grass (Nm)')
            ax.set_title('Vista Previa de la Función de Torque Exponencial')
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig_preview)
            plt.close()


def configure_spatial_torque(torque_type, base_params):
    """Configuración de funciones de torque espacial"""

    st.markdown("#### Parámetros de Torque Espacial")

    # Parámetros comunes para funciones espaciales
    k_grass = base_params['k_grass']
    R = base_params['R']
    v_avance = base_params['v_avance']

    st.info(f"Usando: k_grass={k_grass} N⋅s/m, R={R} m, v_avance={v_avance} m/s")
    st.markdown("**Modelo Espacial:**")
    st.latex(r"\tau_{grass}(t) = k_{grass} \times \rho(x(t)) \times R")
    st.latex(r"\text{donde } x(t) = v_{avance} \times t")

    if "Zonas Alternadas" in torque_type:
        col1, col2 = st.columns(2)

        with col1:
            zone_length = st.number_input(
                "Longitud de Zona (m)",
                min_value=1.0, max_value=50.0,
                value=10.0, step=1.0,
                help="Longitud de cada zona alternada"
            )

            pattern = st.selectbox(
                "Patrón de Zonas",
                options=["alternating", "low_first", "high_first"],
                index=0,
                help="Patrón de alternancia de las zonas"
            )

        with col2:
            rho_low = st.number_input(
                "Densidad Baja (kg/m²)",
                min_value=0.1, max_value=5.0,
                value=0.5, step=0.1,
                help="Densidad en zonas de vegetación baja"
            )

            rho_high = st.number_input(
                "Densidad Alta (kg/m²)",
                min_value=rho_low + 0.1, max_value=10.0,
                value=2.0, step=0.1,
                help="Densidad en zonas de vegetación densa"
            )

        st.session_state.tau_grass_func = tau_grass_spatial_zones(
            zone_length, rho_low, rho_high, k_grass, R, v_avance, pattern
        )

        # Mostrar descripción
        st.info(f" Zonas de {zone_length}m: ρ = {rho_low} ↔ {rho_high} kg/m² ({pattern})")

    elif "Parches Gaussianos" in torque_type:
        st.markdown("##### Configuración de Parches")

        # Número de parches
        n_patches = st.slider("Número de Parches", min_value=1, max_value=5, value=2)

        centers = []
        amplitudes = []
        widths = []

        for i in range(n_patches):
            col1, col2, col3 = st.columns(3)

            with col1:
                center = st.number_input(
                    f"Centro Parche {i+1} (m)",
                    min_value=0.0, max_value=100.0,
                    value=10.0 + i*15.0, step=1.0,
                    key=f"center_{i}",
                    help=f"Posición central del parche {i+1}"
                )
                centers.append(center)

            with col2:
                amplitude = st.number_input(
                    f"Amplitud {i+1} (kg/m²)",
                    min_value=0.1, max_value=5.0,
                    value=1.5, step=0.1,
                    key=f"amplitude_{i}",
                    help=f"Amplitud de densidad del parche {i+1}"
                )
                amplitudes.append(amplitude)

            with col3:
                width = st.number_input(
                    f"Ancho {i+1} (m)",
                    min_value=0.5, max_value=10.0,
                    value=2.0, step=0.1,
                    key=f"width_{i}",
                    help=f"Ancho característico del parche {i+1}"
                )
                widths.append(width)

        rho_base = st.number_input(
            "Densidad Base (kg/m²)",
            min_value=0.1, max_value=5.0,
            value=0.5, step=0.1,
            help="Densidad base del terreno"
        )

        st.session_state.tau_grass_func = tau_grass_spatial_gaussian_patches(
            centers, amplitudes, widths, rho_base, k_grass, R, v_avance
        )

        # Mostrar descripción
        patch_info = ", ".join([f"x={c}m(A={a:.1f},w={w:.1f})" for c, a, w in zip(centers, amplitudes, widths)])
        st.info(f"Base: {rho_base} kg/m² + Parches: {patch_info}")

    elif "Transición Sigmoide" in torque_type:
        col1, col2 = st.columns(2)

        with col1:
            x_transition = st.number_input(
                "Posición Transición (m)",
                min_value=1.0, max_value=100.0,
                value=15.0, step=1.0,
                help="Posición central de la transición"
            )

            transition_width = st.number_input(
                "Ancho Transición (m)",
                min_value=0.5, max_value=20.0,
                value=3.0, step=0.5,
                help="Ancho de la zona de transición"
            )

        with col2:
            rho_initial = st.number_input(
                "Densidad Inicial (kg/m²)",
                min_value=0.1, max_value=5.0,
                value=0.5, step=0.1,
                help="Densidad antes de la transición"
            )

            rho_final = st.number_input(
                "Densidad Final (kg/m²)",
                min_value=0.1, max_value=10.0,
                value=2.5, step=0.1,
                help="Densidad después de la transición"
            )

        st.session_state.tau_grass_func = tau_grass_spatial_sigmoid_transition(
            x_transition, rho_initial, rho_final, transition_width, k_grass, R, v_avance
        )

        # Mostrar descripción
        st.info(f"Transición en x={x_transition}m: {rho_initial} → {rho_final} kg/m² (ancho: {transition_width}m)")

    elif "Sinusoidal" in torque_type and "Espacial" in torque_type:
        col1, col2 = st.columns(2)

        with col1:
            amplitude = st.number_input(
                "Amplitud (kg/m²)",
                min_value=0.1, max_value=5.0,
                value=1.0, step=0.1,
                help="Amplitud de la variación espacial"
            )

            wavelength = st.number_input(
                "Longitud de Onda (m)",
                min_value=1.0, max_value=100.0,
                value=20.0, step=1.0,
                help="Longitud de onda espacial"
            )

        with col2:
            rho_base = st.number_input(
                "Densidad Base (kg/m²)",
                min_value=0.1, max_value=5.0,
                value=1.5, step=0.1,
                help="Densidad base promedio"
            )

            phase = st.number_input(
                "Fase (rad)",
                min_value=0.0, max_value=2*np.pi,
                value=0.0, step=0.1,
                help="Desfase inicial"
            )

        st.session_state.tau_grass_func = tau_grass_spatial_sinusoidal(
            amplitude, wavelength, rho_base, phase, k_grass, R, v_avance
        )

        # Mostrar ecuación
        st.markdown("**Ecuación de Densidad:**")
        st.latex(f"\\rho(x) = {rho_base} + {amplitude} \\sin\\left(\\frac{{2\\pi x}}{{{wavelength}}} + {phase:.2f}\\right)")

        # Mostrar preview visual
        with st.expander("Vista Previa de la Densidad Espacial"):
            import matplotlib.pyplot as plt
            x_preview = np.linspace(0, 2*wavelength, 200)
            rho_preview = rho_base + amplitude * np.sin(2*np.pi*x_preview/wavelength + phase)

            fig_preview, ax = plt.subplots(figsize=(8, 3))
            ax.plot(x_preview, rho_preview, 'g-', linewidth=2)
            ax.axhline(y=rho_base, color='g', linestyle='--', alpha=0.7, label=f'Base: {rho_base} kg/m²')
            ax.set_xlabel('Posición x (m)')
            ax.set_ylabel('ρ(x) (kg/m²)')
            ax.set_title('Vista Previa de la Densidad Vegetal Espacial')
            ax.grid(True, alpha=0.3)
            ax.legend()
            st.pyplot(fig_preview)
            plt.close()

    elif "Terreno Complejo" in torque_type:
        st.markdown("##### Configuración de Terreno Complejo")

        # Densidad base
        base_density = st.number_input(
            "Densidad Base (kg/m²)",
            min_value=0.1, max_value=5.0,
            value=0.8, step=0.1,
            help="Densidad base del terreno"
        )

        # Configurar parches gaussianos
        st.markdown("**Parches Gaussianos:**")
        n_patches = st.slider("Número de Parches", min_value=0, max_value=3, value=2, key="complex_patches")

        patches = []
        for i in range(n_patches):
            col1, col2, col3 = st.columns(3)
            with col1:
                center = st.number_input(f"Centro {i+1} (m)", value=5.0 + i*10.0, key=f"complex_center_{i}")
            with col2:
                amplitude = st.number_input(f"Amplitud {i+1}", value=1.2, key=f"complex_amp_{i}")
            with col3:
                width = st.number_input(f"Ancho {i+1} (m)", value=2.0, key=f"complex_width_{i}")

            patches.append({'center': center, 'amplitude': amplitude, 'width': width})

        # Configurar zonas rectangulares
        st.markdown("**Zonas Rectangulares:**")
        n_zones = st.slider("Número de Zonas", min_value=0, max_value=3, value=1, key="complex_zones")

        zones = []
        for i in range(n_zones):
            col1, col2, col3 = st.columns(3)
            with col1:
                x_start = st.number_input(f"Inicio {i+1} (m)", value=8.0 + i*5.0, key=f"complex_start_{i}")
            with col2:
                x_end = st.number_input(f"Final {i+1} (m)", value=x_start + 2.0, key=f"complex_end_{i}")
            with col3:
                density_add = st.number_input(f"Densidad Adicional {i+1}", value=1.0, key=f"complex_add_{i}")

            zones.append({'x_start': x_start, 'x_end': x_end, 'density_add': density_add})

        # Configurar tendencias lineales
        st.markdown("**Tendencias Lineales:**")
        n_trends = st.slider("Número de Tendencias", min_value=0, max_value=2, value=1, key="complex_trends")

        trends = []
        for i in range(n_trends):
            col1, col2, col3 = st.columns(3)
            with col1:
                x_start = st.number_input(f"Inicio Tendencia {i+1} (m)", value=15.0 + i*10.0, key=f"complex_trend_start_{i}")
            with col2:
                x_end = st.number_input(f"Final Tendencia {i+1} (m)", value=x_start + 5.0, key=f"complex_trend_end_{i}")
            with col3:
                slope = st.number_input(f"Pendiente {i+1}", value=0.1, key=f"complex_slope_{i}")

            trends.append({'x_start': x_start, 'x_end': x_end, 'slope': slope})

        # Crear configuración del terreno complejo
        terrain_data = {
            'base_density': base_density,
            'patches': patches,
            'zones': zones,
            'trends': trends
        }

        st.session_state.tau_grass_func = tau_grass_spatial_complex_terrain(
            terrain_data, k_grass, R, v_avance
        )

        # Mostrar resumen
        st.info(f"Terreno complejo: Base={base_density}, {len(patches)} parches, {len(zones)} zonas, {len(trends)} tendencias")


def configure_initial_conditions_tab():
    """Configuración de condiciones iniciales"""

    st.markdown('<div class="section-header icon-rocket">Condiciones Iniciales del Sistema</div>',
                unsafe_allow_html=True)

    # Selector del tipo de condiciones iniciales
    initial_type = st.selectbox(
        "Tipo de Condiciones Iniciales",
        options=[
            "Reposo (θ=0, ω=0)",
            "Ángulo Específico",
            "Velocidad Específica (RPM)",
            "Sistema Girando",
            "Ángulo de Cuchillas",
            "Personalizado"
        ],
        index=0,
        help="Selecciona el tipo de condiciones iniciales"
    )

    if initial_type == "Reposo (θ=0, ω=0)":
        st.info("Sistema inicia desde reposo completo")
        st.latex(r"\theta_0 = 0 \text{ rad}, \quad \omega_0 = 0 \text{ rad/s}")
        st.session_state.y0 = [0.0, 0.0]

    elif initial_type == "Ángulo Específico":
        theta0_deg = st.number_input(
            "Ángulo Inicial (grados)",
            min_value=-360.0, max_value=360.0,
            value=0.0, step=15.0,
            help="Ángulo inicial del plato en grados"
        )

        theta0_rad = np.deg2rad(theta0_deg)
        st.session_state.y0 = create_initial_conditions(theta0_rad, 0.0)
        st.info(f"Ángulo inicial: {theta0_deg}° ({theta0_rad:.3f} rad)")

    elif initial_type == "Velocidad Específica (RPM)":
        rpm0 = st.number_input(
            "Velocidad Inicial (RPM)",
            min_value=0.0, max_value=3000.0,
            value=300.0, step=50.0,
            help="Velocidad angular inicial en RPM"
        )

        st.session_state.y0 = initial_conditions_from_rpm(0.0, rpm0)
        omega0 = rpm0 * 2 * np.pi / 60
        st.info(f"Velocidad inicial: {rpm0} RPM ({omega0:.2f} rad/s)")
        st.markdown("**Conversión:**")
        st.latex(f"\\omega_0 = {rpm0} \\times \\frac{{2\\pi}}{{60}} = {omega0:.2f} \\text{{ rad/s}}")

    elif initial_type == "Sistema Girando":
        col1, col2 = st.columns(2)

        with col1:
            omega0 = st.number_input(
                "Velocidad Angular (rad/s)",
                min_value=0.0, max_value=500.0,
                value=50.0, step=5.0,
                help="Velocidad angular inicial en rad/s"
            )

        with col2:
            revolutions = st.number_input(
                "Revoluciones Completadas",
                min_value=0.0, max_value=10.0,
                value=0.0, step=0.25,
                help="Número de revoluciones ya completadas"
            )

        st.session_state.y0 = initial_conditions_spinning(omega0, revolutions)
        rpm = omega0 * 60 / (2 * np.pi)
        theta0 = revolutions * 2 * np.pi
        st.info(f"Sistema girando: {omega0:.2f} rad/s ({rpm:.1f} RPM), {revolutions} revoluciones")
        st.markdown("**Condiciones Iniciales:**")
        st.latex(f"\\theta_0 = {revolutions} \\times 2\\pi = {theta0:.2f} \\text{{ rad}}")
        st.latex(f"\\omega_0 = {omega0:.2f} \\text{{ rad/s}}")

    elif initial_type == "Ángulo de Cuchillas":
        col1, col2 = st.columns(2)

        with col1:
            blade_angle_deg = st.number_input(
                "Ángulo de Cuchillas (°)",
                min_value=0.0, max_value=360.0,
                value=45.0, step=15.0,
                help="Ángulo de las cuchillas en grados"
            )

        with col2:
            omega0 = st.number_input(
                "Velocidad Inicial (rad/s)",
                min_value=0.0, max_value=100.0,
                value=0.0, step=1.0,
                help="Velocidad angular inicial"
            )

        st.session_state.y0 = initial_conditions_blade_angle(blade_angle_deg, omega0)
        st.info(f"Cuchillas a {blade_angle_deg}°, velocidad: {omega0:.2f} rad/s")

    elif initial_type == "Personalizado":
        col1, col2 = st.columns(2)

        with col1:
            theta0 = st.number_input(
                "Ángulo θ₀ (rad)",
                min_value=-100.0, max_value=100.0,
                value=0.0, step=0.1,
                help="Ángulo inicial en radianes"
            )

        with col2:
            omega0 = st.number_input(
                "Velocidad ω₀ (rad/s)",
                min_value=-1000.0, max_value=1000.0,
                value=0.0, step=1.0,
                help="Velocidad angular inicial en rad/s"
            )

        try:
            st.session_state.y0 = create_initial_conditions(theta0, omega0)
            theta0_deg = np.rad2deg(theta0)
            rpm = omega0 * 60 / (2 * np.pi)
            st.success(f"Condiciones válidas: θ₀={theta0:.3f} rad ({theta0_deg:.1f}°), ω₀={omega0:.2f} rad/s ({rpm:.1f} RPM)")
        except ValueError as e:
            st.error(f"Error en condiciones iniciales: {e}")
            st.session_state.y0 = [0.0, 0.0]


def simulation_tab(base_params, params_valid):
    """Tab de simulación"""

    st.markdown('<div class="section-header icon-play">Ejecutar Simulación</div>',
                unsafe_allow_html=True)

    # Mostrar ecuaciones principales del modelo
    with st.expander("Ecuaciones del Modelo Físico"):
        st.markdown("#### Sistema de Ecuaciones Diferenciales")
        st.latex(r"\frac{d\theta}{dt} = \omega")
        st.latex(r"\frac{d\omega}{dt} = \frac{\tau_{input} - \tau_{friction} - \tau_{drag} - \tau_{grass}}{I_{total}}")

        st.markdown("#### Componentes del Torque")
        st.latex(r"\tau_{friction} = b \cdot \omega")
        st.latex(r"\tau_{drag} = c_{drag} \cdot \omega^2 \cdot \text{sign}(\omega)")
        st.latex(r"\tau_{grass} = k_{grass} \cdot \rho_{veg} \cdot v_{avance} \cdot R \text{ (modelo clásico)}")

        st.markdown("#### Momento de Inercia Total")
        st.latex(r"I_{total} = I_{plate} + n_{blades} \cdot m_c \cdot (R + L)^2")

    if not params_valid:
        st.error("Corrige los parámetros básicos antes de ejecutar la simulación")
        return

    # Parámetros de simulación
    col1, col2, col3 = st.columns(3)

    with col1:
        T_end = st.number_input(
            "Tiempo Final (s)",
            min_value=0.5, max_value=60.0,
            value=5.0, step=0.5,
            help="Duración total de la simulación"
        )

    with col2:
        dt = st.number_input(
            "Paso de Tiempo (s)",
            min_value=0.001, max_value=0.1,
            value=0.01, step=0.001,
            format="%.3f",
            help="Paso de tiempo para la integración"
        )

    with col3:
        st.markdown("#### Opciones de Análisis")
        compute_advanced_metrics = st.checkbox(
            "Métricas Avanzadas",
            value=True,
            help="Calcular métricas de eficiencia y corte"
        )

    # Botón de simulación
    if st.button("Ejecutar Simulación", type="primary", use_container_width=True):
        run_simulation_process(base_params, T_end, dt, compute_advanced_metrics)


def run_simulation_process(base_params, T_end, dt, compute_advanced_metrics):
    """Ejecuta el proceso de simulación"""

    # Crear barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Preparando parámetros...")
        progress_bar.progress(10)

        # Preparar parámetros finales
        final_params = base_params.copy()

        # Agregar función de torque si existe
        if hasattr(st.session_state, 'tau_grass_func') and st.session_state.tau_grass_func is not None:
            final_params['tau_grass_func'] = st.session_state.tau_grass_func

        # Obtener condiciones iniciales
        y0 = getattr(st.session_state, 'y0', None)

        status_text.text("Validando parámetros...")
        progress_bar.progress(20)

        # Validar parámetros finales
        validate_params(final_params)

        status_text.text("Ejecutando simulación...")
        progress_bar.progress(40)

        # Ejecutar simulación
        # Calcular masa total aproximada del sistema
        # masa_total = masa_cuchillas + masa_plato_estimada
        mass_total = base_params['m_c'] * base_params['n_blades'] + base_params['I_plate'] / (0.5 * base_params['R']**2)

        results = run_simulation(
            mass=mass_total,
            radius=base_params['R'],
            omega=None,
            T_end=T_end,
            dt=dt,
            advanced_params=final_params,
            y0=y0
        )

        progress_bar.progress(70)
        status_text.text("Calculando métricas...")

        # Calcular métricas avanzadas si se solicita
        if compute_advanced_metrics:
            try:
                performance = analyze_performance(results)
                results['performance_analysis'] = performance
            except Exception as e:
                st.warning(f"No se pudieron calcular todas las métricas de rendimiento: {e}")

        progress_bar.progress(90)
        status_text.text("Simulación completada")

        # Almacenar resultados en session_state
        st.session_state.simulation_results = results
        st.session_state.last_params = final_params.copy()

        progress_bar.progress(100)
        status_text.text("¡Simulación exitosa! Ve a la pestaña 'Resultados y Análisis'")

        # Mostrar resumen rápido
        st.success("Simulación completada exitosamente")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Velocidad Final",
                f"{results['omega'][-1]:.2f} rad/s",
                f"{results['omega'][-1] * 60 / (2*np.pi):.1f} RPM"
            )

        with col2:
            st.metric(
                "Torque Máximo",
                f"{results['statistics']['torque_max']:.2f} Nm"
            )

        with col3:
            st.metric(
                "Energía Promedio",
                f"{results['statistics']['energy_avg']:.1f} J"
            )

        with col4:
            if 'advanced_metrics' in results:
                st.metric(
                    "Eficiencia de Corte",
                    f"{results['advanced_metrics']['eta']*100:.2f}%"
                )
            else:
                st.metric("Puntos de Integración", f"{len(results['time'])}")

    except Exception as e:
        progress_bar.progress(0)
        status_text.text("")
        st.error(f"Error en la simulación: {str(e)}")

        # Mostrar detalles del error en un expander
        with st.expander("Detalles del Error"):
            st.code(str(e))

            # Sugerencias de solución
            st.markdown("**Posibles soluciones:**")
            st.markdown("- Verifica que todos los parámetros sean válidos")
            st.markdown("- Reduce el tiempo de simulación o aumenta el paso de tiempo")
            st.markdown("- Revisa la configuración de la función de torque")
            st.markdown("- Verifica las condiciones iniciales")


def results_analysis_tab():
    """Tab de resultados y análisis"""

    st.markdown('<div class="section-header icon-chart">Resultados y Análisis</div>',
                unsafe_allow_html=True)

    if st.session_state.simulation_results is None:
        st.info("Ejecuta una simulación para ver los resultados aquí")
        return

    # Mostrar resultados
    display_simulation_results()


def display_simulation_results():
    """Muestra los resultados de la simulación con gráficos y métricas"""

    results = st.session_state.simulation_results

    # Información general de la simulación
    st.markdown("### Información General")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Duración Simulación",
            f"{results['time'][-1]:.2f} s"
        )

    with col2:
        st.metric(
            "Puntos de Datos",
            f"{len(results['time'])}"
        )

    with col3:
        st.metric(
            "Momento de Inercia",
            f"{results['moment_of_inertia']:.4f} kg⋅m²"
        )

    with col4:
        if 'initial_theta' in results['statistics']:
            theta0_deg = np.rad2deg(results['statistics']['initial_theta'])
            st.metric(
                "Condiciones Iniciales",
                f"θ₀={theta0_deg:.1f}°",
                f"ω₀={results['statistics']['initial_omega']:.1f} rad/s"
            )
        else:
            st.metric("Paso de Tiempo", f"{results['statistics']['time_step']:.3f} s")

    # Métricas principales
    st.markdown("### Métricas Principales")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        omega_final = results['omega'][-1]
        rpm_final = omega_final * 60 / (2 * np.pi)
        st.metric(
            "Velocidad Final",
            f"{omega_final:.2f} rad/s",
            f"{rpm_final:.1f} RPM"
        )

    with col2:
        st.metric(
            "Torque Máximo",
            f"{results['statistics']['torque_max']:.2f} Nm"
        )

    with col3:
        st.metric(
            "Torque RMS",
            f"{results['statistics']['torque_rms']:.2f} Nm"
        )

    with col4:
        st.metric(
            "Energía Promedio",
            f"{results['statistics']['energy_avg']:.1f} J"
        )

    with col5:
        st.metric(
            "Trabajo Total",
            f"{results['work_total']:.1f} J"
        )

    # Métricas avanzadas si están disponibles
    if 'advanced_metrics' in results:
        st.markdown("### Métricas Avanzadas de Corte")

        adv = results['advanced_metrics']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Eficiencia de Corte",
                f"{adv['eta']*100:.2f}%"
            )

        with col2:
            st.metric(
                "Energía Total",
                f"{adv['E_total']:.1f} J"
            )

        with col3:
            st.metric(
                "Energía Útil",
                f"{adv['E_util']:.1f} J"
            )

        with col4:
            st.metric(
                "Área Cortada",
                f"{adv['A_total']:.2f} m²"
            )

    # Análisis de rendimiento si está disponible
    if 'performance_analysis' in results:
        st.markdown("### Análisis de Rendimiento")

        perf = results['performance_analysis']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Eficiencia Básica",
                f"{perf['efficiency']:.4f}"
            )

        with col2:
            st.metric(
                "Estabilidad ω",
                f"{perf['omega_stability']:.4f}"
            )

        with col3:
            st.metric(
                "Estabilidad τ",
                f"{perf['torque_stability']:.4f}"
            )

        with col4:
            st.metric(
                "Potencia Promedio",
                f"{perf['avg_power']:.1f} W"
            )

    # Gráficos principales
    create_simulation_plots(results)

    # Exportación de datos
    st.markdown("### Exportar Resultados")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Exportar a CSV", use_container_width=True):
            export_to_csv(results)

    with col2:
        if st.button("Exportar a Excel", use_container_width=True):
            export_to_excel(results)

    with col3:
        if st.button("Copiar Resumen", use_container_width=True):
            copy_summary_to_clipboard(results)


def create_simulation_plots(results):
    """Crea gráficos interactivos de los resultados de simulación"""

    st.markdown("### Gráficos de Resultados")

    time = results['time']
    omega = results['omega']
    theta = results['theta']
    torque = results['torque']
    kinetic_energy = results['kinetic_energy']
    power = results['power']

    # Gráfico 1: Velocidad Angular vs Tiempo
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=time, y=omega,
        mode='lines',
        name='ω(t)',
        line=dict(color='#1e3a8a', width=3),
        hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>ω:</b> %{y:.2f} rad/s<extra></extra>'
    ))

    # Agregar línea de RPM en eje secundario
    rpm = omega * 60 / (2 * np.pi)
    fig1.add_trace(go.Scatter(
        x=time, y=rpm,
        mode='lines',
        name='RPM',
        line=dict(color='#3b82f6', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>RPM:</b> %{y:.1f}<extra></extra>'
    ))

    fig1.update_layout(
        title='Velocidad Angular vs Tiempo',
        xaxis_title='Tiempo (s)',
        yaxis_title='Velocidad Angular (rad/s)',
        yaxis2=dict(
            title='RPM',
            overlaying='y',
            side='right',
            color='#3b82f6'
        ),
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Torque vs Tiempo
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=time, y=torque,
        mode='lines',
        name='τ(t)',
        line=dict(color='#475569', width=3),
        hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>Torque:</b> %{y:.2f} Nm<extra></extra>'
    ))

    # Agregar línea de torque promedio
    torque_avg = np.mean(torque)
    fig2.add_hline(
        y=torque_avg,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Promedio: {torque_avg:.2f} Nm"
    )

    fig2.update_layout(
        title='Torque vs Tiempo',
        xaxis_title='Tiempo (s)',
        yaxis_title='Torque (Nm)',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3: Energía y Potencia
    fig3 = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Energía vs Tiempo', 'Potencia vs Tiempo'),
        vertical_spacing=0.1
    )

    # Energía Cinética
    fig3.add_trace(
        go.Scatter(
            x=time, y=kinetic_energy,
            mode='lines',
            name='Energía Cinética',
            line=dict(color='#1e3a8a', width=3),
            hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>Energía:</b> %{y:.1f} J<extra></extra>'
        ),
        row=1, col=1
    )

    # Potencia
    fig3.add_trace(
        go.Scatter(
            x=time, y=power,
            mode='lines',
            name='Potencia',
            line=dict(color='#3b82f6', width=3),
            hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>Potencia:</b> %{y:.1f} W<extra></extra>'
        ),
        row=2, col=1
    )

    fig3.update_xaxes(title_text="Tiempo (s)", row=2, col=1)
    fig3.update_yaxes(title_text="Energía (J)", row=1, col=1)
    fig3.update_yaxes(title_text="Potencia (W)", row=2, col=1)

    fig3.update_layout(
        height=600,
        hovermode='x unified',
        showlegend=False
    )

    st.plotly_chart(fig3, use_container_width=True)

    # Gráfico 4: Diagrama de Fase (ω vs θ)
    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=theta, y=omega,
        mode='lines+markers',
        name='Trayectoria',
        line=dict(color='#475569', width=3),
        marker=dict(size=4, color='#64748b'),
        hovertemplate='<b>θ:</b> %{x:.3f} rad<br><b>ω:</b> %{y:.2f} rad/s<extra></extra>'
    ))

    # Marcar punto inicial y final
    fig4.add_trace(go.Scatter(
        x=[theta[0]], y=[omega[0]],
        mode='markers',
        name='Inicio',
        marker=dict(color='#22c55e', size=12, symbol='circle'),
        hovertemplate='<b>Inicio:</b><br>θ₀=%{x:.3f} rad<br>ω₀=%{y:.2f} rad/s<extra></extra>'
    ))

    fig4.add_trace(go.Scatter(
        x=[theta[-1]], y=[omega[-1]],
        mode='markers',
        name='Final',
        marker=dict(color='#ef4444', size=12, symbol='square'),
        hovertemplate='<b>Final:</b><br>θf=%{x:.3f} rad<br>ωf=%{y:.2f} rad/s<extra></extra>'
    ))

    fig4.update_layout(
        title='Diagrama de Fase (ω vs θ)',
        xaxis_title='Ángulo θ (rad)',
        yaxis_title='Velocidad Angular ω (rad/s)',
        height=400
    )

    st.plotly_chart(fig4, use_container_width=True)


def export_to_csv(results):
    """Exporta los resultados a formato CSV"""

    # Crear DataFrame con los datos principales
    df = pd.DataFrame({
        'Tiempo_s': results['time'],
        'Angulo_rad': results['theta'],
        'Velocidad_Angular_rad_s': results['omega'],
        'Velocidad_Angular_RPM': results['omega'] * 60 / (2 * np.pi),
        'Torque_Nm': results['torque'],
        'Energia_J': results['energy'],
        'Potencia_W': results['power']
    })

    # Convertir a CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_data = csv_buffer.getvalue()

    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulacion_rotary_cutter_{timestamp}.csv"

    # Botón de descarga
    st.download_button(
        label="⬇️ Descargar CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        help="Descarga los datos de la simulación en formato CSV"
    )

    st.success(f"Archivo CSV preparado: {filename}")


def export_to_excel(results):
    """Exporta los resultados a formato Excel con múltiples hojas"""

    # Crear buffer para Excel
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:

        # Hoja 1: Datos principales
        df_main = pd.DataFrame({
            'Tiempo_s': results['time'],
            'Angulo_rad': results['theta'],
            'Velocidad_Angular_rad_s': results['omega'],
            'Velocidad_Angular_RPM': results['omega'] * 60 / (2 * np.pi),
            'Torque_Nm': results['torque'],
            'Energia_J': results['energy'],
            'Potencia_W': results['power']
        })
        df_main.to_excel(writer, sheet_name='Datos_Simulacion', index=False)

        # Hoja 2: Estadísticas
        stats_data = []
        for key, value in results['statistics'].items():
            if isinstance(value, (int, float)):
                stats_data.append({'Metrica': key, 'Valor': value})

        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)

        # Hoja 3: Métricas avanzadas (si existen)
        if 'advanced_metrics' in results:
            adv_data = []
            for key, value in results['advanced_metrics'].items():
                if isinstance(value, (int, float)):
                    adv_data.append({'Metrica_Avanzada': key, 'Valor': value})

            df_adv = pd.DataFrame(adv_data)
            df_adv.to_excel(writer, sheet_name='Metricas_Avanzadas', index=False)

        # Hoja 4: Parámetros de simulación
        if hasattr(st.session_state, 'last_params') and st.session_state.last_params:
            params_data = []
            for key, value in st.session_state.last_params.items():
                if isinstance(value, (int, float, str)):
                    params_data.append({'Parametro': key, 'Valor': value})

            df_params = pd.DataFrame(params_data)
            df_params.to_excel(writer, sheet_name='Parametros', index=False)

    excel_data = excel_buffer.getvalue()

    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulacion_rotary_cutter_{timestamp}.xlsx"

    # Botón de descarga
    st.download_button(
        label="⬇ Descargar Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Descarga los datos de la simulación en formato Excel con múltiples hojas"
    )

    st.success(f"Archivo Excel preparado: {filename}")


def copy_summary_to_clipboard(results):
    """Crea un resumen de texto para copiar al portapapeles"""

    # Crear resumen de texto
    summary = f"""
=== RESUMEN DE SIMULACIÓN ROTARY CUTTER ===
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PARÁMETROS PRINCIPALES:
- Duración: {results['time'][-1]:.2f} s
- Puntos de datos: {len(results['time'])}
- Momento de inercia: {results['moment_of_inertia']:.4f} kg⋅m²

RESULTADOS PRINCIPALES:
- Velocidad final: {results['omega'][-1]:.2f} rad/s ({results['omega'][-1] * 60 / (2*np.pi):.1f} RPM)
- Torque máximo: {results['statistics']['torque_max']:.2f} Nm
- Torque RMS: {results['statistics']['torque_rms']:.2f} Nm
- Energía promedio: {results['statistics']['energy_avg']:.1f} J
- Trabajo total: {results['work_total']:.1f} J
"""

    # Agregar métricas avanzadas si existen
    if 'advanced_metrics' in results:
        adv = results['advanced_metrics']
        summary += f"""
MÉTRICAS AVANZADAS:
- Eficiencia de corte: {adv['eta']*100:.2f}%
- Energía total: {adv['E_total']:.1f} J
- Energía útil: {adv['E_util']:.1f} J
- Área cortada: {adv['A_total']:.2f} m²
"""

    # Agregar análisis de rendimiento si existe
    if 'performance_analysis' in results:
        perf = results['performance_analysis']
        summary += f"""
ANÁLISIS DE RENDIMIENTO:
- Eficiencia básica: {perf['efficiency']:.4f}
- Estabilidad ω: {perf['omega_stability']:.4f}
- Estabilidad τ: {perf['torque_stability']:.4f}
- Potencia promedio: {perf['avg_power']:.1f} W
"""

    summary += "\n=== FIN DEL RESUMEN ==="

    # Mostrar el resumen en un área de texto para que el usuario pueda copiarlo
    st.text_area(
        "Resumen para Copiar",
        value=summary,
        height=300,
        help="Selecciona todo el texto y cópialo (Ctrl+A, Ctrl+C)"
    )

    st.info("Selecciona todo el texto del área superior y cópialo con Ctrl+A y Ctrl+C")


def efficiency_analysis_tab():
    """Tab de análisis avanzado de eficiencia"""

    st.markdown('<div class="section-header icon-efficiency">Análisis Avanzado de Eficiencia</div>',
                unsafe_allow_html=True)

    if st.session_state.simulation_results is None:
        st.info("Ejecuta una simulación para ver el análisis de eficiencia aquí")

        # Mostrar guía de interpretación mientras no hay datos
        with st.expander("Guía de Interpretación de Eficiencia", expanded=True):
            st.markdown('<div class="icon-guide">Fundamentos de Eficiencia Energética</div>', unsafe_allow_html=True)
            st.markdown("""
            ### ¿Qué es la Eficiencia en un Rotary Cutter?

            La **eficiencia energética** mide qué porcentaje de la energía total del motor
            se utiliza efectivamente para cortar vegetación:

            **Eficiencia (%) = (Potencia Útil / Potencia Total) × 100**

            #### Rangos de Eficiencia:
            """)

            # Professional status indicators instead of emojis
            st.markdown("""
            <div class="status-indicator status-excellent">Alta (>80%): Excelente aprovechamiento energético</div>
            <div class="status-indicator status-good">Media (60-80%): Rendimiento aceptable, puede optimizarse</div>
            <div class="status-indicator status-poor">Baja (<60%): Ineficiente, requiere ajustes</div>
            """, unsafe_allow_html=True)

            st.markdown("""
            #### Factores que Afectan la Eficiencia:
            - **Densidad de vegetación**: Mayor densidad → Mayor resistencia útil
            - **Velocidad de avance**: Velocidad óptima maximiza eficiencia
            - **Configuración de cuchillas**: Número y geometría influyen
            - **Condiciones del terreno**: Variaciones espaciales afectan rendimiento
            """)
        return

    results = st.session_state.simulation_results

    # Verificar que tenemos métricas avanzadas
    if 'advanced_metrics' not in results:
        st.warning("Las métricas avanzadas no están disponibles para esta simulación")
        return

    advanced_metrics = results['advanced_metrics']

    # Verificar que tenemos las nuevas métricas de eficiencia
    if 'efficiency_instantaneous' not in advanced_metrics:
        st.warning("Las métricas de eficiencia detalladas no están disponibles. Ejecuta una nueva simulación.")
        return

    # Mostrar análisis de eficiencia
    display_efficiency_analysis(results, advanced_metrics)


def display_efficiency_analysis(results, advanced_metrics):
    """Muestra el análisis completo de eficiencia con todos los gráficos"""

    # Extraer datos necesarios
    time = advanced_metrics['time_series']
    power_total = advanced_metrics['power_total_series']
    power_util = advanced_metrics['power_util_series']
    efficiency_inst = advanced_metrics['efficiency_instantaneous']
    efficiency_avg = advanced_metrics['efficiency_average']

    # === MÉTRICAS CLAVE ===
    st.markdown('<div class="section-header icon-efficiency">Métricas Clave de Eficiencia</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Eficiencia Promedio",
            f"{efficiency_avg:.1f}%",
            delta=f"{efficiency_avg - 70:.1f}%" if efficiency_avg > 70 else f"{efficiency_avg - 70:.1f}%"
        )

    with col2:
        st.metric(
            "Eficiencia Máxima",
            f"{advanced_metrics['efficiency_peak']:.1f}%"
        )

    with col3:
        st.metric(
            "Eficiencia Mínima",
            f"{advanced_metrics['efficiency_min']:.1f}%"
        )

    with col4:
        energy_efficiency = (advanced_metrics['E_util'] / advanced_metrics['E_total']) * 100
        st.metric(
            "Eficiencia Energética Total",
            f"{energy_efficiency:.1f}%"
        )

    # === GRÁFICO 1: POTENCIA TOTAL VS ÚTIL ===
    st.markdown('<div class="section-header icon-power">Potencia Total vs Potencia Útil</div>', unsafe_allow_html=True)

    fig_power = go.Figure()

    # Potencia total
    fig_power.add_trace(go.Scatter(
        x=time, y=power_total,
        mode='lines',
        name='Potencia Total',
        line=dict(color='#ef4444', width=3),
        hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>Potencia Total:</b> %{y:.1f} W<extra></extra>'
    ))

    # Potencia útil
    fig_power.add_trace(go.Scatter(
        x=time, y=power_util,
        mode='lines',
        name='Potencia Útil',
        line=dict(color='#10b981', width=3),
        yaxis='y2',
        hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>Potencia Útil:</b> %{y:.1f} W<extra></extra>'
    ))

    fig_power.update_layout(
        title='Evolución de Potencia Total y Útil',
        xaxis_title='Tiempo (s)',
        yaxis=dict(
            title='Potencia Total (W)',
            side='left',
            color='#ef4444'
        ),
        yaxis2=dict(
            title='Potencia Útil (W)',
            side='right',
            overlaying='y',
            color='#10b981'
        ),
        hovermode='x unified',
        height=400,
        legend=dict(x=0.02, y=0.98)
    )

    st.plotly_chart(fig_power, use_container_width=True)

    # === GRÁFICO 2: EFICIENCIA INSTANTÁNEA ===
    st.markdown('<div class="section-header icon-trend">Eficiencia Instantánea</div>', unsafe_allow_html=True)

    fig_eff = go.Figure()

    # Eficiencia instantánea
    fig_eff.add_trace(go.Scatter(
        x=time, y=efficiency_inst,
        mode='lines',
        name='Eficiencia Instantánea',
        line=dict(color='#3b82f6', width=3),
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.1)',
        hovertemplate='<b>Tiempo:</b> %{x:.3f} s<br><b>Eficiencia:</b> %{y:.1f}%<extra></extra>'
    ))

    # Línea de eficiencia promedio
    fig_eff.add_hline(
        y=efficiency_avg,
        line_dash="dash",
        line_color="#1e40af",
        line_width=2,
        annotation_text=f"Promedio: {efficiency_avg:.1f}%",
        annotation_position="top right"
    )

    # Líneas de referencia para rangos de eficiencia
    fig_eff.add_hline(y=80, line_dash="dot", line_color="#10b981", opacity=0.7,
                     annotation_text="Alta Eficiencia (80%)", annotation_position="left")
    fig_eff.add_hline(y=60, line_dash="dot", line_color="#f59e0b", opacity=0.7,
                     annotation_text="Eficiencia Media (60%)", annotation_position="left")

    fig_eff.update_layout(
        title='Eficiencia Instantánea vs Tiempo',
        xaxis_title='Tiempo (s)',
        yaxis_title='Eficiencia (%)',
        yaxis=dict(range=[0, min(100, max(efficiency_inst) * 1.1)]),
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig_eff, use_container_width=True)

    # === GRÁFICO 3: DISTRIBUCIÓN DE ENERGÍA (PIE CHART) ===
    st.markdown('<div class="section-header icon-pie">Distribución de Energía</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Datos para el pie chart
        energy_useful = advanced_metrics['E_util']
        energy_losses = advanced_metrics['E_losses']

        fig_pie = go.Figure(data=[go.Pie(
            labels=['Energía Útil', 'Pérdidas'],
            values=[energy_useful, energy_losses],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444'],
            textinfo='label+percent+value',
            texttemplate='<b>%{label}</b><br>%{percent}<br>%{value:.1f} J',
            hovertemplate='<b>%{label}</b><br>Energía: %{value:.1f} J<br>Porcentaje: %{percent}<extra></extra>'
        )])

        fig_pie.update_layout(
            title='Distribución de Energía Total',
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown('<div class="icon-summary">Resumen Energético</div>', unsafe_allow_html=True)

        total_energy = advanced_metrics['E_total']
        useful_percent = (energy_useful / total_energy) * 100
        losses_percent = (energy_losses / total_energy) * 100

        st.metric("Energía Total", f"{total_energy:.1f} J")
        st.metric("Energía Útil", f"{energy_useful:.1f} J", f"{useful_percent:.1f}%")
        st.metric("Pérdidas", f"{energy_losses:.1f} J", f"{losses_percent:.1f}%")

        # Professional status indicators instead of emojis
        if useful_percent > 80:
            st.markdown('<div class="status-indicator status-excellent">Excelente aprovechamiento energético</div>', unsafe_allow_html=True)
        elif useful_percent > 60:
            st.markdown('<div class="status-indicator status-good">Aprovechamiento moderado</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-poor">Bajo aprovechamiento energético</div>', unsafe_allow_html=True)

    # === GRÁFICO 4: MÉTRICAS DE RENDIMIENTO (BAR CHART) ===
    st.markdown('<div class="section-header icon-metrics">Métricas de Rendimiento</div>', unsafe_allow_html=True)

    # Preparar datos para el gráfico de barras
    metrics_names = [
        'Eficiencia Promedio (%)',
        'Eficiencia Máxima (%)',
        'Potencia Pico (W)',
        'Potencia Útil Pico (W)',
        'Tiempo Alta Eficiencia (%)',
        'Área Cortada (m²)'
    ]

    metrics_values = [
        efficiency_avg,
        advanced_metrics['efficiency_peak'],
        advanced_metrics['power_peak'],
        advanced_metrics['power_util_peak'],
        advanced_metrics['high_efficiency_time_percent'],
        advanced_metrics['A_total']
    ]

    # Normalizar valores para visualización (escalar a 0-100)
    normalized_values = []
    for i, value in enumerate(metrics_values):
        if i < 2 or i == 4:  # Porcentajes ya están en 0-100
            normalized_values.append(value)
        elif i == 2 or i == 3:  # Potencias - escalar a porcentaje del máximo
            max_power = max(advanced_metrics['power_peak'], advanced_metrics['power_util_peak'])
            normalized_values.append((value / max_power) * 100)
        else:  # Área - escalar según un valor de referencia
            normalized_values.append(min(100, (value / 10) * 100))  # Asumiendo 10 m² como referencia

    # Colores según el rendimiento
    colors = []
    for i, norm_val in enumerate(normalized_values):
        if i < 5:  # Para métricas de eficiencia y tiempo
            if norm_val > 80:
                colors.append('#10b981')  # Verde
            elif norm_val > 60:
                colors.append('#f59e0b')  # Amarillo
            else:
                colors.append('#ef4444')  # Rojo
        else:
            colors.append('#3b82f6')  # Azul para área

    fig_bar = go.Figure(data=[
        go.Bar(
            x=metrics_names,
            y=normalized_values,
            text=[f"{val:.1f}" for val in metrics_values],
            textposition='auto',
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>Valor: %{text}<br>Normalizado: %{y:.1f}%<extra></extra>'
        )
    ])

    fig_bar.update_layout(
        title='Métricas Clave de Rendimiento',
        xaxis_title='Métricas',
        yaxis_title='Valor Normalizado (%)',
        yaxis=dict(range=[0, 100]),
        height=400,
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # === ANÁLISIS TEMPORAL DE EFICIENCIA ===
    st.markdown('<div class="section-header icon-time">Análisis Temporal de Eficiencia</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tiempo en Alta Eficiencia",
            f"{advanced_metrics['high_efficiency_time_percent']:.1f}%",
            help="Porcentaje del tiempo con eficiencia > 80%"
        )

    with col2:
        st.metric(
            "Tiempo en Eficiencia Media",
            f"{advanced_metrics['medium_efficiency_time_percent']:.1f}%",
            help="Porcentaje del tiempo con eficiencia 60-80%"
        )

    with col3:
        st.metric(
            "Tiempo en Baja Eficiencia",
            f"{advanced_metrics['low_efficiency_time_percent']:.1f}%",
            help="Porcentaje del tiempo con eficiencia < 60%"
        )

    # === RECOMENDACIONES ===
    st.markdown('<div class="section-header icon-recommendations">Recomendaciones de Optimización</div>', unsafe_allow_html=True)

    recommendations = generate_efficiency_recommendations(advanced_metrics)

    for rec_type, rec_text in recommendations.items():
        if rec_type == "success":
            st.success(rec_text)
        elif rec_type == "warning":
            st.warning(rec_text)
        elif rec_type == "error":
            st.error(rec_text)
        else:
            st.info(rec_text)


def generate_efficiency_recommendations(advanced_metrics):
    """Genera recomendaciones basadas en las métricas de eficiencia"""

    recommendations = {}

    efficiency_avg = advanced_metrics['efficiency_average']
    high_eff_time = advanced_metrics['high_efficiency_time_percent']
    efficiency_peak = advanced_metrics['efficiency_peak']
    efficiency_min = advanced_metrics['efficiency_min']

    # Recomendaciones basadas en eficiencia promedio
    if efficiency_avg > 85:
        recommendations["success"] = "**Excelente rendimiento**: El sistema opera con alta eficiencia. Mantén los parámetros actuales."
    elif efficiency_avg > 70:
        recommendations["warning"] = "**Buen rendimiento con margen de mejora**: Considera ajustar la velocidad de avance o la configuración de cuchillas."
    else:
        recommendations["error"] = "**Rendimiento bajo**: Revisa la configuración del sistema. Posibles causas: velocidad inadecuada, exceso de fricción, o configuración de cuchillas subóptima."

    # Recomendaciones basadas en variabilidad
    efficiency_range = efficiency_peak - efficiency_min
    if efficiency_range > 40:
        recommendations["info"] = "**Alta variabilidad detectada**: La eficiencia varía significativamente. Considera usar torque variable o ajustar la velocidad según las condiciones del terreno."

    # Recomendaciones basadas en tiempo en alta eficiencia
    if high_eff_time < 30:
        recommendations["warning"] = "**Poco tiempo en alta eficiencia**: Solo el {:.1f}% del tiempo opera con alta eficiencia. Optimiza los parámetros operacionales.".format(high_eff_time)

    # Recomendaciones específicas
    if efficiency_avg < 60:
        recommendations["info"] = """
        **Sugerencias específicas para mejorar eficiencia**:
        - Reducir fricción viscosa (parámetro 'b')
        - Optimizar número de cuchillas
        - Ajustar velocidad de avance según densidad vegetal
        - Verificar configuración del torque de entrada
        """

    return recommendations


if __name__ == "__main__":
    main()
