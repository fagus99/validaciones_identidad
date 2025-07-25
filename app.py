import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import os
import re
import tempfile

st.title("📄 Extractor de Datos de Validación de Identidad")

carpeta_zip = st.file_uploader("Subí una carpeta ZIP con los PDFs", type=["zip"])

if carpeta_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Guardar y extraer ZIP
        zip_path = os.path.join(tmpdir, "archivos.zip")
        with open(zip_path, "wb") as f:
            f.write(carpeta_zip.read())
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        resultados = []

        for archivo in os.listdir(tmpdir):
            if archivo.endswith(".pdf"):
                path_pdf = os.path.join(tmpdir, archivo)
                try:
                    texto = ""
                    with fitz.open(path_pdf) as doc:
                        for pagina in doc:
                            texto += pagina.get_text()

                    nombre_match = re.search(r"First Name\s+(.+)", texto)
                    apellido_match = re.search(r"Surname\s+(.+)", texto)
                    dni_match = re.search(r"Document\s+Number\s+([\d\.]+)", texto)

                    nombre = nombre_match.group(1).strip() if nombre_match else ""
                    apellido = apellido_match.group(1).strip() if apellido_match else ""
                    dni = dni_match.group(1).replace(".", "") if dni_match else ""

                    resultados.append({
                        "Archivo": archivo,
                        "Nombre": nombre,
                        "Apellido": apellido,
                        "DNI": dni
                    })
                except Exception as e:
                    st.warning(f"❌ Error procesando {archivo}: {e}")

        if resultados:
            df = pd.DataFrame(resultados)
            st.dataframe(df)

            excel_output = os.path.join(tmpdir, "datos_extraidos.xlsx")
            df.to_excel(excel_output, index=False)
            with open(excel_output, "rb") as f:
                st.download_button("📥 Descargar Excel", f, file_name="datos_extraidos.xlsx")
        else:
            st.info("No se extrajeron datos válidos.")
