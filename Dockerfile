FROM ghcr.io/a224327780/python

WORKDIR /data/python

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]