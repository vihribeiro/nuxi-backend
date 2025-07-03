FROM python:3.11-slim

# Cria diretório de trabalho
WORKDIR /app

# Copia tudo (inclusive nuxi_backend/)
COPY . .

# Instala dependências dentro da pasta
RUN pip install --upgrade pip && pip install -r nuxi_backend/requirements.txt

# Expõe a porta 5000
EXPOSE 5000

# Executa o Gunicorn apontando para o app dentro de src/
CMD ["gunicorn", "nuxi_backend.src.main:app", "--bind", "0.0.0.0:5000"]
