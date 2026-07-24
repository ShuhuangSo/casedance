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
docker exec casedance_web python manage.py migrate --noinput || warn "迁移失败，继续..."

step "收集静态文件..."
docker exec casedance_web python manage.py collectstatic --noinput || warn "静态文件收集失败"

# ========== 7. Nginx ==========
step "配置 Nginx..."

# 安装 Nginx（如未安装）
if ! command -v nginx &>/dev/null; then
    step "安装 Nginx..."
    apt update -qq && apt install nginx -y
fi

# 删除 Ubuntu 默认站点，避免劫持请求
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
    step "已移除 Nginx 默认站点"
fi

# 写入配置
SERVER_NAME=$(grep SERVER_NAME "$PROJECT_DIR/.env" | cut -d= -f2)
sed "s/<域名或IP>/${SERVER_NAME:-_}/g" "$PROJECT_DIR/nginx.conf" > /etc/nginx/conf.d/casedance.conf

# 验证并重载
if nginx -t 2>/dev/null; then
    systemctl enable nginx 2>/dev/null || true
    nginx -s reload 2>/dev/null || nginx
    step "Nginx 已配置并启动"
else
    warn "Nginx 配置有误，请手动检查 /etc/nginx/conf.d/casedance.conf"
fi

# ========== 8. 验证 ==========
step "验证部署..."

# 检查静态文件
if [ -f "$PROJECT_DIR/static/admin/css/login.css" ]; then
    step "静态文件: OK"
else
    warn "静态文件可能未正确收集"
fi

# 检查 API 可达
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8002/api/ 2>/dev/null | grep -q "30[12]\|200\|40[34]"; then
    step "Django API: OK"
else
    warn "Django 可能未就绪，稍后重试: docker compose logs web --tail=20"
fi

# ========== 9. 完成 ==========
PRIVATE_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "未知")
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "  内网访问:  http://$PRIVATE_IP"
echo "  公网访问:  http://$PUBLIC_IP"
echo "  Flower:    http://$PUBLIC_IP:5555"
echo "  Django API: http://${SERVER_NAME:-$PUBLIC_IP}:8000/api/"
echo ""
echo "  常用命令:"
echo "    cd $PROJECT_DIR"
echo "    docker compose logs -f web        # 查看 Web 日志"
echo "    docker compose restart celery      # 重启 Celery"
echo "    docker compose up -d --build      # 重新构建并启动"
echo "    docker compose ps                 # 查看服务状态"
echo ""
