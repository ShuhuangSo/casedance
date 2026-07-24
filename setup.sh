#!/bin/bash
# ============================================
# Casedance 一键部署脚本
# 用法：
#   新服务器：curl ... | bash  或  chmod +x setup.sh && ./setup.sh
#   已有项目：./setup.sh
# ============================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
step()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[X]${NC} $1"; exit 1; }

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_BACKUP_FILE="$PROJECT_DIR/casedance_backup.sql"

# ========== 1. 安装 Docker ==========
step "检查 Docker..."
if ! command -v docker &>/dev/null; then
    step "安装 Docker..."
    curl -fsSL https://get.docker.com | sh
fi
if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null; then
    step "安装 docker-compose..."
    apt install docker-compose -y 2>/dev/null || true
fi
step "Docker 就绪: $(docker --version)"

# ========== 2. 初始化 .env ==========
step "检查 .env 环境配置..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        warn "已从 .env.example 创建 .env，请编辑填入真实值后重新运行:"
        warn "  vim $PROJECT_DIR/.env"
        exit 0
    else
        error "未找到 .env.example"
    fi
fi
step ".env 已就绪"

cd "$PROJECT_DIR"

# ========== 3. 拉取代码（如果已有 git） ==========
if [ -d .git ]; then
    step "拉取最新代码..."
    git pull origin master 2>/dev/null || warn "git pull 失败，使用当前代码继续"
fi

# ========== 4. 启动服务 ==========
step "构建镜像..."
if [ -f docker-compose.prod.yaml ]; then
    COMPOSE_FILES="-f docker-compose.yaml -f docker-compose.prod.yaml"
else
    COMPOSE_FILES="-f docker-compose.yaml"
fi
docker compose $COMPOSE_FILES build

step "启动服务..."
docker compose $COMPOSE_FILES up -d

step "等待服务就绪..."
sleep 5
docker compose $COMPOSE_FILES ps

# ========== 5. 导入数据库（如果有备份文件） ==========
if [ -f "$DB_BACKUP_FILE" ]; then
    step "发现数据库备份: $DB_BACKUP_FILE"
    read -p "是否导入数据库备份？这将覆盖现有数据 [y/N]: " answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        step "导入数据库..."
        DB_PASSWORD=$(grep DB_PASSWORD "$PROJECT_DIR/.env" | cut -d= -f2)
        docker exec -i casedance_db mysql -uroot -p"$DB_PASSWORD" casedance < "$DB_BACKUP_FILE"
        step "数据库导入完成"
    fi
fi

# ========== 6. 迁移 + 静态文件 ==========
step "执行数据库迁移..."
docker exec casedance_web python manage.py migrate --noinput 2>/dev/null || warn "迁移失败，可能已是最新"

step "收集静态文件..."
docker exec casedance_web python manage.py collectstatic --noinput 2>/dev/null || warn "静态文件收集失败"

# ========== 7. Nginx ==========
step "配置 Nginx..."
if command -v nginx &>/dev/null; then
    if [ -f "$PROJECT_DIR/nginx.conf" ]; then
        SERVER_NAME=$(grep SERVER_NAME "$PROJECT_DIR/.env" | cut -d= -f2)
        sed "s/<域名或IP>/${SERVER_NAME:-_}/g" "$PROJECT_DIR/nginx.conf" > /etc/nginx/conf.d/casedance.conf
        nginx -t && nginx -s reload 2>/dev/null && step "Nginx 已配置并重载" || warn "Nginx 配置有误，请检查 /etc/nginx/conf.d/casedance.conf"
    fi
else
    step "安装 Nginx..."
    apt install nginx -y
    SERVER_NAME=$(grep SERVER_NAME "$PROJECT_DIR/.env" | cut -d= -f2)
    sed "s/<域名或IP>/${SERVER_NAME:-_}/g" "$PROJECT_DIR/nginx.conf" > /etc/nginx/conf.d/casedance.conf
    nginx -t && nginx -s reload && step "Nginx 已安装并启动"
fi

# ========== 8. 完成 ==========
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "  访问地址:  http://$IP:8000"
echo "  Flower:    http://$IP:5555"
echo ""
echo "  常用命令:"
echo "    cd $PROJECT_DIR"
echo "    docker compose logs -f web        # 查看 Web 日志"
echo "    docker compose restart celery      # 重启 Celery"
echo "    docker compose up -d --build      # 重新构建并启动"
echo "    docker compose ps                 # 查看服务状态"
echo ""
