#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PYTHON="/home/ubuntu/anaconda3/envs/TAA/bin/python"
API_MGMT_SCRIPT="$SCRIPT_DIR/app.py"
API_MGMT_PORT=5010
FRONTEND_DIR="$PROJECT_DIR/frontend"
FRONTEND_PORT=3001

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    log_info "正在停止所有服务..."
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        log_ok "API 管理服务已停止 (PID: $API_PID)"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_ok "前端开发服务已停止 (PID: $FRONTEND_PID)"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        API 统一管理模块 - 一键启动脚本          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

if ! command -v $PYTHON &> /dev/null; then
    log_error "未找到 Python: $PYTHON"
    log_info "请确认 conda 环境 TAA 已正确安装"
    exit 1
fi
log_ok "Python 环境检查通过"

if ! $PYTHON -c "import flask; import flask_cors" 2>/dev/null; then
    log_error "缺少依赖: flask 或 flask_cors"
    log_info "正在安装依赖..."
    $PYTHON -m pip install flask flask-cors -q
    log_ok "依赖安装完成"
fi

if ! command -v node &> /dev/null; then
    log_error "未找到 Node.js"
    log_info "请先安装 Node.js (>= 16)"
    exit 1
fi
log_ok "Node.js 环境检查通过"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    log_info "前端依赖未安装，正在安装..."
    cd "$FRONTEND_DIR" && npm install
    log_ok "前端依赖安装完成"
fi

if lsof -i :$API_MGMT_PORT -t &>/dev/null; then
    log_warn "端口 $API_MGMT_PORT 已被占用，正在释放..."
    lsof -i :$API_MGMT_PORT -t | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -i :$FRONTEND_PORT -t &>/dev/null; then
    log_warn "端口 $FRONTEND_PORT 已被占用，正在释放..."
    lsof -i :$FRONTEND_PORT -t | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo ""
log_info "正在启动 API 管理后端服务 (端口: $API_MGMT_PORT)..."
cd "$SCRIPT_DIR"
$PYTHON "$API_MGMT_SCRIPT" --host 0.0.0.0 --port $API_MGMT_PORT &
API_PID=$!
sleep 2

if ! kill -0 $API_PID 2>/dev/null; then
    log_error "API 管理服务启动失败"
    exit 1
fi

HEALTH_CHECK=$(curl -s http://127.0.0.1:$API_MGMT_PORT/api/health 2>/dev/null || echo "")
if echo "$HEALTH_CHECK" | grep -q '"status":"ok"'; then
    log_ok "API 管理服务启动成功 (PID: $API_PID, 端口: $API_MGMT_PORT)"
else
    log_warn "API 管理服务可能未就绪，请稍后检查"
fi

log_info "正在启动前端开发服务 (端口: $FRONTEND_PORT)..."
cd "$FRONTEND_DIR"
npx vite --port $FRONTEND_PORT --host 0.0.0.0 &
FRONTEND_PID=$!
sleep 3

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    log_error "前端开发服务启动失败"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           所有服务已成功启动！                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}API 管理后端${NC}:  http://localhost:$API_MGMT_PORT"
echo -e "  ${CYAN}前端界面${NC}:      http://localhost:$FRONTEND_PORT"
echo -e "  ${CYAN}API 管理页面${NC}:  http://localhost:$FRONTEND_PORT/api-management"
echo ""
echo -e "  按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo ""

wait
