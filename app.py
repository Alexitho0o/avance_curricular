import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Evaluación Clase Simulada Online", layout="wide")

# Encabezado con logo
st.markdown(f"""
<div style='display: flex; align-items: center;'>
    <img src="https://ipciisa-my.sharepoint.com/:i:/g/personal/alexi_burgos_ipss_cl/EbwpXxqucFlApf8IEv5Kni8B5G_c9igGAjEvQuxuovnvHA?e=SyPPNB" style='height: 100px; margin-right: 20px;'>
    <h1>Evaluación de Clase Simulada Online</h1>
</div>
""", unsafe_allow_html=True)

# Formulario de antecedentes
st.header("Antecedentes del Candidato y Evaluador")
with st.form("datos"):
    col1, col2, col3 = st.columns(3)
    candidato = col1.text_input("Nombre del Candidato")
    rut = col2.text_input("RUT del Candidato")
    nombre_eval = col3.text_input("Nombre del Evaluador")
    col4, col5, col6 = st.columns(3)
    cargo = col4.text_input("Cargo del Evaluador")
    area = col5.text_input("Área/Facultad")
    semestre = col6.text_input("Semestre", value="2024-1")
    col7, col8, col9 = st.columns(3)
    carrera = col7.text_input("Nombre de la Carrera")
    cod_carrera = col8.text_input("Código de la Carrera")
    asignatura = col9.text_input("Nombre de Asignatura")
    col10, col11, col12 = st.columns(3)
    cod_asignatura = col10.text_input("Código de Asignatura")
    fecha = col11.date_input("Fecha", value=datetime.today())
    hora = col12.time_input("Hora", value=datetime.strptime("18:30", "%H:%M").time())
    st.form_submit_button("Guardar Datos")

# Escala de evaluación
descriptores = {
    7: "SOBRE LO ESPERADO",
    5: "ESPERADO",
    3: "BAJO LO ESPERADO",
    1: "NO CUMPLE"
}

estructura = [
    ("Inicio", "Contextualiza la clase, vincula con aprendizajes previos y capta atención.", [
        ("Contextualización", 5),
        ("Activación", 5),
        ("Motivación", 5)
    ]),
    ("Desarrollo", "Desarrolla contenidos con metodologías activas, rol facilitador y buen clima.", [
        ("Coherencia", 10),
        ("Metodología", 15),
        ("Rol docente", 15),
        ("Clima de aula", 10),
        ("Relación interpersonal", 10),
        ("Recursos de Apoyo", 5)
    ]),
    ("Cierre", "Concluye la clase con claridad y evalúa logros.", [
        ("Cierre", 5),
        ("Evaluación formativa", 5)
    ]),
    ("Dominio disciplinar", "Demuestra dominio del contenido.", [
        ("Disciplinar", 10)
    ])
]

# Evaluación
total = 0
puntajes = []
comentarios = []
comentarios_dim = []

st.header("Evaluación por Dimensión")
with st.form("evaluacion"):
    for dim, descripcion, subdims in estructura:
        st.markdown(f"### {dim}")
        st.info(descripcion)
        for subdim, pond in subdims:
            st.subheader(f"{subdim} ({pond}%)")
            puntos = st.radio(f"Nivel alcanzado en {subdim}", [7, 5, 3, 1], format_func=lambda x: descriptores[x], key=subdim)
            comentario = st.text_area(f"Comentario para {subdim}", key="coment_" + subdim)
            puntajes.append((dim, subdim, puntos, pond))
            comentarios.append(comentario)
        comentario_dim = st.text_area(f"Comentario general para la dimensión {dim}", key="coment_global_" + dim)
        comentarios_dim.append(comentario_dim)

    submit_eval = st.form_submit_button("Generar Informe Final")

if submit_eval:
    filas = []
    for (dim, subdim, puntos, pond), comentario in zip(puntajes, comentarios):
        ponderado = puntos * (pond / 100)
        total += ponderado
        filas.append({
            "Dimensión": dim,
            "Subdimensión": subdim,
            "Puntaje": puntos,
            "Ponderación (%)": pond,
            "% Logro Ponderado": round(ponderado, 2),
            "Comentario": comentario
        })

    resultado = "INSATISFACTORIO"
    if total >= 85:
        resultado = "DESTACADO"
    elif total >= 70:
        resultado = "SATISFACTORIO"
    elif total >= 60:
        resultado = "BÁSICO"

    df = pd.DataFrame(filas)
    df.loc[len(df.index)] = ["", "TOTAL", "", "", "", ""]
    df.loc[len(df.index)] = ["", "RESULTADO", "", "", round(total, 2), resultado]

    st.success("✅ Evaluación completada")
    st.write(f"**Resultado Final:** `{resultado}` ({round(total, 2)}%)")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Informe en CSV", data=csv, file_name="evaluacion_clase_simulada.csv", mime='text/csv')

    st.markdown("---")
    st.header("Comentarios Generales por Dimensión")
    for (dim, _, _), comentario in zip(estructura, comentarios_dim):
        st.subheader(f"{dim}")
        st.write(comentario if comentario else "_Sin comentario_")
