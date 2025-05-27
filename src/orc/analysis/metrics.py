"""
Performance metrics calculation and analysis for rotary cutter systems.

This module provides comprehensive performance analysis including:
- Energy efficiency calculations
- Stability metrics
- Power analysis
- Cutting performance metrics
- Statistical analysis of simulation results
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from ..core.simulation import SimulationResult


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    
    # Energy metrics
    efficiency: float                    # Overall energy efficiency [0-1]
    cutting_efficiency: float           # Cutting energy efficiency [0-1]
    energy_total: float                  # Total energy consumed [J]
    energy_useful: float                 # Useful energy for cutting [J]
    energy_losses: float                 # Energy losses [J]
    
    # Power metrics
    power_avg: float                     # Average power [W]
    power_max: float                     # Maximum power [W]
    power_min: float                     # Minimum power [W]
    power_rms: float                     # RMS power [W]
    
    # Stability metrics
    omega_stability: float               # Angular velocity stability [0-1]
    torque_stability: float              # Torque stability [0-1]
    power_stability: float               # Power stability [0-1]
    
    # Cutting performance
    area_cut: float                      # Total area cut [m²]
    cutting_rate: float                  # Cutting rate [m²/s]
    area_efficiency: float               # Area per unit energy [m²/J]
    
    # Dynamic characteristics
    settling_time: float                 # Time to reach steady state [s]
    overshoot: float                     # Maximum overshoot [%]
    steady_state_error: float            # Steady state error [%]
    
    # Frequency analysis
    dominant_frequency: float            # Dominant frequency [Hz]
    frequency_content: Dict              # Frequency spectrum analysis
    
    # Statistical metrics
    statistics: Dict                     # Additional statistical measures


class PerformanceAnalyzer:
    """
    Comprehensive performance analyzer for rotary cutter simulations.
    
    This class provides methods to analyze simulation results and calculate
    various performance metrics including efficiency, stability, and cutting performance.
    """
    
    def __init__(self):
        """Initialize the performance analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, result: SimulationResult) -> PerformanceMetrics:
        """
        Perform comprehensive performance analysis of simulation results.
        
        Args:
            result: SimulationResult object containing simulation data
            
        Returns:
            PerformanceMetrics object with all calculated metrics
        """
        if not result.success:
            self.logger.warning("Analyzing failed simulation result")
        
        # Extract time series data
        time = result.time
        omega = result.angular_velocity
        torque = result.torque
        power = result.power
        kinetic_energy = result.kinetic_energy
        
        # Calculate energy metrics
        energy_metrics = self._calculate_energy_metrics(time, power, result.parameters)
        
        # Calculate power metrics
        power_metrics = self._calculate_power_metrics(power)
        
        # Calculate stability metrics
        stability_metrics = self._calculate_stability_metrics(omega, torque, power)
        
        # Calculate cutting performance
        cutting_metrics = self._calculate_cutting_metrics(time, result.parameters)
        
        # Calculate dynamic characteristics
        dynamic_metrics = self._calculate_dynamic_metrics(time, omega, torque)
        
        # Frequency analysis
        frequency_metrics = self._calculate_frequency_metrics(time, torque)
        
        # Statistical analysis
        statistical_metrics = self._calculate_statistical_metrics(
            time, omega, torque, power, kinetic_energy
        )
        
        return PerformanceMetrics(
            # Energy metrics
            efficiency=energy_metrics['efficiency'],
            cutting_efficiency=energy_metrics['cutting_efficiency'],
            energy_total=energy_metrics['energy_total'],
            energy_useful=energy_metrics['energy_useful'],
            energy_losses=energy_metrics['energy_losses'],
            
            # Power metrics
            power_avg=power_metrics['avg'],
            power_max=power_metrics['max'],
            power_min=power_metrics['min'],
            power_rms=power_metrics['rms'],
            
            # Stability metrics
            omega_stability=stability_metrics['omega'],
            torque_stability=stability_metrics['torque'],
            power_stability=stability_metrics['power'],
            
            # Cutting performance
            area_cut=cutting_metrics['area_cut'],
            cutting_rate=cutting_metrics['cutting_rate'],
            area_efficiency=cutting_metrics['area_efficiency'],
            
            # Dynamic characteristics
            settling_time=dynamic_metrics['settling_time'],
            overshoot=dynamic_metrics['overshoot'],
            steady_state_error=dynamic_metrics['steady_state_error'],
            
            # Frequency analysis
            dominant_frequency=frequency_metrics['dominant_frequency'],
            frequency_content=frequency_metrics['spectrum'],
            
            # Statistical metrics
            statistics=statistical_metrics
        )
    
    def _calculate_energy_metrics(self, time: np.ndarray, power: np.ndarray, 
                                 parameters: Dict) -> Dict:
        """Calculate energy-related metrics."""
        # Total energy consumed
        energy_total = np.trapz(np.abs(power), time)
        
        # Useful energy (for cutting)
        # This requires knowledge of the cutting torque component
        tau_input = parameters.get('tau_input', 0)
        k_grass = parameters.get('k_grass', 0)
        rho_veg = parameters.get('rho_veg', 0)
        v_avance = parameters.get('v_avance', 0)
        R = parameters.get('R', 0)
        
        # Estimate useful power (simplified)
        if 'tau_grass_func' in parameters and parameters['tau_grass_func'] is not None:
            # Variable torque function
            tau_grass_values = np.array([parameters['tau_grass_func'](t) for t in time])
            useful_power = tau_grass_values * np.abs(power) / (tau_input + 1e-10)
        else:
            # Constant torque
            tau_grass = k_grass * rho_veg * v_avance * R
            useful_power = (tau_grass / (tau_input + 1e-10)) * np.abs(power)
        
        energy_useful = np.trapz(useful_power, time)
        energy_losses = energy_total - energy_useful
        
        # Efficiencies
        efficiency = energy_useful / (energy_total + 1e-10)
        cutting_efficiency = efficiency  # Simplified for now
        
        return {
            'efficiency': efficiency,
            'cutting_efficiency': cutting_efficiency,
            'energy_total': energy_total,
            'energy_useful': energy_useful,
            'energy_losses': energy_losses
        }
    
    def _calculate_power_metrics(self, power: np.ndarray) -> Dict:
        """Calculate power-related metrics."""
        return {
            'avg': np.mean(power),
            'max': np.max(power),
            'min': np.min(power),
            'rms': np.sqrt(np.mean(power**2))
        }
    
    def _calculate_stability_metrics(self, omega: np.ndarray, torque: np.ndarray,
                                   power: np.ndarray) -> Dict:
        """Calculate stability metrics."""
        # Stability is defined as 1 - (coefficient of variation)
        omega_stability = 1 - (np.std(omega) / (np.mean(np.abs(omega)) + 1e-10))
        torque_stability = 1 - (np.std(torque) / (np.mean(np.abs(torque)) + 1e-10))
        power_stability = 1 - (np.std(power) / (np.mean(np.abs(power)) + 1e-10))
        
        # Ensure stability metrics are between 0 and 1
        omega_stability = max(0, min(1, omega_stability))
        torque_stability = max(0, min(1, torque_stability))
        power_stability = max(0, min(1, power_stability))
        
        return {
            'omega': omega_stability,
            'torque': torque_stability,
            'power': power_stability
        }
    
    def _calculate_cutting_metrics(self, time: np.ndarray, parameters: Dict) -> Dict:
        """Calculate cutting performance metrics."""
        v_avance = parameters.get('v_avance', 0)
        w = parameters.get('w', 1.8)  # Cutting width
        
        # Total area cut
        area_cut = v_avance * w * time[-1]
        
        # Cutting rate
        cutting_rate = v_avance * w
        
        # Area efficiency (will be calculated with energy data)
        area_efficiency = 0.0  # Placeholder
        
        return {
            'area_cut': area_cut,
            'cutting_rate': cutting_rate,
            'area_efficiency': area_efficiency
        }
    
    def _calculate_dynamic_metrics(self, time: np.ndarray, omega: np.ndarray,
                                  torque: np.ndarray) -> Dict:
        """Calculate dynamic response characteristics."""
        # Settling time (time to reach 95% of final value)
        final_omega = omega[-1]
        settling_threshold = 0.05 * abs(final_omega)
        
        settling_time = time[-1]  # Default to full simulation time
        for i in range(len(omega) - 1, 0, -1):
            if abs(omega[i] - final_omega) > settling_threshold:
                settling_time = time[i]
                break
        
        # Overshoot (maximum deviation from final value)
        if final_omega != 0:
            overshoot = (np.max(omega) - final_omega) / abs(final_omega) * 100
        else:
            overshoot = 0.0
        
        # Steady state error (simplified)
        steady_state_error = 0.0  # Would need reference value
        
        return {
            'settling_time': settling_time,
            'overshoot': overshoot,
            'steady_state_error': steady_state_error
        }
    
    def _calculate_frequency_metrics(self, time: np.ndarray, torque: np.ndarray) -> Dict:
        """Calculate frequency domain characteristics."""
        if len(time) < 10:
            return {
                'dominant_frequency': 0.0,
                'spectrum': {}
            }
        
        # Calculate sampling frequency
        dt = np.mean(np.diff(time))
        fs = 1.0 / dt
        
        # FFT analysis
        fft_torque = np.fft.fft(torque)
        freqs = np.fft.fftfreq(len(time), dt)
        
        # Find dominant frequency (excluding DC component)
        positive_freqs = freqs[1:len(freqs)//2]
        positive_fft = np.abs(fft_torque[1:len(freqs)//2])
        
        if len(positive_fft) > 0:
            dominant_freq_idx = np.argmax(positive_fft)
            dominant_frequency = positive_freqs[dominant_freq_idx]
        else:
            dominant_frequency = 0.0
        
        # Frequency spectrum (simplified)
        spectrum = {
            'frequencies': positive_freqs.tolist() if len(positive_freqs) > 0 else [],
            'magnitudes': positive_fft.tolist() if len(positive_fft) > 0 else [],
            'sampling_frequency': fs
        }
        
        return {
            'dominant_frequency': dominant_frequency,
            'spectrum': spectrum
        }
    
    def _calculate_statistical_metrics(self, time: np.ndarray, omega: np.ndarray,
                                     torque: np.ndarray, power: np.ndarray,
                                     kinetic_energy: np.ndarray) -> Dict:
        """Calculate additional statistical metrics."""
        return {
            'simulation_duration': time[-1] - time[0],
            'n_points': len(time),
            'omega_range': float(np.ptp(omega)),
            'omega_mean': float(np.mean(omega)),
            'omega_std': float(np.std(omega)),
            'torque_range': float(np.ptp(torque)),
            'torque_mean': float(np.mean(torque)),
            'torque_std': float(np.std(torque)),
            'power_range': float(np.ptp(power)),
            'power_mean': float(np.mean(power)),
            'power_std': float(np.std(power)),
            'energy_final': float(kinetic_energy[-1]),
            'energy_peak': float(np.max(kinetic_energy))
        }


def calculate_efficiency(energy_useful: float, energy_total: float) -> float:
    """
    Calculate energy efficiency.
    
    Args:
        energy_useful: Useful energy for cutting [J]
        energy_total: Total energy consumed [J]
        
    Returns:
        Efficiency ratio [0-1]
    """
    return energy_useful / (energy_total + 1e-10)


def calculate_stability_metrics(signal: np.ndarray) -> Dict:
    """
    Calculate stability metrics for a signal.
    
    Args:
        signal: Time series signal
        
    Returns:
        Dictionary with stability metrics
    """
    mean_val = np.mean(np.abs(signal))
    std_val = np.std(signal)
    
    # Coefficient of variation
    cv = std_val / (mean_val + 1e-10)
    
    # Stability index (1 - CV, bounded between 0 and 1)
    stability = max(0, min(1, 1 - cv))
    
    return {
        'stability_index': stability,
        'coefficient_of_variation': cv,
        'mean': mean_val,
        'std': std_val,
        'range': np.ptp(signal),
        'rms': np.sqrt(np.mean(signal**2))
    }
