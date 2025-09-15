from django import forms

class UploadArquivoForm(forms.Form):
    arquivo = forms.FileField(label='Selecione um arquivo CSV ou XLSX')
