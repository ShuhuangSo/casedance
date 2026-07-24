# 锁定 Python 3.8.10
FROM python:3.8.10-slim

# 设置工作目录
WORKDIR /app

# Debian Buster 已 EOL，将 apt 源指向归档仓库
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装依赖
# 注意：确保你的项目根目录下有 requirements.txt 文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 保持容器运行
CMD ["sleep", "infinity"]