from flask import Flask, request, send_file, render_template_string
import pandas as pd
import io

app = Flask(__name__)

HTML_FORM = '''
<!doctype html>
<title>Separador de Coordenadas</title>
<h1>Upload de Planilha Excel (.xlsx)</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Processar>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, sheet_name=0)
            # Identificação automática da coluna de coordenadas
            colunas_normalizadas = {col.lower().strip(): col for col in df.columns}
            possiveis_nomes = ['coordenadas', 'coord', 'coordenadas gps']
            col_coordenadas = None
            for nome in possiveis_nomes:
                if nome in colunas_normalizadas:
                    col_coordenadas = colunas_normalizadas[nome]
                    break
            if col_coordenadas is None:
                return "Coluna de coordenadas não encontrada!"
            # Limpeza e separação
            df[col_coordenadas] = df[col_coordenadas].astype(str).str.strip().str.replace('\n', '', regex=True)
            df[['latitude', 'longitude']] = df[col_coordenadas].str.split('|', expand=True)
            df['latitude'] = df['latitude'].str.strip().str.replace(',', '.')
            df['longitude'] = df['longitude'].str.strip().str.replace(',', '.')
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df.drop(columns=[col_coordenadas], inplace=True)
            # Salvar para download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return send_file(
                output,
                as_attachment=True,
                download_name="planilha_corrigida.xlsx",
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return "Por favor, envie um arquivo .xlsx"
    return render_template_string(HTML_FORM)
