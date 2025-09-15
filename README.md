# 🖥️ Análise de Desempenho Escolar com Django

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.2.6-006400)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

## 📌 Sobre o Projeto
Este projeto foi desenvolvido para processar arquivos CSV ou XLSX contendo notas de alunos, realizar análise de desempenho, gerar gráficos e relatórios PDF, tudo utilizando o framework Django. O processamento é feito inteiramente em memória, sem salvar arquivos no disco, garantindo agilidade e segurança.

---

## 🚀 Funcionalidades
- **Upload de arquivos CSV ou XLSX:** Envio de planilhas com notas dos alunos.
- **Validação dos dados:** Verifica colunas obrigatórias, valores e duplicidade.
- **Cálculo automático da média e situação:** Define se o aluno está aprovado ou reprovado.
- **Geração de gráficos dinâmicos:** Gráfico de pizza da distribuição e gráfico de barras do desempenho.
- **Relatório PDF completo:** Inclui dados, estatísticas e gráficos.
- **Download dos arquivos gerados:** PDF e gráficos disponíveis para download via botões.
- **Tabela HTML estilizada:** Exibição dos dados com formatação responsiva e alinhada.

---

## 🛠 Tecnologias Utilizadas
- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Pandas](https://pandas.pydata.org/) para manipulação de dados
- [Matplotlib](https://matplotlib.org/) para geração de gráficos
- [ReportLab](https://www.reportlab.com/) para criação de PDFs
- [Bootstrap 5](https://getbootstrap.com/) para estilização da interface

---

## ▶️ Como executar

1. Clone o repositório:
```bash
git clone https://github.com/Gabriel4002/django-upload-archives.git
cd django-upload-archives/analysis
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
Copy code
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r ../requirements.txt
```

4. Execute as migrações do banco de dados:
```bash
python manage.py migrate
```

5. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

6. Acesse no navegador:
```bash
http://127.0.0.1:8000/
```

7. Faça upload do arquivo CSV ou XLSX com as notas dos alunos e visualize os resultados. Estes arquivos podem ser encontrados em ```django-upload-archives/analysis/archives```

8. (Opcional) Você pode realizar testes automatizados utilizando `django.test.TestCase` através do comando ```python manage.py test analise```

---

📝 Observações
- O processamento dos arquivos e geração dos relatórios é feito inteiramente em memória, sem salvar arquivos no disco.
- Os arquivos gerados (PDF e gráficos) ficam armazenados na sessão do usuário para download posterior.
- A tabela HTML é estilizada com Bootstrap para melhorar a visualização.
- Logs de erros são gravados na pasta logs/ para facilitar a manutenção.

---

## ✍️ Autor

Gabriel Lobato  
[LinkedIn](https://www.linkedin.com/in/gabriel-lobato-314096371)

---

> Este projeto foi desenvolvido como parte do meu aprendizado sobre Python e Django
