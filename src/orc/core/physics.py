"""
Core physics equations and mathematical models for rotary cutter systems.

This module implements the fundamental physics equations that govern the behavior
of rotary cutter systems, including:
- Rotational dynamics
- Moment of inertia calculations
- Torque component analysis
- Differential equation system definition

The physics model is based on Newton's second law for rotational motion:
I * α = Σ τ

Where:
- I: Total moment of inertia [kg⋅m²]
- α: Angular acceleration [rad/s²]
- Σ τ: Sum of all torques acting on the system [N⋅m]
"""

import numpy as np
from typing import Dict, Tuple, Callable, Optional
from dataclasses import dataclass


@dataclass
class PhysicsConstants:
    """Physical constants used in the rotary cutter model."""
    
    # Default material properties
    STEEL_DENSITY: float = 7850.0  # kg/m³
    AIR_DENSITY: float = 1.225     # kg/m³ at sea level
    
    # Typical ranges for validation
    MAX_ANGULAR_VELOCITY: float = 1000.0    # rad/s
    MAX_TORQUE: float = 10000.0             # N⋅m
    MAX_RADIUS: float = 5.0                 # m
    MAX_MASS: float = 1000.0                # kg


class RotaryCutterPhysics:
    """
    Core physics engine for rotary cutter systems.
    
    This class implements the fundamental physics equations and provides
    methods for calculating various physical quantities.
    """
    
    def __init__(self, constants: Optional[PhysicsConstants] = None):
        """
        Initialize the physics engine.
        
        Args:
            constants: Physical constants to use. If None, defaults are used.
        """
        self.constants = constants or PhysicsConstants()
    
    def differential_equation_system(self, t: float, y: np.ndarray, 
                                   params: Dict) -> np.ndarray:
        """
        Define the system of differential equations for rotary cutter dynamics.
        
        This implements the core physics model:
        dθ/dt = ω
        dω/dt = (τ_input - τ_friction - τ_drag - τ_grass) / I_total
        
        Args:
            t: Current time [s]
            y: State vector [θ, ω] where θ is angle [rad] and ω is angular velocity [rad/s]
            params: Dictionary containing physical parameters
            
        Returns:
            Derivative vector [dθ/dt, dω/dt]
        """
        theta, omega = y
        
        # Calculate total moment of inertia
        I_total = self.calculate_total_moment_of_inertia(params)
        
        # Calculate torque components
        torque_components = self.calculate_torque_components(t, omega, params)
        
        # Net torque
        net_torque = (torque_components['input'] - 
                     torque_components['friction'] - 
                     torque_components['drag'] - 
                     torque_components['grass'])
        
        # Angular acceleration
        alpha = net_torque / I_total
        
        return np.array([omega, alpha])
    
    def calculate_total_moment_of_inertia(self, params: Dict) -> float:
        """
        Calculate the total moment of inertia of the rotary cutter system.
        
        I_total = I_plate + n_blades * m_c * (R + L)²
        
        Args:
            params: Dictionary containing physical parameters
            
        Returns:
            Total moment of inertia [kg⋅m²]
        """
        I_plate = params['I_plate']
        n_blades = params.get('n_blades', 2)
        m_c = params['m_c']
        R = params['R']
        L = params['L']
        
        I_blades = n_blades * m_c * (R + L)**2
        
        return I_plate + I_blades
    
    def calculate_torque_components(self, t: float, omega: float, 
                                  params: Dict) -> Dict[str, float]:
        """
        Calculate all torque components acting on the system.
        
        Args:
            t: Current time [s]
            omega: Current angular velocity [rad/s]
            params: Dictionary containing physical parameters
            
        Returns:
            Dictionary with torque components [N⋅m]
        """
        # Input torque (motor)
        tau_input = params['tau_input']
        
        # Viscous friction torque
        tau_friction = params['b'] * omega
        
        # Aerodynamic drag torque
        tau_drag = params['c_drag'] * omega**2 * np.sign(omega)
        
        # Vegetation resistance torque
        if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
            # Variable torque function
            tau_grass = params['tau_grass_func'](t)
        else:
            # Constant torque model
            tau_grass = (params['k_grass'] * params['rho_veg'] * 
                        params['v_avance'] * params['R'])
        
        return {
            'input': tau_input,
            'friction': tau_friction,
            'drag': tau_drag,
            'grass': tau_grass,
            'net': tau_input - tau_friction - tau_drag - tau_grass
        }


def calculate_moment_of_inertia(mass_plate: float, radius: float, 
                              mass_blade: float, blade_radius: float, 
                              n_blades: int = 2) -> Tuple[float, float, float]:
    """
    Calculate moment of inertia components for a rotary cutter system.
    
    Args:
        mass_plate: Mass of the central plate [kg]
        radius: Radius of the plate [m]
        mass_blade: Mass of each blade [kg]
        blade_radius: Effective radius of blade center of mass [m]
        n_blades: Number of blades
        
    Returns:
        Tuple of (I_plate, I_blades, I_total) [kg⋅m²]
    """
    # Plate modeled as solid disk
    I_plate = 0.5 * mass_plate * radius**2
    
    # Blades modeled as point masses
    I_blades = n_blades * mass_blade * blade_radius**2
    
    # Total moment of inertia
    I_total = I_plate + I_blades
    
    return I_plate, I_blades, I_total


def calculate_kinetic_energy(moment_of_inertia: float, 
                           angular_velocity: float) -> float:
    """
    Calculate rotational kinetic energy.
    
    KE = 0.5 * I * ω²
    
    Args:
        moment_of_inertia: Moment of inertia [kg⋅m²]
        angular_velocity: Angular velocity [rad/s]
        
    Returns:
        Kinetic energy [J]
    """
    return 0.5 * moment_of_inertia * angular_velocity**2


def calculate_power(torque: float, angular_velocity: float) -> float:
    """
    Calculate mechanical power.
    
    P = τ * ω
    
    Args:
        torque: Applied torque [N⋅m]
        angular_velocity: Angular velocity [rad/s]
        
    Returns:
        Power [W]
    """
    return torque * angular_velocity
