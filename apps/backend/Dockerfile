FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY apps/backend/ ./apps/backend/
COPY libs/ ./libs/

# 设置环境变量
ENV PYTHONPATH=/app/apps/backend:/app/libs:/app
ENV PEG_ENV=production

EXPOSE 8000

CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
