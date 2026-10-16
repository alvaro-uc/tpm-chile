# ¿Podemos anticipar al Banco Central?

Proyecto semestral de IMT 2210 — Introducción a la Ciencia de Datos.

## Resumen

Este proyecto estudia hasta qué punto los indicadores macroeconómicos públicos permiten anticipar la dirección de la próxima decisión de Tasa de Política Monetaria (TPM) del Banco Central de Chile: **sube, se mantiene o baja**.

Construiremos un conjunto de datos reproducible para 2010–2025, integrando series oficiales del Banco Central de Chile, Cochilco y el Instituto Nacional de Estadísticas (INE): TPM, IPC/inflación, IMACEC, desempleo, USD/CLP y precio del cobre. También evaluaremos si las Expectativas Económicas (EEE) agregan información, según disponibilidad y alcance del curso.

El estudio incluirá preparación documentada, análisis exploratorio, una regla base y uno o dos clasificadores introductorios (regresión logística y, opcionalmente, árbol de decisión). La evaluación respetará el orden temporal. El objetivo es medir la señal predictiva, no construir un sistema de inversión ni afirmar causalidad.

**Pregunta principal:** ¿Hasta qué punto los indicadores macroeconómicos públicos permiten anticipar si la próxima decisión de TPM será subir, mantener o bajar?

## Estructura del repositorio

```text
proyecto-cd/
├── data/
│   ├── raw/                  # Excel originales versionados
│   │   ├── clp_usd.xlsx
│   │   ├── cu_usd_lb.xlsx
│   │   ├── desempleo_total_mensual.xlsx
│   │   ├── exp_tpm_mensual_mediana.xlsx
│   │   ├── imacec_empalmado_original.xlsx
│   │   ├── ipc_general_anual.xlsx
│   │   ├── ipc_general_mensual.xlsx
│   │   └── tpm_bcentral_diaria.xlsx
│   └── processed/            # Datos integrados y transformados
├── docs/                     # Diccionario, fuentes y decisiones metodológicas
├── notebooks/                # Exploración y notebook final
├── src/
│   ├── ingest/               # Lectura de archivos fuente locales
│   ├── processing/           # Limpieza, integración, rezagos y etiqueta objetivo
│   └── visualization/        # Funciones reutilizables para gráficos
├── .gitignore
├── requirements.txt
└── README.md
```

- `data/raw/`: conserva las descargas originales; no se sobrescriben con versiones limpias.
- `data/processed/`: contiene tablas derivadas que se pueden regenerar mediante código.
- `src/`: contiene lógica reutilizable para ingesta, procesamiento y visualización.
- `notebooks/`: aloja análisis numerados, como `01_revision_fuentes.ipynb`, `02_eda.ipynb` y `99_estudio_final.ipynb`.
- `docs/`: registra definiciones, unidades, frecuencias, fuentes, fechas de consulta/publicación, decisiones de transformación y la retroalimentación del profesor.

Los archivos Excel de `data/raw/` son las fuentes originales que usará el equipo y se versionan para que todos trabajen con las mismas copias. La lista de series, períodos y advertencias está en `docs/README.md`. Los demás archivos de datos siguen ignorados por defecto. No subas credenciales ni información con restricciones de uso.

El historial de reuniones se guarda **aparte** en
`data/processed/reuniones_tpm_2010_2025.csv`: 161 decisiones, con fecha de
anuncio, corte al cierre del día hábil anterior y etiqueta `sube/mantiene/baja`.
Se regenera localmente con `python -m src.processing.reuniones_tpm`, a partir
del Excel original y las fuentes `rpm_*.json` conservadas en `data/raw/reuniones_tpm/`.
Las fuentes, la recopilación web puntual autorizada, la corrección de una
fecha y los límites de esta primera versión están en
[`docs/reuniones_tpm.md`](docs/reuniones_tpm.md).
El notebook [`02_reuniones_tpm.ipynb`](notebooks/02_reuniones_tpm.ipynb)
explica y ejecuta ese proceso paso a paso desde un kernel limpio.

**Fuente elegida para el cobre: Cochilco, precio spot BML/LME, para todo 2010–2025.**
Las descargas originales y su procedencia están en `data/raw/cobre_historico/`.
La tabla para análisis es `data/processed/cobre_cochilco_diario_2010_2025.csv`,
en dólares por libra, con fechas ISO y trazabilidad por fila. Se regenera sin
conexión con `python -m src.processing.cobre_cochilco`. El notebook
[`03_cobre_historico.ipynb`](notebooks/03_cobre_historico.ipynb) explica y ejecuta
la recuperación, comparación y construcción de la serie completa.
El Excel del BCCh queda como referencia; no se mezclan sus precios con Cochilco.
Ver la decisión y sus controles en [`docs/cobre_historico.md`](docs/cobre_historico.md).

## Requisitos previos

- Git.
- Python 3.10 o superior.
- Acceso al repositorio de GitHub.

## Instalación

### 1. Clonar el repositorio

Reemplacen la URL de ejemplo por la URL real compartida en GitHub:

```bash
git clone https://github.com/ORGANIZACION/REPOSITORIO.git
cd REPOSITORIO
```

### 2. Crear y activar el entorno virtual

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Cada integrante crea su propio `.venv`; no se versiona ni se comparte. Para salir del entorno: `deactivate`.

### 4. Iniciar Jupyter

```bash
jupyter notebook
```

## Flujo de análisis previsto

1. **Obtención y preparación:** trabajar desde los archivos fuente versionados en `data/raw/`, sin APIs ni descargas automáticas; revisar fechas, unidades, frecuencia y valores faltantes; integrar series y documentar transformaciones.
2. **Análisis exploratorio:** estudiar la evolución de TPM e inflación, IMACEC y desempleo, dólar y cobre; revisar distribución de decisiones y correlaciones. Los episodios económicos sirven como contexto, no como evidencia causal.
3. **Variable objetivo:** etiquetar cada decisión como sube, se mantiene o baja mediante una regla explícita acordada por el equipo.
4. **Modelamiento:** construir primero un baseline (por ejemplo, predecir siempre la clase más frecuente) y compararlo con regresión logística y, si corresponde al curso, un árbol de decisión.
5. **Evaluación:** usar una separación cronológica entrenamiento/prueba e interpretar métricas, errores y limitaciones. Explorar si EEE aporta información adicional.

**Cuidado metodológico clave:** para cada decisión, los predictores deben representar información disponible antes de esa decisión. Registrar fechas de publicación y considerar rezagos o revisiones para evitar usar información futura. Una partición aleatoria no sustituye la evaluación cronológica.

## Trabajo colaborativo con GitHub

1. Actualiza tu rama principal antes de comenzar:

   ```bash
   git switch main
   git pull origin main
   ```

2. Crea una rama descriptiva para tu tarea:

   ```bash
   git switch -c feature/documentar-fuentes
   ```

3. Haz cambios acotados y coordinen quién edita cada notebook para evitar conflictos.
4. Revisa antes del commit con `git status` y `git diff`.
5. Usa commits pequeños y mensajes claros:

   ```bash
   git add README.md docs/ src/
   git commit -m "docs: registrar fuentes macroeconómicas"
   git push -u origin feature/documentar-fuentes
   ```

6. Abre un Pull Request hacia `main`, describe el cambio y pide revisión de otro integrante antes de integrarlo.

### Buenas prácticas

- No subas bases de datos, entornos virtuales, credenciales ni configuración personal.
- No trabajes directamente sobre `main`; usa ramas y Pull Requests.
- Mantén los datos originales separados de los procesados.
- Usa rutas relativas y evita que el notebook dependa de variables de una sesión anterior.
- Limpia salidas innecesariamente grandes de notebooks.
- Si cambian dependencias, actualiza `requirements.txt` y explica el motivo.
- Antes de entregar, ejecuta el notebook maestro completo desde un kernel limpio.

## Criterio de éxito

El éxito no depende de predecir perfectamente al Banco Central. Un resultado similar al baseline también es informativo si la evaluación es correcta y se interpretan sus límites. El estudio debe cuantificar cuánta señal aportan los indicadores y si las expectativas agregan información.

## Fuente de la propuesta

El tema, período, variables candidatas y diseño descritos aquí se basan en `Propuesta proyecto IMT210.pdf`, propuesta semestral de IMT 2210. El uso de expectativas y el modelo alternativo son tentativos y se confirmarán según los datos disponibles y el curso.
