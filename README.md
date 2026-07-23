# Optimización de Fronteras Políticas mediante Algoritmos sobre Grafos (Europa 1836)

Este repositorio contiene el entorno computacional, los conjuntos de datos demográficos y los algoritmos desarrollados para resolver el problema del particionamiento territorial óptimo sobre el grafo plano dual de Europa en 1836, utilizando la función de satisfacción cultural agregada.

---

## Guía de Ejecución y Visualización

El proyecto está estructurado para permitir tanto la lectura rápida de resultados como la exploración interactiva de los grafos:

* **Proyecto_Particionamiento_Territorial.ipynb (Notebook Principal):** Es la pieza central para la revisión. Contiene la carga los resultados óptimos precalculados desde los archivos CSV y renderiza de forma estática los mapas políticos y los espectros térmicos de satisfacción. Muestra el grafo base y el mapa cultural.
* **Proyecto_Particionamiento_Territorial_Interactivo.py:** Archivo ejecutable diseñado para la interactividad. Debe ser corrido localmente para desplegar las ventanas dinámicas de Matplotlib, lo que permite interactuar con las figuras, realizar acercamientos (zoom) y explorar la red a pantalla completa.
* **main.py:** Actuó estrictamente como la mesa de trabajo e integración durante el desarrollo. No debe ser corrido, ya que contiene rutinas de depuración internas y flujos de ejecución masivos.

---

## Estructura del Directorio del Proyecto

La arquitectura del software está dividida en los siguientes componentes:

### Procesamiento de Datos y ETL
* **src/builders/**: Contiene los módulos encargados de la extracción y estructuración geométrica y demográfica de las provincias, poblaciones y metadatos de las naciones.
* **src/cleaning/**: Scripts dedicados a la depuración, poda geopolítica y curación de inconsistencias en las bases de datos originales.
* **src/parsers/**: Convertidores y procesadores de formatos de archivos para asegurar la compatibilidad con el motor de red.

### Motor de Grafos y Algoritmos
* **src/graph/**: Aloja el núcleo lógico de la aplicación. Administra la abstracción de la red utilizando la librería NetworkX, gestionando las clases de grafos geográficos y estructuras de partición.
* **src/graph/algorithms/**: Contiene las implementaciones de las cinco estrategias de optimización evaluadas:
    1. Multistart
    2. Depth-First Search - DFS
    3. Breadth-First Search - BFS
    4. Greedy Frontier Expansion
    5. Global Core Region

### Visualización y Renderizado
* **src/graph/show.py**: Módulo encargado de mapear e imprimir las estructuras de redes y colecciones de nodos utilizando Matplotlib.
* **src/imageGenerators/image_generator.py**: Código fuente dedicado a la generación y procesamiento de las matrices cromáticas para producir las salidas de mapas de bits.
* **dist/**: Repositorio de salidas del sistema. Almacena los archivos de mapa de bits (.bmp) con los mapas políticos resultantes, mapas culturales y los mapas térmicos de satisfacción cultural.
