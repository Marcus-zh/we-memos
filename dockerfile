FROM python:3.10

# 设置工作目录
WORKDIR /app

COPY . /root/python/

# 安装项目依赖
RUN pip install -r requirements.txt

# 设置容器启动时运行的命令
CMD ["python", "app.py"]