"""
Modelo físico avanzado para simulación de rotary cutter
Optimización numérica - ORC Project

Este módulo contiene el modelo físico completo basado en ecuaciones diferenciales
para simular el comportamiento dinámico real de un rotary cutter, incluyendo:
- Sistema de EDOs para dinámica rotacional
- Resistencia de vegetación
- Fricción viscosa y arrastre aerodinámico
- Múltiples configuraciones de cuchillas
- Análisis de rendimiento avanzado
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from typing import Dict, Tuple, Optional


# ===============================================================================
# SISTEMA FÍSICO AVANZADO - ECUACIONES DIFERENCIALES
# ===============================================================================

def rotary_cutter_system(t: float, y: np.ndarray, params: Dict) -> np.ndarray:
    """
    Define el sistema de ecuaciones diferenciales para el modelo físico del rotary cutter.

    Variables de estado:
    y[0] = theta (posición angular del plato) [rad]
    y[1] = omega (velocidad angular del plato) [rad/s]

    Args:
        t (float): Tiempo actual
        y (np.ndarray): Vector de estado [theta, omega]
        params (Dict): Parámetros físicos del sistema

    Parámetros esperados en 'params':
        - I_plate: momento de inercia del plato [kg*m^2]
        - m_c: masa de una cuchilla [kg]
        - R: radio desde el eje al perno [m]
        - L: longitud desde el perno al centro de masa de la cuchilla [m]
        - tau_input: torque aplicado por el motor [Nm]
        - b: coeficiente de fricción viscosa [N*m*s/rad]
        - c_drag: coeficiente de arrastre aerodinámico [N*m*s^2/rad^2]
        - rho_veg: densidad de vegetación [kg/m^2]
        - k_grass: constante de resistencia vegetal [N*s/m]
        - v_avance: velocidad de avance del tractor [m/s]
        - n_blades: número de cuchillas

    Returns:
        np.ndarray: Derivadas [dtheta/dt, domega/dt]
    """
    theta, omega = y  # Desempaquetamos variables de estado

    # Parámetros físicos
    I_plate = params['I_plate']
    m_c = params['m_c']
    R = params['R']
    L = params['L']
    tau_input = params['tau_input']
    b = params['b']
    c_drag = params['c_drag']
    rho_veg = params['rho_veg']
    k_grass = params['k_grass']
    v_avance = params['v_avance']
    n_blades = params.get('n_blades', 2)  # Número de cuchillas (default: 2)

    # Momento de inercia total (plato + cuchillas completamente extendidas)
    I_total = I_plate + n_blades * m_c * (R + L)**2

    # Torque resistivo por el pasto
    if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
        # Usar función de torque variable
        tau_grass = params['tau_grass_func'](t)
    else:
        # Usar modelo constante
        tau_grass = k_grass * rho_veg * v_avance * R

    # Fricción viscosa
    friction = b * omega

    # Arrastre cuadrático (aerodinámica)
    drag = c_drag * omega**2 * np.sign(omega)

    # Ecuación de movimiento rotacional: I * alpha = sum(torques)
    domega_dt = (tau_input - friction - drag - tau_grass) / I_total

    return np.array([omega, domega_dt])


def simulate_advanced_configuration(params: Dict, t_max: float = 10.0,
                                  t_eval: Optional[np.ndarray] = None,
                                  y0: Optional[list] = None) -> Dict:
    """
    Simula la configuración física usando el sistema de EDOs con RK45.

    Args:
        params (Dict): Diccionario con parámetros del sistema
        t_max (float): Tiempo máximo de simulación [s]
        t_eval (Optional[np.ndarray]): Array de tiempos para evaluación
        y0 (Optional[list]): Condiciones iniciales [theta(0), omega(0)] en [rad, rad/s]

    Returns:
        Dict: Resultados de la simulación con series temporales y estadísticas
    """
    # Validar parámetros físicos antes de la simulación
    validate_params(params)

    # Condiciones iniciales: [theta(0), omega(0)]
    if y0 is None:
        y0 = [0.0, 0.0]  # Por defecto: reposo
    else:
        # Validar condiciones iniciales
        if not isinstance(y0, (list, tuple, np.ndarray)) or len(y0) != 2:
            raise ValueError("y0 debe ser una lista/array de 2 elementos [theta(0), omega(0)]")

        theta0, omega0 = y0
        if not isinstance(theta0, (int, float)) or not isinstance(omega0, (int, float)):
            raise ValueError("Las condiciones iniciales deben ser números")

        # Verificar rangos razonables
        if abs(theta0) > 100.0:  # ~16 revoluciones
            raise ValueError(f"Ángulo inicial excesivo: {theta0} rad (máximo práctico: ±100 rad)")

        if abs(omega0) > 1000.0:  # ~9550 RPM
            raise ValueError(f"Velocidad angular inicial excesiva: {omega0} rad/s (máximo práctico: ±1000 rad/s)")

        y0 = [float(theta0), float(omega0)]

    # Vector de tiempos si no se especifica
    if t_eval is None:
        t_eval = np.linspace(0, t_max, 1000)

    # Integración con solve_ivp (RK45)
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

    if not sol.success:
        raise RuntimeError(f"La integración falló: {sol.message}")

    # Extraer resultados
    time = sol.t
    theta = sol.y[0]
    omega = sol.y[1]

    # Calcular variables derivadas
    I_total = params['I_plate'] + params.get('n_blades', 2) * params['m_c'] * (params['R'] + params['L'])**2

    # Torque instantáneo
    torque = np.zeros_like(time)
    for i, (t_i, omega_i) in enumerate(zip(time, omega)):
        # Calcular torque del pasto (constante o variable)
        if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
            tau_grass = params['tau_grass_func'](t_i)
        else:
            tau_grass = params['k_grass'] * params['rho_veg'] * params['v_avance'] * params['R']

        friction = params['b'] * omega_i
        drag = params['c_drag'] * omega_i**2 * np.sign(omega_i)
        torque[i] = params['tau_input'] - friction - drag - tau_grass

    # Energía cinética
    kinetic_energy = 0.5 * I_total * omega**2

    # Potencia instantánea
    power = torque * omega

    # Trabajo total
    work_total = np.trapezoid(power, time)

    # Estadísticas básicas
    omega_max = np.max(np.abs(omega))
    omega_rms = np.sqrt(np.mean(omega**2))
    torque_max = np.max(np.abs(torque))
    torque_rms = np.sqrt(np.mean(torque**2))
    energy_avg = np.mean(kinetic_energy)

    # Calcular métricas avanzadas de eficiencia y corte
    advanced_metrics = compute_metrics(sol, params)

    return {
        'time': time,
        'theta': theta,
        'omega': omega,
        'torque': torque,
        'kinetic_energy': kinetic_energy,
        'power': power,
        'moment_of_inertia': I_total,
        'work_total': work_total,
        'statistics': {
            'omega_max': omega_max,
            'omega_rms': omega_rms,
            'torque_max': torque_max,
            'torque_rms': torque_rms,
            'energy_avg': energy_avg,
            'simulation_time': t_max,
            'integration_points': len(time),
            'success': sol.success
        },
        'advanced_metrics': advanced_metrics
    }


# ===============================================================================
# FUNCIONES DE ANÁLISIS DE MÉTRICAS AVANZADAS
# ===============================================================================

def compute_metrics(sol, params):
    """
    Calcula energía total, energía útil (por corte), área cortada y eficiencia.
    Incluye métricas avanzadas para el dashboard de análisis de eficiencia.

    Entradas:
    - sol: objeto resultado de solve_ivp con .t (tiempo), .y (solución)
    - params: diccionario con parámetros del sistema

    Salidas:
    - dict con: E_total, E_util, A_total, eta, epsilon y métricas adicionales
    """

    t = sol.t                         # Vector de tiempo
    omega = sol.y[1]                  # Velocidad angular omega(t)
    dt = np.diff(t)                  # Diferenciales de tiempo

    # Para integración por método del trapecio
    omega_avg = (omega[:-1] + omega[1:]) / 2

    # Parámetros necesarios
    tau_input = params['tau_input']
    R = params['R']
    k_grass = params['k_grass']
    rho_veg = params['rho_veg']
    v_avance = params['v_avance']
    w = params.get('w', 1.8)  # Ancho de corte (default 1.8 m como en MX9/MX10)

    # Energía total: integral de tau_input * omega dt
    power_total = tau_input * omega_avg
    E_total = np.sum(power_total * dt)  # [J]

    # Energía útil: torque pasto * omega dt
    if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
        # Calcular torque variable para cada punto de tiempo
        tau_grass_values = np.array([params['tau_grass_func'](t_i) for t_i in t[:-1]])
        power_util = tau_grass_values * omega_avg
    else:
        # Usar torque constante
        tau_grass = k_grass * rho_veg * v_avance * R
        power_util = tau_grass * omega_avg

    E_util = np.sum(power_util * dt)

    # Área cortada: v_avance * w * t_total
    A_total = v_avance * w * t[-1]  # [m²]

    # Eficiencias
    eta = E_util / E_total if E_total > 0 else 0  # eficiencia energética
    epsilon = A_total / E_total if E_total > 0 else 0  # m²/J

    # === MÉTRICAS ADICIONALES PARA DASHBOARD DE EFICIENCIA ===

    # Potencia total instantánea para todo el tiempo
    power_total_full = tau_input * omega

    # Potencia útil instantánea para todo el tiempo
    if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
        tau_grass_full = np.array([params['tau_grass_func'](t_i) for t_i in t])
        power_util_full = tau_grass_full * omega
    else:
        tau_grass = k_grass * rho_veg * v_avance * R
        power_util_full = tau_grass * omega

    # Eficiencia instantánea (%)
    # Usar máscara más robusta para evitar divisiones por cero y valores inválidos
    valid_mask = (power_total_full > 1e-6) & (power_util_full >= 0) & np.isfinite(power_total_full) & np.isfinite(power_util_full)
    efficiency_instantaneous = np.zeros_like(power_total_full)
    efficiency_instantaneous[valid_mask] = (power_util_full[valid_mask] / power_total_full[valid_mask]) * 100

    # Limitar eficiencia a valores razonables (0-100%)
    efficiency_instantaneous = np.clip(efficiency_instantaneous, 0.0, 100.0)

    # Eficiencia promedio
    efficiency_average = np.mean(efficiency_instantaneous)

    # Energía perdida
    E_losses = E_total - E_util

    # Métricas de rendimiento adicionales
    power_peak = np.max(power_total_full)
    power_util_peak = np.max(power_util_full)
    efficiency_peak = np.max(efficiency_instantaneous)
    efficiency_min = np.min(efficiency_instantaneous)

    # Tiempo en diferentes rangos de eficiencia
    high_eff_time = np.sum(efficiency_instantaneous > 80) / len(efficiency_instantaneous) * 100
    medium_eff_time = np.sum((efficiency_instantaneous >= 60) & (efficiency_instantaneous <= 80)) / len(efficiency_instantaneous) * 100
    low_eff_time = np.sum(efficiency_instantaneous < 60) / len(efficiency_instantaneous) * 100

    return {
        # Métricas básicas existentes
        'E_total': E_total,
        'E_util': E_util,
        'A_total': A_total,
        'eta': eta,
        'epsilon': epsilon,
        'power_total_avg': np.mean(power_total),
        'power_util_avg': np.mean(power_util),
        'cutting_width': w,
        'cutting_speed': v_avance,
        'simulation_time': t[-1],

        # Nuevas métricas para dashboard de eficiencia
        'time_series': t,
        'power_total_series': power_total_full,
        'power_util_series': power_util_full,
        'efficiency_instantaneous': efficiency_instantaneous,
        'efficiency_average': efficiency_average,
        'E_losses': E_losses,
        'power_peak': power_peak,
        'power_util_peak': power_util_peak,
        'efficiency_peak': efficiency_peak,
        'efficiency_min': efficiency_min,
        'high_efficiency_time_percent': high_eff_time,
        'medium_efficiency_time_percent': medium_eff_time,
        'low_efficiency_time_percent': low_eff_time
    }


# ===============================================================================
# FUNCIONES DE CONFIGURACIÓN Y UTILIDADES
# ===============================================================================


# ===============================================================================
# FUNCIONES DE VALIDACIÓN DE PARÁMETROS
# ===============================================================================

def validate_params(params: Dict) -> None:
    """
    Valida que todos los parámetros físicos sean coherentes y positivos.

    Args:
        params (Dict): Diccionario con parámetros del sistema

    Raises:
        ValueError: Si algún parámetro es inválido
        KeyError: Si falta algún parámetro requerido
    """

    # Parámetros requeridos y sus restricciones
    required_positive = {
        'I_plate': 'Momento de inercia del plato',
        'm_c': 'Masa de cuchilla',
        'R': 'Radio al perno',
        'L': 'Longitud de cuchilla',
        'tau_input': 'Torque del motor',
        'b': 'Fricción viscosa',
        'c_drag': 'Arrastre aerodinámico',
        'rho_veg': 'Densidad de vegetación',
        'k_grass': 'Resistencia vegetal',
        'v_avance': 'Velocidad de avance'
    }

    # Verificar que existan todos los parámetros requeridos
    missing_params = []
    for param in required_positive.keys():
        if param not in params:
            missing_params.append(param)

    if missing_params:
        raise KeyError(f"Parámetros faltantes: {', '.join(missing_params)}")

    # Verificar que los parámetros sean positivos
    invalid_params = []
    for param, description in required_positive.items():
        value = params[param]
        if not isinstance(value, (int, float)) or value <= 0:
            invalid_params.append(f"{param} ({description}): {value}")

    if invalid_params:
        raise ValueError(f"Los siguientes parámetros deben ser números positivos:\n" +
                        "\n".join(f"  - {param}" for param in invalid_params))

    # Verificar número de cuchillas
    if 'n_blades' in params:
        n_blades = params['n_blades']
        if not isinstance(n_blades, int) or n_blades < 1:
            raise ValueError(f"Número de cuchillas debe ser un entero ≥ 1, recibido: {n_blades}")
        if n_blades > 12:  # Límite práctico
            raise ValueError(f"Número de cuchillas excesivo (máximo 12), recibido: {n_blades}")

    # Verificar ancho de corte si está presente
    if 'w' in params:
        w = params['w']
        if not isinstance(w, (int, float)) or w <= 0:
            raise ValueError(f"Ancho de corte debe ser positivo, recibido: {w}")
        if w > 10.0:  # Límite práctico de 10 metros
            raise ValueError(f"Ancho de corte excesivo (máximo 10 m), recibido: {w}")

    # Validaciones de coherencia física

    # L no debe ser mucho mayor que R
    if params['L'] > 2 * params['R']:
        raise ValueError(f"Longitud de cuchilla (L={params['L']:.3f}) no puede ser más del doble del radio (R={params['R']:.3f})")

    # Verificar que el momento de inercia sea razonable
    # I_plate debería ser del orden de masa * radio²
    expected_I_order = params['m_c'] * params['R']**2
    if params['I_plate'] > 10 * expected_I_order:
        raise ValueError(f"Momento de inercia del plato parece excesivo: {params['I_plate']:.3f} kg⋅m² "
                        f"(esperado del orden de {expected_I_order:.3f} kg⋅m²)")

    # Verificar que la velocidad de avance sea razonable
    if params['v_avance'] > 20.0:  # 20 m/s = 72 km/h
        raise ValueError(f"Velocidad de avance excesiva: {params['v_avance']:.1f} m/s (máximo práctico: 20 m/s)")

    # Verificar que el torque no sea excesivo
    if params['tau_input'] > 10000.0:  # 10 kN⋅m
        raise ValueError(f"Torque del motor excesivo: {params['tau_input']:.1f} N⋅m (máximo práctico: 10000 N⋅m)")

    # Validar función de torque del pasto si está presente
    if 'tau_grass_func' in params and params['tau_grass_func'] is not None:
        tau_grass_func = params['tau_grass_func']
        if not callable(tau_grass_func):
            raise ValueError("tau_grass_func debe ser una función callable")

        # Probar la función con algunos valores de tiempo
        try:
            test_times = [0.0, 1.0, 5.0]
            for t_test in test_times:
                result = tau_grass_func(t_test)
                if not isinstance(result, (int, float)):
                    raise ValueError(f"tau_grass_func debe retornar un número, retornó {type(result)} para t={t_test}")
                if result < 0:
                    raise ValueError(f"tau_grass_func debe retornar valores no negativos, retornó {result} para t={t_test}")
                if result > 1000.0:  # Límite práctico
                    raise ValueError(f"tau_grass_func retorna valores excesivos: {result} N⋅m para t={t_test} (máximo práctico: 1000 N⋅m)")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            else:
                raise ValueError(f"Error al evaluar tau_grass_func: {str(e)}")


def validate_simulation_params(mass: float, radius: float, omega: float,
                              T_end: float, dt: float) -> None:
    """
    Valida los parámetros básicos de simulación.

    Args:
        mass (float): Masa total del sistema
        radius (float): Radio principal
        omega (float): Velocidad angular de referencia
        T_end (float): Tiempo final de simulación
        dt (float): Paso de tiempo

    Raises:
        ValueError: Si algún parámetro es inválido
    """

    # Validar parámetros básicos
    if not isinstance(mass, (int, float)) or mass <= 0:
        raise ValueError(f"Masa debe ser positiva, recibido: {mass}")
    if mass > 1000.0:  # 1 tonelada
        raise ValueError(f"Masa excesiva: {mass} kg (máximo práctico: 1000 kg)")

    if not isinstance(radius, (int, float)) or radius <= 0:
        raise ValueError(f"Radio debe ser positivo, recibido: {radius}")
    if radius > 5.0:  # 5 metros
        raise ValueError(f"Radio excesivo: {radius} m (máximo práctico: 5 m)")

    if omega is not None:
        if not isinstance(omega, (int, float)) or omega <= 0:
            raise ValueError(f"Velocidad angular debe ser positiva, recibido: {omega}")
        if omega > 1000.0:  # 1000 rad/s ≈ 9550 RPM
            raise ValueError(f"Velocidad angular excesiva: {omega} rad/s (máximo práctico: 1000 rad/s)")

    if not isinstance(T_end, (int, float)) or T_end <= 0:
        raise ValueError(f"Tiempo final debe ser positivo, recibido: {T_end}")
    if T_end > 3600.0:  # 1 hora
        raise ValueError(f"Tiempo de simulación excesivo: {T_end} s (máximo práctico: 3600 s)")

    if not isinstance(dt, (int, float)) or dt <= 0:
        raise ValueError(f"Paso de tiempo debe ser positivo, recibido: {dt}")
    if dt > T_end / 10:
        raise ValueError(f"Paso de tiempo demasiado grande: {dt} s (máximo recomendado: {T_end/10:.3f} s)")
    if dt < 1e-6:
        raise ValueError(f"Paso de tiempo demasiado pequeño: {dt} s (mínimo práctico: 1e-6 s)")


# ===============================================================================
# FUNCIONES DE DENSIDAD VEGETAL ESPACIAL
# ===============================================================================

def rho_vegetation_uniform(rho_base: float = 1.0):
    """
    Densidad vegetal uniforme (constante).

    Args:
        rho_base (float): Densidad base [kg/m²]

    Returns:
        function: Función ρ(x) que retorna densidad en función de posición
    """
    def rho_func(x):
        return rho_base
    return rho_func


def rho_vegetation_zones(zone_length: float = 10.0, rho_low: float = 0.5,
                        rho_high: float = 2.0, pattern: str = "alternating"):
    """
    Zonas alternadas de vegetación baja y densa.

    Args:
        zone_length (float): Longitud de cada zona [m]
        rho_low (float): Densidad en zonas bajas [kg/m²]
        rho_high (float): Densidad en zonas densas [kg/m²]
        pattern (str): Patrón ("alternating", "low_first", "high_first")

    Returns:
        function: Función ρ(x) que retorna densidad en función de posición
    """
    def rho_func(x):
        zone_index = int(x / zone_length)

        if pattern == "alternating":
            return rho_low if zone_index % 2 == 0 else rho_high
        elif pattern == "low_first":
            return rho_low if zone_index % 2 == 0 else rho_high
        elif pattern == "high_first":
            return rho_high if zone_index % 2 == 0 else rho_low
        else:
            return rho_low if zone_index % 2 == 0 else rho_high

    return rho_func


def rho_vegetation_gaussian_patches(centers: list, amplitudes: list, widths: list,
                                   rho_base: float = 0.5):
    """
    Parches gaussianos de vegetación densa.

    Args:
        centers (list): Posiciones centrales de los parches [m]
        amplitudes (list): Amplitudes de densidad adicional [kg/m²]
        widths (list): Anchos característicos de los parches [m]
        rho_base (float): Densidad base del terreno [kg/m²]

    Returns:
        function: Función ρ(x) que retorna densidad en función de posición
    """
    def rho_func(x):
        rho = rho_base
        for center, amplitude, width in zip(centers, amplitudes, widths):
            rho += amplitude * np.exp(-0.5 * ((x - center) / width)**2)
        return max(rho, 0.0)  # Evitar densidades negativas

    return rho_func


def rho_vegetation_sigmoid_transition(x_transition: float = 15.0, rho_initial: float = 0.5,
                                     rho_final: float = 2.5, transition_width: float = 3.0):
    """
    Transición suave entre dos densidades usando función sigmoide.

    Args:
        x_transition (float): Posición central de la transición [m]
        rho_initial (float): Densidad inicial [kg/m²]
        rho_final (float): Densidad final [kg/m²]
        transition_width (float): Ancho de la zona de transición [m]

    Returns:
        function: Función ρ(x) que retorna densidad en función de posición
    """
    def rho_func(x):
        # Función sigmoide: 1 / (1 + exp(-k*(x - x0)))
        k = 4.0 / transition_width  # Factor de escala para el ancho
        sigmoid = 1.0 / (1.0 + np.exp(-k * (x - x_transition)))
        return rho_initial + (rho_final - rho_initial) * sigmoid

    return rho_func


def rho_vegetation_sinusoidal(amplitude: float = 1.0, wavelength: float = 20.0,
                             rho_base: float = 1.5, phase: float = 0.0):
    """
    Variación sinusoidal de densidad vegetal.

    Args:
        amplitude (float): Amplitud de la variación [kg/m²]
        wavelength (float): Longitud de onda espacial [m]
        rho_base (float): Densidad base [kg/m²]
        phase (float): Fase inicial [rad]

    Returns:
        function: Función ρ(x) que retorna densidad en función de posición
    """
    def rho_func(x):
        k = 2 * np.pi / wavelength  # Número de onda
        rho = rho_base + amplitude * np.sin(k * x + phase)
        return max(rho, 0.1)  # Mínimo de 0.1 kg/m² para evitar densidad cero

    return rho_func


def rho_vegetation_complex_terrain(terrain_data: dict):
    """
    Terreno complejo combinando múltiples características.

    Args:
        terrain_data (dict): Diccionario con configuración del terreno
            - 'base_density': Densidad base [kg/m²]
            - 'patches': Lista de parches gaussianos
            - 'zones': Lista de zonas rectangulares
            - 'trends': Lista de tendencias lineales

    Returns:
        function: Función ρ(x) que retorna densidad en función de posición
    """
    def rho_func(x):
        rho = terrain_data.get('base_density', 1.0)

        # Agregar parches gaussianos
        for patch in terrain_data.get('patches', []):
            center = patch['center']
            amplitude = patch['amplitude']
            width = patch['width']
            rho += amplitude * np.exp(-0.5 * ((x - center) / width)**2)

        # Agregar zonas rectangulares
        for zone in terrain_data.get('zones', []):
            x_start = zone['x_start']
            x_end = zone['x_end']
            density_add = zone['density_add']
            if x_start <= x <= x_end:
                rho += density_add

        # Agregar tendencias lineales
        for trend in terrain_data.get('trends', []):
            x_start = trend['x_start']
            x_end = trend['x_end']
            if x_start <= x <= x_end:
                slope = trend['slope']
                rho += slope * (x - x_start)

        return max(rho, 0.1)  # Mínimo de 0.1 kg/m²

    return rho_func


# ===============================================================================
# FUNCIONES DE TORQUE VARIABLE PREDEFINIDAS (TEMPORALES)
# ===============================================================================

def tau_grass_sinusoidal(amplitude: float = 10.0, frequency: float = 1.0,
                         offset: float = 15.0):
    """
    Crea una función de torque sinusoidal para simular variaciones periódicas.

    Args:
        amplitude (float): Amplitud de la variación [Nm]
        frequency (float): Frecuencia de la variación [Hz]
        offset (float): Valor base del torque [Nm]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    def tau_grass_func(t):
        return offset + amplitude * np.sin(2 * np.pi * frequency * t)
    return tau_grass_func


def tau_grass_step(t_change: float = 1.0, tau_initial: float = 10.0,
                   tau_final: float = 30.0):
    """
    Crea una función de torque escalón para simular cambios abruptos.

    Args:
        t_change (float): Tiempo del cambio [s]
        tau_initial (float): Torque inicial [Nm]
        tau_final (float): Torque final [Nm]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    def tau_grass_func(t):
        return tau_initial if t < t_change else tau_final
    return tau_grass_func


def tau_grass_ramp(t_start: float = 0.5, t_end: float = 2.0,
                   tau_initial: float = 5.0, tau_final: float = 25.0):
    """
    Crea una función de torque rampa para simular cambios graduales.

    Args:
        t_start (float): Tiempo de inicio de la rampa [s]
        t_end (float): Tiempo de fin de la rampa [s]
        tau_initial (float): Torque inicial [Nm]
        tau_final (float): Torque final [Nm]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    def tau_grass_func(t):
        if t < t_start:
            return tau_initial
        elif t > t_end:
            return tau_final
        else:
            # Interpolación lineal
            ratio = (t - t_start) / (t_end - t_start)
            return tau_initial + ratio * (tau_final - tau_initial)
    return tau_grass_func


def tau_grass_exponential(tau_base: float = 10.0, tau_max: float = 50.0,
                         time_constant: float = 1.0):
    """
    Crea una función de torque exponencial para simular acumulación gradual.

    Args:
        tau_base (float): Torque base [Nm]
        tau_max (float): Torque máximo asintótico [Nm]
        time_constant (float): Constante de tiempo [s]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    def tau_grass_func(t):
        return tau_base + (tau_max - tau_base) * (1 - np.exp(-t / time_constant))
    return tau_grass_func


# ===============================================================================
# FUNCIONES DE TORQUE ESPACIAL (BASADO EN AVANCE)
# ===============================================================================

def create_spatial_tau_grass_func(rho_vegetation_func, k_grass: float, R: float,
                                 v_avance: float):
    """
    Crea una función de torque resistivo basada en densidad vegetal espacial.

    Modelo: tau_grass(t) = k_grass * ρ(x(t)) * R
    donde x(t) = v_avance * t

    Args:
        rho_vegetation_func: Función ρ(x) que retorna densidad en función de posición
        k_grass (float): Constante de resistencia vegetal [N*s/m]
        R (float): Radio del rotary cutter [m]
        v_avance (float): Velocidad de avance [m/s]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    def tau_grass_func(t):
        x = v_avance * t  # Posición espacial
        rho = rho_vegetation_func(x)  # Densidad en esa posición
        return k_grass * rho * R

    return tau_grass_func


def tau_grass_spatial_zones(zone_length: float = 10.0, rho_low: float = 0.5,
                           rho_high: float = 2.0, k_grass: float = 15.0,
                           R: float = 0.5, v_avance: float = 3.0,
                           pattern: str = "alternating"):
    """
    Torque resistivo con zonas alternadas de vegetación.

    Args:
        zone_length (float): Longitud de cada zona [m]
        rho_low (float): Densidad en zonas bajas [kg/m²]
        rho_high (float): Densidad en zonas densas [kg/m²]
        k_grass (float): Constante de resistencia vegetal [N*s/m]
        R (float): Radio del rotary cutter [m]
        v_avance (float): Velocidad de avance [m/s]
        pattern (str): Patrón de zonas

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    rho_func = rho_vegetation_zones(zone_length, rho_low, rho_high, pattern)
    return create_spatial_tau_grass_func(rho_func, k_grass, R, v_avance)


def tau_grass_spatial_gaussian_patches(centers: list, amplitudes: list, widths: list,
                                      rho_base: float = 0.5, k_grass: float = 15.0,
                                      R: float = 0.5, v_avance: float = 3.0):
    """
    Torque resistivo con parches gaussianos de vegetación densa.

    Args:
        centers (list): Posiciones centrales de los parches [m]
        amplitudes (list): Amplitudes de densidad adicional [kg/m²]
        widths (list): Anchos característicos de los parches [m]
        rho_base (float): Densidad base del terreno [kg/m²]
        k_grass (float): Constante de resistencia vegetal [N*s/m]
        R (float): Radio del rotary cutter [m]
        v_avance (float): Velocidad de avance [m/s]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    rho_func = rho_vegetation_gaussian_patches(centers, amplitudes, widths, rho_base)
    return create_spatial_tau_grass_func(rho_func, k_grass, R, v_avance)


def tau_grass_spatial_sigmoid_transition(x_transition: float = 15.0,
                                        rho_initial: float = 0.5, rho_final: float = 2.5,
                                        transition_width: float = 3.0, k_grass: float = 15.0,
                                        R: float = 0.5, v_avance: float = 3.0):
    """
    Torque resistivo con transición suave entre densidades.

    Args:
        x_transition (float): Posición central de la transición [m]
        rho_initial (float): Densidad inicial [kg/m²]
        rho_final (float): Densidad final [kg/m²]
        transition_width (float): Ancho de la zona de transición [m]
        k_grass (float): Constante de resistencia vegetal [N*s/m]
        R (float): Radio del rotary cutter [m]
        v_avance (float): Velocidad de avance [m/s]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    rho_func = rho_vegetation_sigmoid_transition(x_transition, rho_initial,
                                               rho_final, transition_width)
    return create_spatial_tau_grass_func(rho_func, k_grass, R, v_avance)


def tau_grass_spatial_sinusoidal(amplitude: float = 1.0, wavelength: float = 20.0,
                                 rho_base: float = 1.5, phase: float = 0.0,
                                 k_grass: float = 15.0, R: float = 0.5,
                                 v_avance: float = 3.0):
    """
    Torque resistivo con variación sinusoidal espacial.

    Args:
        amplitude (float): Amplitud de la variación [kg/m²]
        wavelength (float): Longitud de onda espacial [m]
        rho_base (float): Densidad base [kg/m²]
        phase (float): Fase inicial [rad]
        k_grass (float): Constante de resistencia vegetal [N*s/m]
        R (float): Radio del rotary cutter [m]
        v_avance (float): Velocidad de avance [m/s]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    rho_func = rho_vegetation_sinusoidal(amplitude, wavelength, rho_base, phase)
    return create_spatial_tau_grass_func(rho_func, k_grass, R, v_avance)


def tau_grass_spatial_complex_terrain(terrain_data: dict, k_grass: float = 15.0,
                                     R: float = 0.5, v_avance: float = 3.0):
    """
    Torque resistivo para terreno complejo con múltiples características.

    Args:
        terrain_data (dict): Configuración del terreno complejo
        k_grass (float): Constante de resistencia vegetal [N*s/m]
        R (float): Radio del rotary cutter [m]
        v_avance (float): Velocidad de avance [m/s]

    Returns:
        function: Función tau_grass(t) que retorna torque en función del tiempo
    """
    rho_func = rho_vegetation_complex_terrain(terrain_data)
    return create_spatial_tau_grass_func(rho_func, k_grass, R, v_avance)


# ===============================================================================
# FUNCIONES PARA CONDICIONES INICIALES
# ===============================================================================

def create_initial_conditions(theta0: float = 0.0, omega0: float = 0.0) -> list:
    """
    Crea condiciones iniciales validadas para la simulación.

    Args:
        theta0 (float): Ángulo inicial en radianes
        omega0 (float): Velocidad angular inicial en rad/s

    Returns:
        list: Condiciones iniciales [theta0, omega0]

    Raises:
        ValueError: Si las condiciones iniciales son inválidas
    """
    # Validar rangos
    if abs(theta0) > 100.0:
        raise ValueError(f"Ángulo inicial excesivo: {theta0} rad (máximo: ±100 rad)")

    if abs(omega0) > 1000.0:
        raise ValueError(f"Velocidad angular inicial excesiva: {omega0} rad/s (máximo: ±1000 rad/s)")

    return [float(theta0), float(omega0)]


def initial_conditions_from_rpm(theta0: float = 0.0, rpm0: float = 0.0) -> list:
    """
    Crea condiciones iniciales a partir de RPM.

    Args:
        theta0 (float): Ángulo inicial en radianes
        rpm0 (float): Velocidad inicial en RPM

    Returns:
        list: Condiciones iniciales [theta0, omega0]
    """
    omega0 = rpm0 * 2 * np.pi / 60  # Convertir RPM a rad/s
    return create_initial_conditions(theta0, omega0)


def initial_conditions_spinning(omega0: float, revolutions: float = 0.0) -> list:
    """
    Crea condiciones iniciales para un sistema ya girando.

    Args:
        omega0 (float): Velocidad angular inicial en rad/s
        revolutions (float): Número de revoluciones iniciales

    Returns:
        list: Condiciones iniciales [theta0, omega0]
    """
    theta0 = revolutions * 2 * np.pi
    return create_initial_conditions(theta0, omega0)


def initial_conditions_blade_angle(blade_angle_deg: float, omega0: float = 0.0,
                                  n_blades: int = 2) -> list:
    """
    Crea condiciones iniciales basadas en el ángulo de las cuchillas.

    Args:
        blade_angle_deg (float): Ángulo de las cuchillas en grados
        omega0 (float): Velocidad angular inicial en rad/s
        n_blades (int): Número de cuchillas

    Returns:
        list: Condiciones iniciales [theta0, omega0]
    """
    # Convertir ángulo de cuchilla a ángulo del plato
    blade_angle_rad = np.deg2rad(blade_angle_deg)

    # El ángulo del plato depende de la configuración de cuchillas
    # Para cuchillas simétricas, el ángulo del plato es el ángulo de cuchilla
    theta0 = blade_angle_rad

    return create_initial_conditions(theta0, omega0)


def initial_conditions_moment_of_inertia_function(params: Dict, theta0: float = 0.0,
                                                 omega0: float = 0.0) -> Tuple[list, Dict]:
    """
    Crea condiciones iniciales y parámetros con momento de inercia variable I(θ).

    Args:
        params (Dict): Parámetros base del sistema
        theta0 (float): Ángulo inicial en radianes
        omega0 (float): Velocidad angular inicial en rad/s

    Returns:
        Tuple[list, Dict]: (condiciones_iniciales, parámetros_modificados)

    Note:
        Esta función prepara el sistema para simular el efecto de cuchillas
        que se extienden/contraen según el ángulo, afectando I(θ).
    """
    y0 = create_initial_conditions(theta0, omega0)

    # Los parámetros se mantienen igual por ahora
    # En el futuro se puede implementar I(θ) variable
    modified_params = params.copy()

    # Agregar información sobre el estado inicial
    modified_params['_initial_setup'] = {
        'theta0': theta0,
        'omega0': omega0,
        'variable_inertia': False  # Para futuras implementaciones
    }

    return y0, modified_params


# ===============================================================================
# FUNCIONES DE UTILIDAD Y CONFIGURACIÓN
# ===============================================================================

def create_default_params(mass: float = 10.0, radius: float = 0.5,
                         tau_input: float = 100.0) -> Dict:
    """
    Crea parámetros por defecto para el modelo avanzado basados en parámetros básicos.

    Args:
        mass (float): Masa total aproximada del sistema [kg]
        radius (float): Radio principal [m]
        tau_input (float): Torque de entrada del motor [Nm]

    Returns:
        Dict: Parámetros completos para el modelo avanzado
    """
    params = {
        # Parámetros geométricos
        'I_plate': 0.4 * mass * radius**2,  # ~40% de la masa en el plato
        'm_c': 0.3 * mass,  # ~30% de la masa en cada cuchilla
        'R': radius,  # Radio al perno
        'L': 0.3 * radius,  # Longitud de cuchilla (30% del radio)
        'n_blades': 2,  # Número de cuchillas

        # Parámetros de control
        'tau_input': tau_input,  # Torque del motor

        # Parámetros de resistencia
        'b': 0.1,  # Fricción viscosa [N*m*s/rad]
        'c_drag': 0.01,  # Arrastre aerodinámico [N*m*s^2/rad^2]

        # Parámetros de vegetación y corte
        'rho_veg': 0.5,  # Densidad de vegetación [kg/m^2]
        'k_grass': 10.0,  # Constante de resistencia vegetal [N*s/m]
        'v_avance': 2.0,  # Velocidad de avance [m/s]
        'w': 1.8,  # Ancho de corte [m] (típico para MX9/MX10)
    }

    # Validar parámetros creados
    try:
        validate_params(params)
    except (ValueError, KeyError) as e:
        raise ValueError(f"Error en parámetros por defecto: {str(e)}")

    return params


def create_validated_params(base_params: Dict, **overrides) -> Dict:
    """
    Crea parámetros validados combinando parámetros base con modificaciones.

    Args:
        base_params (Dict): Parámetros base
        **overrides: Parámetros a modificar o agregar

    Returns:
        Dict: Parámetros validados

    Raises:
        ValueError: Si los parámetros resultantes no son válidos
    """
    # Combinar parámetros
    params = base_params.copy()
    params.update(overrides)

    # Validar parámetros combinados
    validate_params(params)

    return params


# ===============================================================================
# CONFIGURATION WRAPPER - SISTEMA CENTRALIZADO DE CONFIGURACIÓN
# ===============================================================================

class RotaryCutterConfig:
    """
    Wrapper centralizado para configuración y validación de parámetros del rotary cutter.

    Elimina la duplicación de código y centraliza toda la lógica de:
    - Creación de parámetros por defecto
    - Validación de parámetros
    - Conversión entre formatos
    - Mapeo de parámetros desde archivos
    - Configuración de funciones de torque
    """

    # Mapeo estándar de parámetros para archivos
    PARAM_MAPPING = {
        'mass': 'mass', 'masa': 'mass', 'peso': 'mass',
        'tau_input': 'tau_input', 'torque_motor': 'tau_input', 'torque': 'tau_input',
        'n_blades': 'n_blades', 'cuchillas': 'n_blades', 'num_cuchillas': 'n_blades',
        'r': 'R', 'radio': 'R', 'radius': 'R',
        'omega_ref': 'omega_ref', 'velocidad_angular': 'omega_ref', 'omega': 'omega_ref',
        'mass_plate_percent': 'mass_plate_percent', 'masa_plato_percent': 'mass_plate_percent',
        'l_percent': 'L_percent', 'longitud_percent': 'L_percent',
        'b': 'b', 'friccion': 'b', 'friccion_viscosa': 'b',
        'c_drag': 'c_drag', 'arrastre': 'c_drag', 'arrastre_aerodinamico': 'c_drag',
        'rho_veg': 'rho_veg', 'densidad_vegetal': 'rho_veg', 'densidad': 'rho_veg',
        'v_avance': 'v_avance', 'velocidad_avance': 'v_avance', 'velocidad': 'v_avance',
        'k_grass': 'k_grass', 'resistencia_vegetal': 'k_grass', 'resistencia': 'k_grass',
        'w': 'w', 'ancho': 'w', 'ancho_corte': 'w'
    }

    def __init__(self, mass: float = 15.0, radius: float = 0.6, tau_input: float = 200.0):
        """
        Inicializa la configuración con parámetros básicos.

        Args:
            mass (float): Masa total aproximada del sistema [kg]
            radius (float): Radio principal [m]
            tau_input (float): Torque de entrada del motor [Nm]
        """
        self.base_mass = mass
        self.base_radius = radius
        self.base_tau_input = tau_input
        self._params = None
        self._validated = False

        # Crear parámetros por defecto
        self.reset_to_defaults()

    def reset_to_defaults(self):
        """Resetea la configuración a valores por defecto."""
        self._params = create_default_params(self.base_mass, self.base_radius, self.base_tau_input)
        self._validated = True

    @classmethod
    def from_dict(cls, config_dict: Dict, name: str = "Config"):
        """
        Crea una configuración desde un diccionario (ej: desde archivo Excel).

        Args:
            config_dict (Dict): Diccionario con parámetros
            name (str): Nombre de la configuración

        Returns:
            RotaryCutterConfig: Instancia configurada
        """
        # Extraer parámetros básicos con valores por defecto
        mass = config_dict.get('mass', 15.0)
        radius = config_dict.get('R', 0.6)
        tau_input = config_dict.get('tau_input', 200.0)

        # Crear instancia
        config = cls(mass, radius, tau_input)
        config.name = name

        # Actualizar con parámetros del diccionario
        config.update_params(**config_dict)

        return config

    @classmethod
    def from_file_row(cls, row_dict: Dict, column_mapping: Dict = None):
        """
        Crea una configuración desde una fila de archivo (CSV/Excel).

        Args:
            row_dict (Dict): Diccionario con datos de la fila
            column_mapping (Dict): Mapeo personalizado de columnas

        Returns:
            RotaryCutterConfig: Instancia configurada
        """
        if column_mapping is None:
            column_mapping = cls.PARAM_MAPPING

        # Mapear parámetros
        mapped_params = {}
        config_name = row_dict.get('name', row_dict.get('Nombre', 'Config'))

        for key, value in row_dict.items():
            if key.lower() in column_mapping and value is not None:
                try:
                    # Convertir a número si es posible
                    if isinstance(value, str):
                        value = value.replace(',', '.')

                    # Convertir a entero para n_blades
                    param_name = column_mapping[key.lower()]
                    if param_name == 'n_blades':
                        mapped_params[param_name] = int(float(value))
                    else:
                        mapped_params[param_name] = float(value)
                except (ValueError, TypeError):
                    mapped_params[column_mapping[key.lower()]] = value

        # Crear configuración
        return cls.from_dict(mapped_params, config_name)

    def update_params(self, **kwargs):
        """
        Actualiza parámetros de la configuración.

        Args:
            **kwargs: Parámetros a actualizar
        """
        # Filtrar parámetros válidos (excluir 'name')
        valid_params = {k: v for k, v in kwargs.items() if k != 'name' and k in self._params}

        # Actualizar parámetros
        self._params.update(valid_params)
        self._validated = False

        # Re-validar
        self.validate()

    def validate(self):
        """Valida la configuración actual."""
        try:
            validate_params(self._params)
            self._validated = True
        except Exception as e:
            self._validated = False
            raise ValueError(f"Configuración inválida: {str(e)}")

    def get_params(self) -> Dict:
        """
        Obtiene los parámetros validados.

        Returns:
            Dict: Parámetros del sistema
        """
        if not self._validated:
            self.validate()
        return self._params.copy()

    def set_torque_function(self, torque_func):
        """
        Establece una función de torque personalizada.

        Args:
            torque_func: Función que toma tiempo y retorna torque
        """
        self._params['tau_grass_func'] = torque_func
        self._validated = False
        self.validate()

    def get_summary(self) -> Dict:
        """
        Obtiene un resumen de la configuración.

        Returns:
            Dict: Resumen con parámetros clave
        """
        params = self.get_params()
        return {
            'name': getattr(self, 'name', 'Config'),
            'mass_total': params['m_c'] * params['n_blades'] + params['I_plate'] / (0.5 * params['R']**2),
            'tau_input': params['tau_input'],
            'n_blades': params['n_blades'],
            'radius': params['R'],
            'omega_ref': params.get('omega_ref', 60.0),
            'validated': self._validated
        }

    def simulate(self, t_max: float = 10.0, t_eval: Optional[np.ndarray] = None,
                 y0: Optional[list] = None) -> Dict:
        """
        Ejecuta la simulación con la configuración actual.

        Args:
            t_max (float): Tiempo máximo de simulación
            t_eval (Optional[np.ndarray]): Tiempos de evaluación
            y0 (Optional[list]): Condiciones iniciales

        Returns:
            Dict: Resultados de la simulación
        """
        params = self.get_params()
        return simulate_advanced_configuration(params, t_max, t_eval, y0)

    def __str__(self):
        """Representación en string de la configuración."""
        summary = self.get_summary()
        return f"RotaryCutterConfig(name='{summary['name']}', validated={summary['validated']})"

    def __repr__(self):
        return self.__str__()


class ConfigurationManager:
    """
    Gestor de múltiples configuraciones para comparación masiva.
    """

    def __init__(self):
        self.configurations = []

    def add_config(self, config: RotaryCutterConfig):
        """Agrega una configuración al gestor."""
        self.configurations.append(config)

    def load_from_dataframe(self, df, name_column: str = 'Nombre'):
        """
        Carga múltiples configuraciones desde un DataFrame.

        Args:
            df: DataFrame con configuraciones
            name_column (str): Nombre de la columna con nombres de configuración
        """
        self.configurations = []

        for idx, row in df.iterrows():
            row_dict = row.to_dict()

            # Buscar columna de nombre de forma flexible
            config_name = None
            name_columns = [name_column, 'Nombre', 'nombre', 'Name', 'name', 'Config', 'config']

            for col_name in name_columns:
                if col_name in row_dict and pd.notna(row_dict[col_name]):
                    config_name = str(row_dict[col_name])
                    break

            # Si no se encuentra nombre, usar índice
            if config_name is None:
                config_name = f"Config_{idx + 1}"

            row_dict['name'] = config_name

            try:
                config = RotaryCutterConfig.from_file_row(row_dict)
                config.name = config_name
                self.add_config(config)
            except Exception as e:
                print(f"Error cargando configuración {config_name}: {e}")

    def get_config_by_name(self, name: str) -> Optional[RotaryCutterConfig]:
        """Obtiene una configuración por nombre."""
        for config in self.configurations:
            if getattr(config, 'name', '') == name:
                return config
        return None

    def get_summary_dataframe(self):
        """
        Obtiene un DataFrame con resumen de todas las configuraciones.

        Returns:
            pd.DataFrame: Resumen de configuraciones
        """
        summaries = [config.get_summary() for config in self.configurations]
        return pd.DataFrame(summaries)

    def simulate_all(self, selected_names: list = None, **sim_kwargs) -> Dict:
        """
        Simula múltiples configuraciones.

        Args:
            selected_names (list): Nombres de configuraciones a simular
            **sim_kwargs: Argumentos para la simulación

        Returns:
            Dict: Resultados de todas las simulaciones
        """
        if selected_names is None:
            configs_to_simulate = self.configurations
        else:
            configs_to_simulate = [self.get_config_by_name(name) for name in selected_names]
            configs_to_simulate = [c for c in configs_to_simulate if c is not None]

        results = {}
        for config in configs_to_simulate:
            try:
                result = config.simulate(**sim_kwargs)
                results[getattr(config, 'name', 'Unknown')] = {
                    'config': config,
                    'result': result,
                    'summary': config.get_summary()
                }
            except Exception as e:
                results[getattr(config, 'name', 'Unknown')] = {
                    'config': config,
                    'error': str(e),
                    'summary': config.get_summary()
                }

        return results

    def __len__(self):
        return len(self.configurations)

    def __iter__(self):
        return iter(self.configurations)


def run_simulation(mass: float, radius: float, omega: float = None,
                  T_end: float = 5.0, dt: float = 0.01,
                  geometry: str = "disk", torque_type: str = "advanced_model",
                  use_advanced_model: bool = True,
                  advanced_params: Optional[Dict] = None,
                  y0: Optional[list] = None) -> Dict:
    """
    Ejecuta la simulación del rotary cutter usando el modelo avanzado con EDOs.

    Args:
        mass (float): Masa total aproximada del sistema en kg
        radius (float): Radio principal en metros
        omega (float): Velocidad angular de referencia en rad/s (opcional, para estimación de torque)
        T_end (float): Tiempo final de simulación en segundos
        dt (float): Paso de tiempo en segundos
        geometry (str): Tipo de geometría (mantenido por compatibilidad)
        torque_type (str): Tipo de perfil de torque (mantenido por compatibilidad)
        use_advanced_model (bool): Siempre True (mantenido por compatibilidad)
        advanced_params (Optional[Dict]): Parámetros específicos del modelo avanzado
        y0 (Optional[list]): Condiciones iniciales [theta(0), omega(0)] en [rad, rad/s]

    Returns:
        Dict: Diccionario con resultados de la simulación
    """
    # Validación de parámetros básicos de simulación
    validate_simulation_params(mass, radius, omega, T_end, dt)

    # Crear parámetros para el modelo avanzado
    if advanced_params is None:
        # Crear parámetros por defecto basados en los parámetros básicos
        if omega is None:
            omega = 10.0  # Valor por defecto
        tau_input = mass * radius * omega * 10  # Estimación del torque necesario
        params = create_default_params(mass, radius, tau_input)
    else:
        params = advanced_params.copy()
        # Asegurar que los parámetros básicos estén incluidos
        if 'I_plate' not in params:
            params['I_plate'] = 0.4 * mass * radius**2
        if 'R' not in params:
            params['R'] = radius
        if omega is None:
            omega = 10.0  # Valor por defecto

    # Ejecutar simulación avanzada
    results = simulate_advanced_configuration(params, T_end,
                                            np.linspace(0, T_end, int(T_end/dt) + 1),
                                            y0=y0)

    # Agregar compatibilidad con interfaz existente
    results['angular_velocity'] = omega  # Velocidad angular de referencia
    results['statistics']['time_step'] = dt
    results['statistics']['geometry'] = geometry
    results['statistics']['torque_type'] = 'advanced_model'

    # Agregar información sobre condiciones iniciales
    if y0 is not None:
        results['statistics']['initial_theta'] = y0[0]
        results['statistics']['initial_omega'] = y0[1]
    else:
        results['statistics']['initial_theta'] = 0.0
        results['statistics']['initial_omega'] = 0.0

    return results


# ===============================================================================
# FUNCIONES DE ANÁLISIS Y EXPORTACIÓN
# ===============================================================================

def analyze_performance(results: Dict) -> Dict:
    """
    Realiza análisis avanzado de rendimiento del rotary cutter.

    Args:
        results (Dict): Resultados de la simulación

    Returns:
        Dict: Métricas de rendimiento adicionales
    """
    time = results['time']
    omega = results.get('omega', results.get('angular_velocity', 0))
    torque = results['torque']
    power = results['power']

    # Análisis de eficiencia básico
    if isinstance(omega, np.ndarray):
        efficiency = np.mean(power) / (np.mean(np.abs(torque)) * np.mean(np.abs(omega)) + 1e-10)
        omega_stability = 1 - (np.std(omega) / (np.mean(np.abs(omega)) + 1e-10))
    else:
        efficiency = np.mean(power) / (np.mean(np.abs(torque)) * abs(omega) + 1e-10)
        omega_stability = 1.0  # Constante en modelo simplificado

    # Análisis de estabilidad
    torque_stability = 1 - (np.std(torque) / (np.mean(np.abs(torque)) + 1e-10))
    power_stability = 1 - (np.std(power) / (np.mean(np.abs(power)) + 1e-10))

    # Análisis de frecuencias (si hay suficientes puntos)
    if len(time) > 10:
        dt = time[1] - time[0]
        freqs = np.fft.fftfreq(len(time), dt)
        torque_fft = np.fft.fft(torque)
        dominant_freq = freqs[np.argmax(np.abs(torque_fft[1:len(time)//2])) + 1]
    else:
        dominant_freq = 0.0

    # Métricas básicas
    performance_metrics = {
        'efficiency': efficiency,
        'omega_stability': omega_stability,
        'torque_stability': torque_stability,
        'power_stability': power_stability,
        'dominant_frequency': dominant_freq,
        'avg_power': np.mean(power),
        'peak_power': np.max(power),
        'energy_total': results.get('work_total', 0)
    }

    # Agregar métricas avanzadas si están disponibles
    if 'advanced_metrics' in results:
        advanced = results['advanced_metrics']
        performance_metrics.update({
            'cutting_efficiency': advanced['eta'],  # Eficiencia energética de corte
            'area_efficiency': advanced['epsilon'],  # m²/J
            'total_area_cut': advanced['A_total'],  # m²
            'useful_energy': advanced['E_util'],  # J
            'total_energy': advanced['E_total'],  # J
            'cutting_width': advanced['cutting_width'],  # m
            'cutting_speed': advanced['cutting_speed'],  # m/s
            'power_total_avg': advanced['power_total_avg'],  # W
            'power_util_avg': advanced['power_util_avg'],  # W
        })

    return performance_metrics


def export_results_to_excel(results: Dict, filename: str = "simulation_results.xlsx") -> None:
    """
    Exporta los resultados de la simulación a un archivo Excel (compatible con ambos modelos).

    Args:
        results (Dict): Diccionario con resultados de la simulación
        filename (str): Nombre del archivo de salida
    """
    # Crear DataFrame con series temporales
    time_series_data = {
        'Time (s)': results['time'],
        'Torque (N⋅m)': results['torque'],
        'Kinetic Energy (J)': results['kinetic_energy'],
        'Power (W)': results['power']
    }

    # Agregar datos específicos del modelo avanzado si están disponibles
    if 'theta' in results:
        time_series_data['Theta (rad)'] = results['theta']
    if 'omega' in results:
        time_series_data['Omega (rad/s)'] = results['omega']

    df_time_series = pd.DataFrame(time_series_data)

    # Crear DataFrame con estadísticas
    stats = results['statistics']
    df_stats = pd.DataFrame([stats])

    # Análisis de rendimiento
    performance = analyze_performance(results)
    df_performance = pd.DataFrame([performance])

    # Métricas avanzadas si están disponibles
    df_advanced = None
    if 'advanced_metrics' in results:
        df_advanced = pd.DataFrame([results['advanced_metrics']])

    # Guardar en Excel con múltiples hojas
    with pd.ExcelWriter(f"data/{filename}", engine='openpyxl') as writer:
        df_time_series.to_excel(writer, sheet_name='Time_Series', index=False)
        df_stats.to_excel(writer, sheet_name='Statistics', index=False)
        df_performance.to_excel(writer, sheet_name='Performance', index=False)

        # Agregar hoja de métricas avanzadas si están disponibles
        if df_advanced is not None:
            df_advanced.to_excel(writer, sheet_name='Advanced_Metrics', index=False)

    print(f"Resultados exportados a data/{filename}")
    if df_advanced is not None:
        print("  - Incluye métricas avanzadas de eficiencia y corte")


def compare_configurations(configs: list, labels: list = None) -> Dict:
    """
    Compara múltiples configuraciones de rotary cutter.

    Args:
        configs (list): Lista de diccionarios de parámetros para simular
        labels (list): Etiquetas para cada configuración

    Returns:
        Dict: Resultados comparativos
    """
    if labels is None:
        labels = [f"Config_{i+1}" for i in range(len(configs))]

    comparison_results = {
        'labels': labels,
        'results': [],
        'performance': [],
        'summary': {}
    }

    for i, config in enumerate(configs):
        try:
            # Ejecutar simulación avanzada para cada configuración
            result = run_simulation(**config)
            performance = analyze_performance(result)

            comparison_results['results'].append(result)
            comparison_results['performance'].append(performance)

        except Exception as e:
            print(f"Error en configuración {labels[i]}: {str(e)}")
            comparison_results['results'].append(None)
            comparison_results['performance'].append(None)

    # Crear resumen comparativo
    valid_performances = [p for p in comparison_results['performance'] if p is not None]
    if valid_performances:
        comparison_results['summary'] = {
            'best_efficiency': max(valid_performances, key=lambda x: x['efficiency']),
            'best_stability': max(valid_performances, key=lambda x: x['torque_stability']),
            'highest_power': max(valid_performances, key=lambda x: x['peak_power'])
        }

    return comparison_results


if __name__ == "__main__":
    print("=== SIMULACIÓN DE ROTARY CUTTER - MODELO AVANZADO CON EDOs ===")
    print()

    # Parámetros de ejemplo
    mass = 10.0  # kg
    radius = 0.5  # m
    omega = 10.0  # rad/s

    print("0. VALIDACIÓN DE PARÁMETROS Y CONDICIONES INICIALES")
    print("-" * 60)

    # Demostrar validación de parámetros
    try:
        # Intentar crear parámetros inválidos
        invalid_params = {
            'I_plate': -1.0,  # Negativo (inválido)
            'm_c': 1.5,
            'R': 0.5,
            'L': 0.15,
            'n_blades': 2,
            'tau_input': 150.0,
            'b': 0.2,
            'c_drag': 0.05,
            'rho_veg': 1.0,
            'k_grass': 15.0,
            'v_avance': 3.0,
            'w': 1.8
        }
        validate_params(invalid_params)
    except ValueError as e:
        print(f"✅ Validación de parámetros funcionando - Error detectado: {str(e)[:80]}...")

    try:
        # Intentar parámetros de simulación inválidos
        validate_simulation_params(-5.0, 0.5, 10.0, 2.0, 0.01)  # Masa negativa
    except ValueError as e:
        print(f"✅ Validación de simulación funcionando - Error detectado: {str(e)[:80]}...")

    # Demostrar validación de condiciones iniciales
    try:
        # Intentar condiciones iniciales inválidas
        invalid_y0 = create_initial_conditions(theta0=200.0, omega0=50.0)  # Ángulo excesivo
    except ValueError as e:
        print(f"✅ Validación de condiciones iniciales funcionando - Error detectado: {str(e)[:80]}...")

    # Crear condiciones iniciales válidas
    y0_rest = create_initial_conditions(0.0, 0.0)  # Reposo
    y0_spinning = initial_conditions_from_rpm(0.0, 500.0)  # 500 RPM
    y0_blade_angle = initial_conditions_blade_angle(45.0, 0.0)  # Cuchillas a 45°

    print("✅ Sistema de validación operativo")
    print(f"✅ Condiciones iniciales creadas: reposo {y0_rest}, girando {y0_spinning}, ángulo {y0_blade_angle}")
    print()

    print("1. SIMULACIÓN CON PARÁMETROS POR DEFECTO")
    print("-" * 50)

    # Ejecutar simulación con parámetros por defecto
    results_default = run_simulation(mass, radius, omega, T_end=2.0, dt=0.01)

    stats_default = results_default['statistics']
    print(f"Momento de inercia total: {results_default['moment_of_inertia']:.4f} kg⋅m²")
    print(f"Velocidad angular final: {results_default['omega'][-1]:.4f} rad/s")
    print(f"Torque máximo: {stats_default['torque_max']:.4f} N⋅m")
    print(f"Torque RMS: {stats_default['torque_rms']:.4f} N⋅m")
    print(f"Energía promedio: {stats_default['energy_avg']:.4f} J")
    print(f"Trabajo total: {results_default['work_total']:.4f} J")
    print(f"Puntos de integración: {stats_default['integration_points']}")
    print()

    print("2. SIMULACIÓN CON PARÁMETROS PERSONALIZADOS")
    print("-" * 50)

    # Crear parámetros base y modificarlos de forma validada
    base_params = create_default_params(mass, radius, mass * radius * omega * 10)

    # Usar create_validated_params para modificaciones seguras
    try:
        custom_params = create_validated_params(
            base_params,
            n_blades=4,          # número de cuchillas (más cuchillas)
            tau_input=200.0,     # Nm (más torque)
            b=0.3,               # fricción viscosa (más fricción)
            c_drag=0.08,         # arrastre aerodinámico (más arrastre)
            rho_veg=1.5,         # densidad de vegetación (más densa)
            k_grass=20.0,        # resistencia vegetal (más resistencia)
            v_avance=4.0,        # velocidad de avance (más rápido)
            m_c=1.2              # masa por cuchilla ajustada
        )
        print("Parámetros personalizados validados correctamente")
    except ValueError as e:
        print(f"Error en parámetros personalizados: {e}")
        # Usar parámetros por defecto como respaldo
        custom_params = base_params

    # Ejecutar simulación personalizada
    results_custom = run_simulation(mass, radius, omega, T_end=2.0, dt=0.01,
                                   advanced_params=custom_params)

    stats_custom = results_custom['statistics']
    print(f"Momento de inercia total: {results_custom['moment_of_inertia']:.4f} kg⋅m²")
    print(f"Velocidad angular final: {results_custom['omega'][-1]:.4f} rad/s")
    print(f"Torque máximo: {stats_custom['torque_max']:.4f} N⋅m")
    print(f"Torque RMS: {stats_custom['torque_rms']:.4f} N⋅m")
    print(f"Energía promedio: {stats_custom['energy_avg']:.4f} J")
    print(f"Trabajo total: {results_custom['work_total']:.4f} J")
    print(f"Puntos de integración: {stats_custom['integration_points']}")
    print()

    print("3. SIMULACIÓN CON CONDICIONES INICIALES DIFERENTES")
    print("-" * 60)

    # Demostrar diferentes condiciones iniciales
    print("Probando diferentes condiciones iniciales:")

    # Simulación con sistema ya girando
    y0_spinning = initial_conditions_from_rpm(theta0=0.0, rpm0=300.0)  # 300 RPM inicial

    try:
        results_spinning = run_simulation(mass, radius, omega, T_end=2.0, dt=0.01,
                                         y0=y0_spinning)

        print(f" Simulación con arranque girando (300 RPM):")
        print(f" Velocidad inicial: {results_spinning['omega'][0]:.2f} rad/s")
        print(f" Velocidad final: {results_spinning['omega'][-1]:.2f} rad/s")
        print(f" Cambio de velocidad: {results_spinning['omega'][-1] - results_spinning['omega'][0]:.2f} rad/s")

        # Comparar con arranque desde reposo
        results_rest = run_simulation(mass, radius, omega, T_end=2.0, dt=0.01,
                                     y0=[0.0, 0.0])

        print(f"Comparación con arranque desde reposo:")
        print(f"Velocidad final (reposo): {results_rest['omega'][-1]:.2f} rad/s")
        print(f"Velocidad final (girando): {results_spinning['omega'][-1]:.2f} rad/s")
        print(f"Diferencia: {results_spinning['omega'][-1] - results_rest['omega'][-1]:.2f} rad/s")

    except Exception as e:
        print(f"Error en simulación con condiciones iniciales: {e}")
        results_spinning = None

    # Simulación con ángulo de cuchilla específico
    y0_blade = initial_conditions_blade_angle(blade_angle_deg=90.0, omega0=0.0)

    try:
        results_blade = run_simulation(mass, radius, omega, T_end=2.0, dt=0.01,
                                      y0=y0_blade)

        print(f"Simulación con ángulo de cuchilla inicial (90°):")
        print(f"Ángulo inicial: {results_blade['theta'][0]:.3f} rad ({np.rad2deg(results_blade['theta'][0]):.1f}°)")
        print(f"Ángulo final: {results_blade['theta'][-1]:.3f} rad ({np.rad2deg(results_blade['theta'][-1]):.1f}°)")
        print(f"Revoluciones completadas: {(results_blade['theta'][-1] - results_blade['theta'][0])/(2*np.pi):.2f}")

    except Exception as e:
        print(f"Error en simulación con ángulo de cuchilla: {e}")
        results_blade = None

    print()

    print("4. SIMULACIÓN CON TORQUE VARIABLE TEMPORAL")
    print("-" * 60)

    # Demostrar diferentes funciones de torque variable temporal
    print("Probando funciones de torque variable temporal:")

    # Función sinusoidal
    tau_sin_func = tau_grass_sinusoidal(amplitude=15.0, frequency=0.5, offset=20.0)

    # Probar validación de función
    try:
        variable_params = create_validated_params(
            base_params,
            tau_grass_func=tau_sin_func,  # Usar torque sinusoidal
            tau_input=180.0
        )
        print("Función de torque sinusoidal validada correctamente")

        # Ejecutar simulación con torque variable
        results_variable = run_simulation(mass, radius, omega, T_end=2.0, dt=0.01,
                                         advanced_params=variable_params)

        stats_variable = results_variable['statistics']
        print(f"Velocidad angular final: {results_variable['omega'][-1]:.2f} rad/s")
        print(f"Torque máximo: {stats_variable['torque_max']:.2f} N⋅m")

        # Mostrar métricas avanzadas
        if 'advanced_metrics' in results_variable:
            adv_var = results_variable['advanced_metrics']
            print(f"Eficiencia de corte: {adv_var['eta']:.4f} ({adv_var['eta']*100:.2f}%)")

    except ValueError as e:
        print(f"Error con función de torque variable: {e}")
        results_variable = None

    print()

    print("5. SIMULACIÓN CON TORQUE ESPACIAL (BASADO EN AVANCE)")
    print("-" * 60)

    # Demostrar funciones de torque basadas en densidad vegetal espacial
    print("Probando funciones de torque espacial:")

    # Obtener parámetros del sistema para las funciones espaciales
    k_grass = base_params['k_grass']
    R = base_params['R']
    v_avance = base_params['v_avance']

    # 1. Zonas alternadas
    tau_zones_func = tau_grass_spatial_zones(
        zone_length=5.0,  # Zonas de 5 metros
        rho_low=0.3,      # Zona ligera
        rho_high=2.0,     # Zona densa
        k_grass=k_grass, R=R, v_avance=v_avance
    )

    # 2. Parches gaussianos
    tau_patches_func = tau_grass_spatial_gaussian_patches(
        centers=[8.0, 15.0],      # Parches en x=8m y x=15m
        amplitudes=[1.5, 2.0],    # Amplitudes de densidad
        widths=[2.0, 3.0],        # Anchos de los parches
        rho_base=0.5,             # Densidad base
        k_grass=k_grass, R=R, v_avance=v_avance
    )

    # 3. Transición sigmoide
    tau_sigmoid_func = tau_grass_spatial_sigmoid_transition(
        x_transition=10.0,        # Transición en x=10m
        rho_initial=0.4,          # Densidad inicial
        rho_final=2.5,            # Densidad final
        transition_width=4.0,     # Ancho de transición
        k_grass=k_grass, R=R, v_avance=v_avance
    )

    # 4. Variación sinusoidal espacial
    tau_spatial_sin_func = tau_grass_spatial_sinusoidal(
        amplitude=1.0,            # Amplitud de variación
        wavelength=12.0,          # Longitud de onda de 12m
        rho_base=1.2,             # Densidad base
        phase=0.0,                # Sin desfase
        k_grass=k_grass, R=R, v_avance=v_avance
    )

    # Probar simulación con zonas alternadas
    try:
        spatial_params = create_validated_params(
            base_params,
            tau_grass_func=tau_zones_func,
            tau_input=180.0
        )
        print("Función de torque espacial (zonas) validada correctamente")

        results_spatial = run_simulation(mass, radius, omega, T_end=3.0, dt=0.01,
                                        advanced_params=spatial_params)

        stats_spatial = results_spatial['statistics']
        print(f"Velocidad angular final: {results_spatial['omega'][-1]:.2f} rad/s")
        print(f"Torque máximo: {stats_spatial['torque_max']:.2f} N⋅m")
        print(f"Distancia recorrida: {v_avance * 3.0:.1f} m")

        # Mostrar métricas avanzadas
        if 'advanced_metrics' in results_spatial:
            adv_spatial = results_spatial['advanced_metrics']
            print(f"Eficiencia de corte: {adv_spatial['eta']:.4f} ({adv_spatial['eta']*100:.2f}%)")
            print(f"Área cortada: {adv_spatial['A_total']:.2f} m²")

    except ValueError as e:
        print(f"Error con función de torque espacial: {e}")
        results_spatial = None

    # Probar terreno complejo
    try:
        complex_terrain = {
            'base_density': 0.8,
            'patches': [
                {'center': 5.0, 'amplitude': 1.2, 'width': 2.0},
                {'center': 12.0, 'amplitude': 0.8, 'width': 1.5}
            ],
            'zones': [
                {'x_start': 8.0, 'x_end': 10.0, 'density_add': 1.0}
            ],
            'trends': [
                {'x_start': 15.0, 'x_end': 20.0, 'slope': 0.1}
            ]
        }

        tau_complex_func = tau_grass_spatial_complex_terrain(
            complex_terrain, k_grass=k_grass, R=R, v_avance=v_avance
        )

        complex_params = create_validated_params(
            base_params,
            tau_grass_func=tau_complex_func,
            tau_input=200.0
        )
        print("Función de torque espacial (terreno complejo) validada correctamente")

        results_complex = run_simulation(mass, radius, omega, T_end=3.0, dt=0.01,
                                        advanced_params=complex_params)

        print(f"Terreno complejo - Velocidad final: {results_complex['omega'][-1]:.2f} rad/s")

    except ValueError as e:
        print(f"Error con terreno complejo: {e}")
        results_complex = None

    print()

    print("6. ANÁLISIS DE RENDIMIENTO COMPARATIVO")
    print("-" * 50)

    # Análisis de rendimiento para todas las configuraciones
    performance_default = analyze_performance(results_default)
    performance_custom = analyze_performance(results_custom)

    # Incluir análisis de torque variable si está disponible
    performance_variable = None
    if results_variable is not None:
        performance_variable = analyze_performance(results_variable)

    print("Configuración por defecto:")
    print(f"  Eficiencia básica: {performance_default['efficiency']:.4f}")
    print(f"  Estabilidad de omega: {performance_default['omega_stability']:.4f}")
    print(f"  Estabilidad de torque: {performance_default['torque_stability']:.4f}")
    print(f"  Potencia promedio: {performance_default['avg_power']:.2f} W")
    print(f"  Potencia pico: {performance_default['peak_power']:.2f} W")

    # Métricas avanzadas si están disponibles
    if 'cutting_efficiency' in performance_default:
        print(f"  Eficiencia de corte: {performance_default['cutting_efficiency']:.4f}")
        print(f"  Área cortada: {performance_default['total_area_cut']:.2f} m²")
        print(f"  Eficiencia de área: {performance_default['area_efficiency']:.4f} m²/J")
    print()

    print("Configuración personalizada:")
    print(f"  Eficiencia básica: {performance_custom['efficiency']:.4f}")
    print(f"  Estabilidad de omega: {performance_custom['omega_stability']:.4f}")
    print(f"  Estabilidad de torque: {performance_custom['torque_stability']:.4f}")
    print(f"  Potencia promedio: {performance_custom['avg_power']:.2f} W")
    print(f"  Potencia pico: {performance_custom['peak_power']:.2f} W")

    # Métricas avanzadas si están disponibles
    if 'cutting_efficiency' in performance_custom:
        print(f"  Eficiencia de corte: {performance_custom['cutting_efficiency']:.4f}")
        print(f"  Área cortada: {performance_custom['total_area_cut']:.2f} m²")
        print(f"  Eficiencia de área: {performance_custom['area_efficiency']:.4f} m²/J")
    print()

    # Análisis de configuración con torque variable
    if performance_variable is not None:
        print("Configuración con torque variable (sinusoidal):")
        print(f"  Eficiencia básica: {performance_variable['efficiency']:.4f}")
        print(f"  Estabilidad de omega: {performance_variable['omega_stability']:.4f}")
        print(f"  Estabilidad de torque: {performance_variable['torque_stability']:.4f}")
        print(f"  Potencia promedio: {performance_variable['avg_power']:.2f} W")
        print(f"  Potencia pico: {performance_variable['peak_power']:.2f} W")

        # Métricas avanzadas si están disponibles
        if 'cutting_efficiency' in performance_variable:
            print(f"  Eficiencia de corte: {performance_variable['cutting_efficiency']:.4f}")
            print(f"  Área cortada: {performance_variable['total_area_cut']:.2f} m²")
            print(f"  Eficiencia de área: {performance_variable['area_efficiency']:.4f} m²/J")
        print()

    print("7. COMPARACIÓN DE CONFIGURACIONES")
    print("-" * 50)

    # Comparar configuraciones (incluyendo torque variable si está disponible)
    configs = [
        {'mass': mass, 'radius': radius, 'omega': omega, 'T_end': 2.0, 'dt': 0.01},
        {'mass': mass, 'radius': radius, 'omega': omega, 'T_end': 2.0, 'dt': 0.01, 'advanced_params': custom_params}
    ]
    labels = ['Config_Default', 'Config_Custom']

    # Agregar configuración con torque variable si está disponible
    if results_variable is not None:
        configs.append({'mass': mass, 'radius': radius, 'omega': omega, 'T_end': 2.0, 'dt': 0.01, 'advanced_params': variable_params})
        labels.append('Config_Variable_Torque')

    comparison = compare_configurations(configs, labels)

    print("Resumen de comparación:")
    for i, label in enumerate(comparison['labels']):
        if comparison['performance'][i] is not None:
            perf = comparison['performance'][i]
            print(f"  {label}:")
            print(f"    Eficiencia básica: {perf['efficiency']:.4f}")
            print(f"    Potencia pico: {perf['peak_power']:.1f} W")
            if 'cutting_efficiency' in perf:
                print(f"    Eficiencia de corte: {perf['cutting_efficiency']:.4f}")
                print(f"    Área cortada: {perf['total_area_cut']:.2f} m²")

    print("\n" + "=" * 100)
    print("SIMULACIÓN COMPLETADA EXITOSAMENTE!")
    print("Modelo físico avanzado con EDOs funcionando correctamente")
    print("Todas las simulaciones usan el modelo realista con ecuaciones diferenciales")
    print("Personaliza 'advanced_params' para diferentes configuraciones de rotary cutter")
    print("Nuevas métricas de eficiencia y corte implementadas para análisis comparativo")
    print("Funcionalidad de torque variable temporal implementada con funciones predefinidas")
    print("Funcionalidad de torque espacial basado en densidad vegetal ρ(x)")
    print("Condiciones iniciales personalizables para arranques realistas")
    print("Sistema de validación robusto para parámetros físicos, funciones y condiciones iniciales")
