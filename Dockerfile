FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

# ENV GOOGLE_API_KEY='AIzaSyCwlEtt1TzTIN1f6bMWRk80s1Laq2i0MtE'
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/keyfile.json"
EXPOSE 8000

CMD ["uvicorn", "rag:app", "--port", "9988"]