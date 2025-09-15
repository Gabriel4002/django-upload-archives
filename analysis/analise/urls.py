from django.urls import path
from .views import upload_arquivo, download_pdf, download_grafico_pizza, download_grafico_barras
urlpatterns = [
    path('', upload_arquivo, name='upload_arquivo'),
    path('download/pdf/', download_pdf, name='download_pdf'),
    path('download/grafico_pizza/', download_grafico_pizza, name='download_grafico_pizza'),
    path('download/grafico_barras/', download_grafico_barras, name='download_grafico_barras'),
]