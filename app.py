import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import zipfile
import io
import re
import os

st.title("📄 Extracción de datos de PDFs (Nombre, Apellido, DNI)")

uploaded_zip = st.file_uploader("Subí una carpeta comprimida (.zip) con los archivos PDF", type="zip")

if uploaded_zip:
    with zipfile.ZipFile(uploaded_zip) as z:
        extracted_pdfs = [f for f in z.namelist() if f.lower().endswith('.pdf')]
        
        resultados = []

        for pdf_name in extracted_pdfs:
            with z.open(pdf_name) as file:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                texto = ""
                for page in doc:
                    texto += page.get_text()
                doc.close()

                # Búsqueda de DNI o Documento
                dni_match = re.search(r"(DNI|Documento|Document Number)\D+(\d{7,10})", texto, re.IGNORECASE)
                dni = dni_match.group(2) if dni_match else ""

                # Búsqueda de Nombre y Apellido (muy variable, usamos heurísticas)
                nombre = ""
                apellido = ""
                name_match = re.search(r"(Nombre|Name)\D+([A-ZÁÉÍÓÚÑa-záéíóúñ ]{2,})", texto)
                surname_match = re.search(r"(Apellido|Surname)\D+([A-ZÁÉÍÓÚÑa-záéíóúñ ]{2,})", texto)

                if name_match:
                    nombre = name_match.group(2).strip()
                if surname_match:
                    apellido = surname_match.group(2).strip()

                resultados.append({
                    "Archivo": os.path.basename(pdf_name),
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "DNI": dni
                })

        df_resultados = pd.DataFrame(resultados)
        st.dataframe(df_resultados)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_resultados.to_excel(writer, index=False, sheet_name='Datos')

        st.download_button(
            label="📥 Descargar Excel",
            data=output.getvalue(),
            file_name="resultados_dni.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
