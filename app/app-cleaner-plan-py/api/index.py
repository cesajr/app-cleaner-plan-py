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
            # ... (restante do seu processamento)
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
