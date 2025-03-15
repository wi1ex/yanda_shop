FROM python:3.11
WORKDIR /backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app", "--access-logfile", "/dev/stdout", "--error-logfile", "/dev/stderr"]
