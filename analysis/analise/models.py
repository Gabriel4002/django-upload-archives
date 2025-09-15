from django.db import models

class UploadArquivo(models.Model):
    arquivo = models.FileField(upload_to='uploads/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.arquivo.name
