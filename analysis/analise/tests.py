from django.test import TestCase, Client
from django.urls import reverse
import io

class AnaliseTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_pagina_upload_get(self):
        response = self.client.get(reverse('upload_arquivo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload de arquivo")

    def test_upload_csv_valido(self):
        csv_content = "Nome,Matematica,Portugues,Historia,Geografia\nAluno1,7,8,6,7\nAluno2,5,4,6,5"
        arquivo = io.BytesIO(csv_content.encode('utf-8'))
        arquivo.name = 'teste.csv'
        response = self.client.post(reverse('upload_arquivo'), {'arquivo': arquivo})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resultado da Análise")
        self.assertContains(response, "Aluno1")
        self.assertContains(response, "Aprovado")

    def test_upload_arquivo_invalido(self):
        arquivo = io.BytesIO(b"conteudo invalido")
        arquivo.name = 'teste.txt'
        response = self.client.post(reverse('upload_arquivo'), {'arquivo': arquivo})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formato não suportado")
