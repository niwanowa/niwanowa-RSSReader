FROM python:3.10.5-alpine3.16
WORKDIR /usr/src/app

# プロジェクトの要件をインストール
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# .env ファイルをコピー
COPY .env .

# ソースコードをコピー
COPY bot/ .

# Bot を実行
CMD ["python","-u", "main.py"]
