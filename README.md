# ORC - Optimización de Rotary Cutter

Sistema avanzado de simulación y optimización para rotary cutters basado en modelado físico con ecuaciones diferenciales.

## Inicio Rápido

### Opción 1: Scripts Automatizados (Recomendado)

1. **Configuración inicial** (solo la primera vez):
   ```bash
   setup_env.bat
   ```

2. **Ejecutar la aplicación**:
   ```bash
   run_app.bat
   ```

### Opción 2: Manual

1. **Crear y activar entorno virtual**:
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   # source env/bin/activate  # Linux/Mac
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar aplicación**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 📁 Estructura del Proyecto

```
orc/
├── streamlit_app.py    # Aplicación principal Streamlit
├── main_model.py       # Modelo físico y simulaciones
├── requirements.txt    # Dependencias Python
├── run_app.bat        # Script para ejecutar la app
├── setup_env.bat      # Script de configuración inicial
├── .gitignore         # Archivos ignorados por Git
└── README.md          # Este archivo
```

##  Características Principales

- **Modelo Físico Avanzado**: Simulación basada en EDOs con scipy.integrate.solve_ivp
- **Interfaz Streamlit Profesional**: Diseño moderno con esquema de colores sobrio
- **Múltiples Configuraciones de Torque**: Temporal y espacial con funciones personalizables
- **Análisis de Rendimiento**: Métricas de eficiencia energética y área de corte
- **Carga de Configuraciones**: Soporte para archivos Excel y CSV
- **Exportación de Resultados**: Descarga de datos en CSV/Excel
- **Condiciones Iniciales Flexibles**: Múltiples opciones de arranque del sistema

##  Uso

### Ejecutar la aplicación

Usa el script automatizado:
```bash
run_app.bat
```

O manualmente:
```bash
env\Scripts\activate
streamlit run streamlit_app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Interfaz de Usuario

La aplicación está organizada en 4 pestañas principales:

1. **Configuración de Torque**: Define funciones de resistencia vegetal
2. **Condiciones Iniciales**: Establece el estado inicial del sistema
3. **Simulación**: Ejecuta la simulación con parámetros configurados
4. **Resultados y Análisis**: Visualiza resultados y métricas

### Parámetros Principales

- **Masa (kg)**: Masa total del sistema rotary cutter
- **Radio (m)**: Radio principal del sistema
- **Número de Cuchillas**: Configuración de cuchillas (1-12)
- **Velocidad Angular (rad/s)**: Velocidad de referencia
- **Torque Motor (Nm)**: Torque de entrada del motor
- **Parámetros de Vegetación**: Densidad, resistencia, velocidad de avance

### Funciones de Torque Disponibles

#### Temporales
- **Sinusoidal**: Variación periódica suave
- **Escalón**: Cambio abrupto en el tiempo
- **Rampa**: Transición lineal gradual
- **Exponencial**: Crecimiento/decaimiento exponencial

#### Espaciales
- **Zonas Alternadas**: Patrones de vegetación alternados
- **Parches Gaussianos**: Concentraciones localizadas
- **Transición Sigmoide**: Cambios suaves entre zonas
- **Sinusoidal Espacial**: Variación periódica en el espacio
- **Terreno Complejo**: Combinación de múltiples patrones

## Modelo Físico

El sistema utiliza un modelo avanzado basado en ecuaciones diferenciales ordinarias (EDOs) que describe la dinámica rotacional del rotary cutter.

### Sistema de EDOs

Variables de estado:
- **θ(t)**: Posición angular del plato [rad]
- **ω(t)**: Velocidad angular del plato [rad/s]

Ecuación de movimiento:
```
I_total × dω/dt = τ_input - τ_friction - τ_drag - τ_grass
```

### Componentes del Modelo

#### Momento de Inercia Total
```
I_total = I_plate + n_blades × m_c × (R + L)²
```
- **I_plate**: Momento de inercia del plato
- **n_blades**: Número de cuchillas
- **m_c**: Masa por cuchilla
- **R**: Radio al perno
- **L**: Longitud de cuchilla

#### Torques Resistivos
- **Fricción viscosa**: τ_friction = b × ω
- **Arrastre aerodinámico**: τ_drag = c_drag × ω² × sign(ω)
- **Resistencia vegetal**: τ_grass = f(t) o τ_grass = k_grass × ρ_veg × v_avance × R

### Métricas de Rendimiento

- **Energía Total**: E_total = ∫ τ_input × ω dt
- **Energía Útil**: E_util = ∫ τ_grass × ω dt
- **Eficiencia**: η = E_util / E_total
- **Área Cortada**: A = v_avance × w × t_total

## Ejemplo de Uso Programático

```python
from main_model import run_simulation, create_default_params, create_validated_params

# Crear parámetros base del sistema
base_params = create_default_params(
    mass=15.0,           # kg - masa total
    radius=0.6,          # m - radio principal
    tau_input=200.0      # Nm - torque motor
)

# Personalizar parámetros específicos
params = create_validated_params(
    base_params,
    n_blades=4,          # número de cuchillas
    rho_veg=1.2,         # kg/m² - densidad vegetal
    v_avance=3.5         # m/s - velocidad de avance
)

# Ejecutar simulación
results = run_simulation(
    mass=15.0,
    radius=0.6,
    omega=None,
    T_end=5.0,
    dt=0.01,
    advanced_params=params
)

# Acceder a resultados
print(f"Momento de inercia: {results['moment_of_inertia']:.4f} kg⋅m²")
print(f"Velocidad final: {results['omega'][-1]:.2f} rad/s")
print(f"Eficiencia: {results['advanced_metrics']['eta']*100:.1f}%")
```

## Desarrollo y Mantenimiento

### Estructura del código

- **`streamlit_app.py`**: Interfaz de usuario completa con Streamlit
- **`main_model.py`**: Modelo físico, simulaciones y análisis
- **`requirements.txt`**: Dependencias del proyecto
- **Scripts de automatización**: `run_app.bat`, `setup_env.bat`

### Optimización

- Uso de `@st.cache_data` para evitar recálculos innecesarios
- Almacenamiento en `session_state` para persistencia de datos
- Integración numérica eficiente con `scipy.integrate.solve_ivp`
- Validación robusta de parámetros físicos

### Testing

Para probar el modelo físico:
```bash
env\Scripts\activate
python -c "from main_model import run_simulation; print('Modelo funcionando')"
```

## Características Avanzadas

- **Validación de Parámetros**: Verificación automática de coherencia física
- **Condiciones Iniciales Flexibles**: Múltiples opciones de arranque
- **Funciones de Torque Personalizables**: Temporal y espacial
- **Análisis de Métricas**: Eficiencia energética y rendimiento
- **Exportación de Datos**: CSV y Excel con múltiples hojas
- **Interfaz Profesional**: Diseño sobrio con iconos SVG personalizados

## Requisitos del Sistema

- **Python**: 3.8 o superior
- **Memoria RAM**: Mínimo 4 GB (recomendado 8 GB)
- **Espacio en disco**: 500 MB para entorno virtual
- **Navegador**: Chrome, Firefox, Edge o Safari actualizado

## Licencia

Proyecto académico para optimización de rotary cutters.

---

**ORC Project** - Sistema de Optimización de Rotary Cutter | Modelado Físico Avanzado
