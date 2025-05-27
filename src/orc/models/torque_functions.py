"""
Torque function definitions for rotary cutter systems.

This module provides predefined torque functions for modeling vegetation
resistance in both temporal and spatial domains. These functions can be
used to simulate various cutting scenarios and terrain conditions.

Temporal functions model how torque varies over time.
Spatial functions model how torque varies with position/distance.
"""

import numpy as np
from typing import Callable, Dict, Any, Optional
from enum import Enum
import logging


class TorqueFunctionType(Enum):
    """Available torque function types."""
    
    # Temporal functions
    CONSTANT = "constant"
    SINUSOIDAL = "sinusoidal"
    STEP = "step"
    RAMP = "ramp"
    EXPONENTIAL = "exponential"
    
    # Spatial functions
    SPATIAL_ZONES = "spatial_zones"
    SPATIAL_GAUSSIAN = "spatial_gaussian"
    SPATIAL_SIGMOID = "spatial_sigmoid"
    SPATIAL_SINUSOIDAL = "spatial_sinusoidal"
    SPATIAL_COMPLEX = "spatial_complex"


class TemporalTorqueFunctions:
    """
    Collection of temporal torque functions.
    
    These functions model how vegetation resistance torque varies over time
    during the cutting operation.
    """
    
    @staticmethod
    def constant(base_torque: float = 50.0) -> Callable[[float], float]:
        """
        Constant torque function.
        
        Args:
            base_torque: Constant torque value [N⋅m]
            
        Returns:
            Torque function τ(t) = base_torque
        """
        def torque_func(t: float) -> float:
            return base_torque
        
        return torque_func
    
    @staticmethod
    def sinusoidal(base_torque: float = 50.0, amplitude: float = 20.0,
                  frequency: float = 0.5, phase: float = 0.0) -> Callable[[float], float]:
        """
        Sinusoidal torque variation.
        
        Args:
            base_torque: Base torque level [N⋅m]
            amplitude: Oscillation amplitude [N⋅m]
            frequency: Oscillation frequency [Hz]
            phase: Phase shift [rad]
            
        Returns:
            Torque function τ(t) = base_torque + amplitude * sin(2π*frequency*t + phase)
        """
        def torque_func(t: float) -> float:
            return base_torque + amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
        return torque_func
    
    @staticmethod
    def step(low_torque: float = 30.0, high_torque: float = 80.0,
            step_time: float = 5.0) -> Callable[[float], float]:
        """
        Step torque function.
        
        Args:
            low_torque: Initial torque level [N⋅m]
            high_torque: Final torque level [N⋅m]
            step_time: Time of step change [s]
            
        Returns:
            Torque function with step change at step_time
        """
        def torque_func(t: float) -> float:
            return high_torque if t >= step_time else low_torque
        
        return torque_func
    
    @staticmethod
    def ramp(initial_torque: float = 30.0, final_torque: float = 80.0,
            ramp_duration: float = 10.0, start_time: float = 0.0) -> Callable[[float], float]:
        """
        Linear ramp torque function.
        
        Args:
            initial_torque: Starting torque [N⋅m]
            final_torque: Ending torque [N⋅m]
            ramp_duration: Duration of ramp [s]
            start_time: Start time of ramp [s]
            
        Returns:
            Torque function with linear ramp
        """
        def torque_func(t: float) -> float:
            if t < start_time:
                return initial_torque
            elif t > start_time + ramp_duration:
                return final_torque
            else:
                progress = (t - start_time) / ramp_duration
                return initial_torque + (final_torque - initial_torque) * progress
        
        return torque_func
    
    @staticmethod
    def exponential(base_torque: float = 50.0, amplitude: float = 30.0,
                   time_constant: float = 3.0, decay: bool = True) -> Callable[[float], float]:
        """
        Exponential torque function.
        
        Args:
            base_torque: Asymptotic torque level [N⋅m]
            amplitude: Initial amplitude [N⋅m]
            time_constant: Time constant [s]
            decay: If True, exponential decay; if False, exponential growth
            
        Returns:
            Torque function with exponential behavior
        """
        def torque_func(t: float) -> float:
            if decay:
                return base_torque + amplitude * np.exp(-t / time_constant)
            else:
                return base_torque + amplitude * (1 - np.exp(-t / time_constant))
        
        return torque_func


class SpatialTorqueFunctions:
    """
    Collection of spatial torque functions.
    
    These functions model how vegetation resistance varies with position
    along the cutting path.
    """
    
    @staticmethod
    def zones(zone_torques: list = None, zone_lengths: list = None,
             advance_velocity: float = 3.0) -> Callable[[float], float]:
        """
        Alternating zones with different torque levels.
        
        Args:
            zone_torques: List of torque values for each zone [N⋅m]
            zone_lengths: List of zone lengths [m]
            advance_velocity: Forward velocity [m/s]
            
        Returns:
            Spatial torque function
        """
        if zone_torques is None:
            zone_torques = [30.0, 70.0, 50.0]
        if zone_lengths is None:
            zone_lengths = [5.0, 3.0, 4.0]
        
        def torque_func(t: float) -> float:
            position = advance_velocity * t
            cumulative_length = 0.0
            
            for torque, length in zip(zone_torques, zone_lengths):
                if position <= cumulative_length + length:
                    return torque
                cumulative_length += length
            
            # Repeat pattern if beyond defined zones
            total_length = sum(zone_lengths)
            if total_length > 0:
                position_mod = position % total_length
                cumulative_length = 0.0
                for torque, length in zip(zone_torques, zone_lengths):
                    if position_mod <= cumulative_length + length:
                        return torque
                    cumulative_length += length
            
            return zone_torques[-1]  # Fallback
        
        return torque_func
    
    @staticmethod
    def gaussian_patches(patch_centers: list = None, patch_amplitudes: list = None,
                        patch_widths: list = None, base_torque: float = 40.0,
                        advance_velocity: float = 3.0) -> Callable[[float], float]:
        """
        Gaussian patches of vegetation.
        
        Args:
            patch_centers: Centers of patches [m]
            patch_amplitudes: Amplitude of each patch [N⋅m]
            patch_widths: Width (standard deviation) of each patch [m]
            base_torque: Base torque level [N⋅m]
            advance_velocity: Forward velocity [m/s]
            
        Returns:
            Spatial torque function with Gaussian patches
        """
        if patch_centers is None:
            patch_centers = [8.0, 20.0, 35.0]
        if patch_amplitudes is None:
            patch_amplitudes = [30.0, 40.0, 25.0]
        if patch_widths is None:
            patch_widths = [2.0, 3.0, 1.5]
        
        def torque_func(t: float) -> float:
            position = advance_velocity * t
            total_torque = base_torque
            
            for center, amplitude, width in zip(patch_centers, patch_amplitudes, patch_widths):
                gaussian = amplitude * np.exp(-0.5 * ((position - center) / width)**2)
                total_torque += gaussian
            
            return total_torque
        
        return torque_func
    
    @staticmethod
    def sigmoid_transition(low_torque: float = 30.0, high_torque: float = 80.0,
                          transition_center: float = 15.0, transition_width: float = 3.0,
                          advance_velocity: float = 3.0) -> Callable[[float], float]:
        """
        Smooth sigmoid transition between torque levels.
        
        Args:
            low_torque: Low torque level [N⋅m]
            high_torque: High torque level [N⋅m]
            transition_center: Center of transition [m]
            transition_width: Width of transition [m]
            advance_velocity: Forward velocity [m/s]
            
        Returns:
            Spatial torque function with sigmoid transition
        """
        def torque_func(t: float) -> float:
            position = advance_velocity * t
            sigmoid = 1.0 / (1.0 + np.exp(-(position - transition_center) / transition_width))
            return low_torque + (high_torque - low_torque) * sigmoid
        
        return torque_func
    
    @staticmethod
    def sinusoidal_spatial(base_torque: float = 50.0, amplitude: float = 20.0,
                          wavelength: float = 10.0, phase: float = 0.0,
                          advance_velocity: float = 3.0) -> Callable[[float], float]:
        """
        Sinusoidal spatial variation.
        
        Args:
            base_torque: Base torque level [N⋅m]
            amplitude: Oscillation amplitude [N⋅m]
            wavelength: Spatial wavelength [m]
            phase: Phase shift [rad]
            advance_velocity: Forward velocity [m/s]
            
        Returns:
            Spatial torque function with sinusoidal variation
        """
        def torque_func(t: float) -> float:
            position = advance_velocity * t
            return base_torque + amplitude * np.sin(2 * np.pi * position / wavelength + phase)
        
        return torque_func
    
    @staticmethod
    def complex_terrain(advance_velocity: float = 3.0) -> Callable[[float], float]:
        """
        Complex terrain with multiple features.
        
        Args:
            advance_velocity: Forward velocity [m/s]
            
        Returns:
            Complex spatial torque function
        """
        def torque_func(t: float) -> float:
            position = advance_velocity * t
            
            # Base level with gentle variation
            base = 45.0 + 10.0 * np.sin(2 * np.pi * position / 20.0)
            
            # Dense patches
            patch1 = 25.0 * np.exp(-0.5 * ((position - 12.0) / 2.0)**2)
            patch2 = 30.0 * np.exp(-0.5 * ((position - 28.0) / 1.5)**2)
            
            # Transition zones
            if 18.0 <= position <= 22.0:
                transition = 15.0 * (1.0 / (1.0 + np.exp(-(position - 20.0) / 1.0)))
            else:
                transition = 0.0
            
            # Random variation (simplified)
            random_component = 5.0 * np.sin(2 * np.pi * position / 3.0 + 1.5)
            
            return base + patch1 + patch2 + transition + random_component
        
        return torque_func


def create_torque_function(function_type: TorqueFunctionType,
                          parameters: Optional[Dict[str, Any]] = None) -> Callable[[float], float]:
    """
    Factory function to create torque functions.
    
    Args:
        function_type: Type of torque function to create
        parameters: Parameters for the function
        
    Returns:
        Torque function
    """
    if parameters is None:
        parameters = {}
    
    logger = logging.getLogger(__name__)
    
    try:
        if function_type == TorqueFunctionType.CONSTANT:
            return TemporalTorqueFunctions.constant(**parameters)
        elif function_type == TorqueFunctionType.SINUSOIDAL:
            return TemporalTorqueFunctions.sinusoidal(**parameters)
        elif function_type == TorqueFunctionType.STEP:
            return TemporalTorqueFunctions.step(**parameters)
        elif function_type == TorqueFunctionType.RAMP:
            return TemporalTorqueFunctions.ramp(**parameters)
        elif function_type == TorqueFunctionType.EXPONENTIAL:
            return TemporalTorqueFunctions.exponential(**parameters)
        elif function_type == TorqueFunctionType.SPATIAL_ZONES:
            return SpatialTorqueFunctions.zones(**parameters)
        elif function_type == TorqueFunctionType.SPATIAL_GAUSSIAN:
            return SpatialTorqueFunctions.gaussian_patches(**parameters)
        elif function_type == TorqueFunctionType.SPATIAL_SIGMOID:
            return SpatialTorqueFunctions.sigmoid_transition(**parameters)
        elif function_type == TorqueFunctionType.SPATIAL_SINUSOIDAL:
            return SpatialTorqueFunctions.sinusoidal_spatial(**parameters)
        elif function_type == TorqueFunctionType.SPATIAL_COMPLEX:
            return SpatialTorqueFunctions.complex_terrain(**parameters)
        else:
            logger.warning(f"Unknown torque function type: {function_type}")
            return TemporalTorqueFunctions.constant()
    
    except Exception as e:
        logger.error(f"Error creating torque function: {e}")
        return TemporalTorqueFunctions.constant()
