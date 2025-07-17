import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pygwalker as pyg
import streamlit.components.v1 as components
from io import BytesIO

st.set_page_config(page_title = "Dashboard Licencias médicas", layout="wide")

st.title("Dashboard Interactivo: Análisis de licencias médicas")

## Carga del dataset

@st.cache_data
def cargar_datos(archivo):
    return pd.read_excel(archivo)

df = cargar_datos("dataframe.xlsx")
st.write("Vista previa del dataframe")
st.dataframe(df.head())

st.write(df.shape)

## Sidebar : filtros interactivos

st.sidebar.header("Filtros del panel")

caltrab = st.sidebar.multiselect("Calidad trabajador", df["CalidadTrabajador"].unique(), default =df["CalidadTrabajador"].unique())

sexo = st.sidebar.multiselect("Sexo", df["SexoTrabajador"].unique(), default = df["SexoTrabajador"].unique())

dias = st.sidebar.slider("Numero Días", int(df["NumeroDias"].min()), int(df["NumeroDias"].max()), (12,30))

solo_autorizados = st.sidebar.checkbox("Licencias autorizadas")

# Aplicar filtros

df_filtrado = df[(df["CalidadTrabajador"].isin(caltrab))&(df["SexoTrabajador"].isin(sexo))&(df["NumeroDias"].between(dias[0], dias[1]))]

st.write(df_filtrado.shape)

with st.expander("¿Qué hace selectbox"):
    """"
    st.selectbox
    Permite al usuario seleccionar una opción de un menú desplegable.
    Aquí se utiliza como menú de navegación para separar secciones de la app en vistas exclusivas:
    -"Análisis General": KPIs, visualizaciones con Seaborn y Plotly.
    -"Exploración con PyGWalker": vista interactiva automática y carga desde JSON.
    """

menu = st.selectbox("Selecciona una sección", ["Análisis General", "Exploración PyGWalker"])

if menu == "Análisis General":
    # Acá va la sección general
    #
    #
    st.write("Análisis General")
    
    col1, col2, col3 = st.columns(3)
    
    total = len(df_filtrado)
    solo_autorizados = (df_filtrado["TipoResolucion"] == "Autoricese").sum()
    porc = round((solo_autorizados/ total)*100,2) if total > 0 else 0
    
    col1.metric("Total datos", total)
    col2.metric("Licencias autorizadas",solo_autorizados)
    col3.metric("Tasa autorizadas",f"{porc}%")
    
    st.subheader("Licencias emitidas por trimestre (plotly)")
    
    # Count licenses by issue date
    conteo_por_fecha = df_filtrado['FechaEmisionLicencia'].value_counts().sort_index()

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bars
    bars = ax.bar(conteo_por_fecha.index.astype(str), conteo_por_fecha.values, 
             color='#4CAF50', edgecolor='darkgreen')

    # Customize plot
    ax.set_title('Cantidad de Licencias Emitidas por Trimestre', fontsize=16, pad=20)
    ax.set_xlabel('Trimestre de Emisión', fontsize=12)
    ax.set_ylabel('Número de Licencias Emitidas', fontsize=12)

    # Rotate x-axis labels - more reliable method
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Add value labels
    ax.bar_label(bars,
            labels=[f"{x:,.0f}" for x in conteo_por_fecha.values],
            padding=3,
            fontsize=10,
            color='black')

    # Adjust layout and display
    plt.tight_layout()
    st.pyplot(fig)
    
    st.subheader("Licencias por tipo de resolución (plotly)")
    
    conteo_por_resolucion = df_filtrado['TipoResolucion'].value_counts().sort_index()

    # 2. Create figure with object-oriented approach
    fig2, ax = plt.subplots(figsize=(12, 6))

    # Create bars with improved formatting
    bars = ax.bar(
    conteo_por_resolucion.index.astype(str),  # X-axis: resolution types
    conteo_por_resolucion.values,             # Y-axis: counts
    color='#4CAF50',
    edgecolor='darkgreen',
    width=0.7)

    # 3. Customize plot with proper axis methods
    ax.set_title('Cantidad de Licencias "Autorizadas" por Tipo de Resolución', fontsize=16, pad=20)
    ax.set_xlabel('Tipo de Resolución', fontsize=12)
    ax.set_ylabel('Número de Licencias Autorizadas', fontsize=12)
    # Rotate x-axis labels properly
    ax.set_xticks(range(len(conteo_por_resolucion)))
    ax.set_xticklabels(conteo_por_resolucion.index.astype(str), rotation=45, ha='right')

    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # 4. Add value labels with proper formatting
    ax.bar_label(
    bars,
    labels=[f"{x:,}" for x in conteo_por_resolucion.values],
    padding=3,
    fontsize=10,
    color='black')

    # 5. Force integer ticks on Y-axis
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Adjust layout and display in Streamlit
    plt.tight_layout()
    st.pyplot(fig2)
    
    
    st.subheader("Licencias por sexo (Seaborn)")
    
    fig3, ax = plt.subplots(figsize=(15, 7))

    # Filtrar y preparar datos
    df_genero = df_filtrado[df_filtrado['SexoTrabajador'].isin(['Femenino', 'Masculino'])]
    conteo_genero = df_genero['SexoTrabajador'].value_counts()
    total = conteo_genero.sum()

    # Calcular porcentajes (con protección contra división por cero)
    porcentaje_femenino = 100 * conteo_genero.get('Femenino', 0) / total if total > 0 else 0
    porcentaje_masculino = 100 * conteo_genero.get('Masculino', 0) / total if total > 0 else 0

    # Crear gráfico
    gender_plot = sns.countplot(
    data=df_genero,
    x='SexoTrabajador',
    order=['Femenino', 'Masculino'],
    palette=['#FF9AA2', '#A0E7E5'],
    ax=ax)

    # Título con ambos porcentajes
    ax.set_title(
    f'Distribución de Licencias por Género\n'
    f'Femenino: {porcentaje_femenino:.1f}% | Masculino: {porcentaje_masculino:.1f}%',
    fontsize=16,
    pad=20)

    # Ejes y estilo
    ax.set_xlabel('Género', fontsize=12, labelpad=10)
    ax.set_ylabel('Número de Licencias', fontsize=12, labelpad=10)
    sns.despine(ax=ax, offset=10, trim=True)
    ax.grid(axis='y', linestyle=':', alpha=0.4)

    # Etiquetas con valores absolutos (arriba) y porcentajes (centro)
    for p in gender_plot.patches:
    # Valor absoluto
        ax.annotate(
        f'{p.get_height():,}',
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', 
        va='bottom',
        xytext=(0, 5),
        textcoords='offset points',
        fontsize=12,
        weight='bold'
    )
    
    # Porcentaje
    porcentaje = 100 * p.get_height() / total if total > 0 else 0
    ax.text(
        p.get_x() + p.get_width() / 2.,
        p.get_height() / 2,
        f'{porcentaje:.1f}%',
        ha='center',
        va='center',
        color='black',
        fontsize=14,
        weight='bold',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2')
    )

    # Ajustar y mostrar
    plt.tight_layout()
    st.pyplot(fig3)
    
    st.subheader("Licencias por grupo etario (Seaborn)")
    
    # Cantidad de licencias por Grupo Etario

    fig4 = plt.figure(figsize=(14, 7))  # Tamaño más grande para mejor visualización

    # Ordenamos los grupos etarios correctamente
    order_edad = sorted(df_filtrado['EdadTrabajador'].unique(),
                   key=lambda x: int(x.split('-')[0]) if '-' in x else 0)

    # Creamos el gráfico y guardamos el objeto ax
    ax = sns.countplot(data=df_filtrado,
                  x='EdadTrabajador',
                  order=order_edad,
                  palette='viridis')  # Paleta de colores adecuada para variables ordinales

    plt.title('Cantidad de licencias por grupo etario', fontsize=16, pad=20)
    plt.xlabel('Grupo etario', fontsize=12)
    plt.ylabel('Número de licencias', fontsize=12)
    plt.xticks(rotation=45, ha='right')  # Mejor alineación de las etiquetas

    # Añadimos las etiquetas de valor en las barras
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height()):,}',  # Formato con separador de miles
               (p.get_x() + p.get_width() / 2., p.get_height()),
               ha='center',
               va='center',
               xytext=(0, 10),
               textcoords='offset points',
               fontsize=11,
               fontweight='bold')

    # Mejoramos el estilo
    sns.despine()
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))  # Formato en eje Y
    plt.tight_layout()
    st.pyplot(fig4)
    
    
    
    
    
    tab1, tab2, tab3 = st.tabs( ["Tabla", "Gráficos", "Estadísticas"])
    
    with tab1:
        #escribir código
        st.dataframe(df_filtrado)
        
    with tab2:
        fig3 = px.violin(df_filtrado, x="SexoTrabajador", y = "NumeroDias", color = "TipoResolucion", box = True, points = 'all')
        st.plotly_chart(fig3, use_container_width= True)
        
    with tab3:
        st.write("Estadísticas descriptivas")
        st.dataframe(df_filtrado.describe())
        


else:
    
    # Hacemos lo de PyGWalker
    #
    #
    st.header("Análisis PyGWalker")
    
    tab_pyg1, tab_pyg2 = st.tabs(["PyGWalker dinámico", "Cargar JSON de PyGWalker"])
    
    with tab_pyg1:
        pyg_html =pyg.to_html(df, return_html = True, dark = 'light')
        st.subheader("Exploración dinámica con PyGWalker")
        components.html(pyg_html, height = 800, scrolling = True)
        ##
    with tab_pyg2:
        st.subheader("Subir archivo JSON de PyGWalker")
        archivo = st.file_uploader("Selecciona un archivo JSON", type="json")
        
        if archivo is not None:
            
            try:
                
                json_content = archivo.read().decode("utf-8")
                html_json = pyg.to_html(df, return_html = True, dark = 'light', spec = json_content)
                st.subheader("Carga gráfica a PyGWalker desde json")
                components.html(html_json,  height = 800, scrolling = True)
            except Exception as e:
                st.error(f"Error al cargar el archivo : {e}")
    
