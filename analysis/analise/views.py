import os
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from .forms import UploadArquivoForm

# Constantes para análise
COLUNAS_NOTA = ["Matematica", "Portugues", "Historia", "Geografia"]
MEDIA_APROVACAO = 6.0

def registrar_erro(mensagem):
    log_path = os.path.join(settings.LOG_DIR, 'erros.log')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")

def converter_para_df_xlsx(buffer_xlsx):
    try:
        df = pd.read_excel(buffer_xlsx)
        return df, None
    except Exception as e:
        registrar_erro(f"Erro na conversão XLSX: {str(e)}")
        return None, f"Erro na conversão XLSX: {str(e)}"

def carregar_df_csv(buffer_csv):
    try:
        df = pd.read_csv(buffer_csv)
        if df.empty:
            msg = "Arquivo CSV está vazio"
            registrar_erro(msg)
            return None, msg
        return df, None
    except Exception as e:
        msg = f"Erro ao carregar CSV: {str(e)}"
        registrar_erro(msg)
        return None, msg

def validar_dados(df):
    erros = []
    if 'Nome' not in df.columns:
        erros.append("Coluna 'Nome' ausente")
    for col in COLUNAS_NOTA:
        if col not in df.columns:
            erros.append(f"Coluna '{col}' ausente")
    if df['Nome'].isnull().any():
        erros.append("Existem alunos sem nome")
    if df['Nome'].duplicated().any():
        erros.append("Existem nomes duplicados")
    if df[COLUNAS_NOTA].lt(0).any().any():
        erros.append("Existem notas negativas")
    if erros:
        msg = " | ".join(erros)
        registrar_erro(msg)
        raise ValueError(msg)

def calcular_medias(df):
    for col in COLUNAS_NOTA:
        if not pd.api.types.is_numeric_dtype(df[col]):
            msg = f"Coluna '{col}' não é numérica"
            registrar_erro(msg)
            raise ValueError(msg)
    df['Média'] = df[COLUNAS_NOTA].mean(axis=1).round(2)
    df['Situação'] = df['Média'].apply(lambda x: 'Aprovado' if x >= MEDIA_APROVACAO else 'Reprovado')
    return df

def gerar_graficos_em_memoria(df):
    graficos = {}

    # Gráfico pizza
    plt.figure(figsize=(6,6))
    df['Situação'].value_counts().plot(
        kind='pie',
        autopct='%1.1f%%',
        colors=['#4CAF50', '#F44336'],
        title='Distribuição de Aprovação'
    )
    buf_pizza = io.BytesIO()
    plt.savefig(buf_pizza, format='png', bbox_inches='tight')
    plt.close()
    buf_pizza.seek(0)
    graficos['distribuicao.png'] = buf_pizza

    # Gráfico barras
    plt.figure(figsize=(10,6))
    df_sorted = df.sort_values('Média')
    cores = df_sorted['Situação'].map({'Aprovado': '#4CAF50', 'Reprovado': '#F44336'})
    df_sorted.plot(kind='barh', x='Nome', y='Média', color=cores, legend=False)
    plt.title('Desempenho Individual')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    buf_barras = io.BytesIO()
    plt.savefig(buf_barras, format='png', bbox_inches='tight')
    plt.close()
    buf_barras.seek(0)
    graficos['desempenho.png'] = buf_barras

    return graficos

def gerar_relatorio_pdf_em_memoria(df, graficos_buffers):
    buffer_pdf = io.BytesIO()
    c = canvas.Canvas(buffer_pdf, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "Relatório de Desempenho dos Alunos")
    c.setFont("Helvetica", 12)
    c.drawString(50, altura - 70, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Estatísticas
    total_alunos = len(df)
    aprovados = df['Situação'].value_counts().get('Aprovado', 0)
    reprovados = df['Situação'].value_counts().get('Reprovado', 0)

    c.drawString(50, altura - 100, f"Total de alunos: {total_alunos}")
    c.drawString(50, altura - 120, f"Aprovados: {aprovados}")
    c.drawString(50, altura - 140, f"Reprovados: {reprovados}")

    # Tabela simples
    y = altura - 180
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Nome")
    c.drawString(250, y, "Média")
    c.drawString(350, y, "Situação")
    c.setFont("Helvetica", 10)

    y -= 20
    for _, row in df.iterrows():
        c.drawString(50, y, str(row['Nome']))
        c.drawString(250, y, f"{row['Média']:.2f}")
        c.drawString(350, y, row['Situação'])
        y -= 15
        if y < 50:
            c.showPage()
            y = altura - 50

    # Página dos gráficos
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 50, "Gráficos de Análise")

    y_pos = altura - 100
    for nome_grafico in ['distribuicao.png', 'desempenho.png']:
        if nome_grafico in graficos_buffers:
            img = ImageReader(graficos_buffers[nome_grafico])
            img_width, img_height = img.getSize()
            max_width = 500
            max_height = 350
            scale = min(max_width / img_width, max_height / img_height)
            new_width = img_width * scale
            new_height = img_height * scale
            x_pos = (largura - new_width) / 2
            c.drawImage(img, x_pos, y_pos - new_height, width=new_width, height=new_height)
            y_pos -= new_height + 30
            if y_pos < 100:
                c.showPage()
                y_pos = altura - 100

    c.save()
    buffer_pdf.seek(0)
    return buffer_pdf

def upload_arquivo(request):
    if request.method == 'POST':
        form = UploadArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.cleaned_data['arquivo']
            nome_arquivo = arquivo.name
            extensao = os.path.splitext(nome_arquivo)[1].lower()

            try:
                if extensao == '.xlsx':
                    buffer_xlsx = io.BytesIO(arquivo.read())
                    df, erro = converter_para_df_xlsx(buffer_xlsx)
                    if erro:
                        return render(request, 'analise/upload.html', {'form': form, 'erro': erro})
                elif extensao == '.csv':
                    buffer_csv = io.StringIO(arquivo.read().decode('utf-8'))
                    df, erro = carregar_df_csv(buffer_csv)
                    if erro:
                        return render(request, 'analise/upload.html', {'form': form, 'erro': erro})
                else:
                    return render(request, 'analise/upload.html', {'form': form, 'erro': 'Formato não suportado. Use CSV ou XLSX.'})

                validar_dados(df)
                df = calcular_medias(df)
                graficos = gerar_graficos_em_memoria(df)
                pdf_buffer = gerar_relatorio_pdf_em_memoria(df, graficos)

                # Armazenar arquivos na sessão para download
                request.session['pdf_bytes'] = base64.b64encode(pdf_buffer.getvalue()).decode('ascii')
                request.session['grafico_pizza'] = base64.b64encode(graficos['distribuicao.png'].getvalue()).decode('ascii')
                request.session['grafico_barras'] = base64.b64encode(graficos['desempenho.png'].getvalue()).decode('ascii')

                contexto = {
                    'tabela_html': df.to_html(classes='table table-hover table-bordered', index=False),
                }
                return render(request, 'analise/resultado.html', contexto)

            except ValueError as e:
                return render(request, 'analise/upload.html', {'form': form, 'erro': str(e)})
            except Exception as e:
                registrar_erro(f"Erro inesperado: {str(e)}")
                return render(request, 'analise/upload.html', {'form': form, 'erro': f"Erro inesperado: {str(e)}"})

        else:
            return render(request, 'analise/upload.html', {'form': form})

    else:
        form = UploadArquivoForm()
        return render(request, 'analise/upload.html', {'form': form})

# Views para download dos arquivos gerados

def download_pdf(request):
    pdf_b64 = request.session.get('pdf_bytes')
    if not pdf_b64:
        return HttpResponse("PDF não disponível", status=404)
    pdf_bytes = base64.b64decode(pdf_b64)
    buffer = io.BytesIO(pdf_bytes)
    return FileResponse(buffer, as_attachment=True, filename='relatorio_alunos.pdf')

def download_grafico_pizza(request):
    img_b64 = request.session.get('grafico_pizza')
    if not img_b64:
        return HttpResponse("Imagem não disponível", status=404)
    img_bytes = base64.b64decode(img_b64)
    buffer = io.BytesIO(img_bytes)
    return FileResponse(buffer, as_attachment=True, filename='distribuicao.png')

def download_grafico_barras(request):
    img_b64 = request.session.get('grafico_barras')
    if not img_b64:
        return HttpResponse("Imagem não disponível", status=404)
    img_bytes = base64.b64decode(img_b64)
    buffer = io.BytesIO(img_bytes)
    return FileResponse(buffer, as_attachment=True, filename='desempenho.png')

