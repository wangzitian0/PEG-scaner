FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY apps/backend/ .

# 设置环境变量
ENV FLASK_APP=src/pegserver
ENV PYTHONPATH=/app/src:/app/proto/generated

EXPOSE 8000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]

