FROM python:3.10

WORKDIR /app

# プロジェクトの要件をインストール
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# .env ファイルをコピー
COPY .env .

# ソースコードをコピー
COPY src/ .

# Bot を実行
CMD ["python", "bot.py"]
