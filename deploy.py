"""English Quest 部署脚本 — 上传到阿里云 ECS 并启动服务"""
import os
import sys
import getpass
from pathlib import Path

import paramiko

# ── 配置 ──────────────────────────────────────────────
SERVER = "47.239.122.123"
USER = "root"
PORT = 22
REMOTE_DIR = "/opt/english-quest"
PORT_NUM = 8001
LOCAL_TAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "english-quest-deploy.tar.gz")

# ── 步骤 ──────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  English Quest · 部署到服务器")
    print("=" * 50)
    print()

    if not os.path.exists(LOCAL_TAR):
        print("[错误] 未找到部署包，请先在项目根目录执行：")
        print("  tar -czf english-quest-deploy.tar.gz --exclude='__pycache__' --exclude='data' --exclude='.env' --exclude='node_modules' --exclude='design' english-quest/")
        sys.exit(1)

    password = os.getenv("SSH_PASSWORD") or getpass.getpass("请输入服务器 root 密码: ")

    print("\n[1/5] 连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER, PORT, USER, password, timeout=15)
    print("  已连接")

    print("[2/5] 上传部署包...")
    sftp = ssh.open_sftp()
    sftp.put(LOCAL_TAR, f"/tmp/english-quest-deploy.tar.gz")
    sftp.close()
    print("  上传完成 (28KB)")

    print("[3/5] 服务器端安装...")
    # 读取本地 .env 密钥
    local_env = {}
    local_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(local_env_path):
        with open(local_env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    local_env[k] = v

    secret_key = local_env.get("SECRET_KEY") or os.urandom(16).hex()
    admin_pw = local_env.get("ADMIN_PASSWORD", "")
    ds_key = local_env.get("DEEPSEEK_API_KEY", "")
    volc_id = local_env.get("VOLC_APP_ID", "")
    volc_token = local_env.get("VOLC_ACCESS_TOKEN", "")

    commands = f"""
set -e
mkdir -p {REMOTE_DIR}
cd {REMOTE_DIR}

# 停旧服务
fuser -k {PORT_NUM}/tcp 2>/dev/null || true
sleep 1

# 解压
tar -xzf /tmp/english-quest-deploy.tar.gz --strip-components=1 2>/dev/null || tar -xzf /tmp/english-quest-deploy.tar.gz --strip-components=1

# 清除缓存（强制重新生成）
find . -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true
rm -rf static/audio/tts_cache/*.mp3 2>/dev/null || true
echo "缓存已清除"

# 创建 .env
cat > .env << ENVEOF
SECRET_KEY={secret_key}
ADMIN_USERNAME=Dimer
ADMIN_PASSWORD={admin_pw}
DEEPSEEK_API_KEY={ds_key}
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
SECURE_COOKIES=true
VOLC_APP_ID={volc_id}
VOLC_ACCESS_TOKEN={volc_token}
ENVEOF

# 安装依赖
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ -q 2>&1 | tail -1

# 创建数据目录
mkdir -p data

# 导入种子数据
python3 scripts/seed_data.py 2>&1

echo "服务端安装完成"
"""
    stdin, stdout, stderr = ssh.exec_command(commands)
    out = stdout.read().decode("utf-8")
    err = stderr.read().decode("utf-8")
    if out:
        print("  " + out.replace("\n", "\n  "))
    if err:
        print("  [stderr] " + err.replace("\n", "\n  ")[:500])

    print("[4/5] 启动服务...")
    # Use systemd service (handles auto-restart on reboot)
    ssh.exec_command(f"systemctl restart english-quest 2>/dev/null || (cd {REMOTE_DIR} && nohup python3 app.py > app.log 2>&1 &)")
    import time
    time.sleep(3)

    stdin, stdout, stderr = ssh.exec_command(f"systemctl status english-quest --no-pager | head -3")
    status = stdout.read().decode("utf-8")
    print("  " + status.replace("\n", "\n  "))

    print("[5/5] 验证服务...")
    verify_cmd = f"curl -s http://localhost:{PORT_NUM}/api/scenarios | head -c 100"
    stdin, stdout, stderr = ssh.exec_command(verify_cmd)
    verify = stdout.read().decode("utf-8").strip()[:100]
    print(f"  {verify}")

    ssh.close()

    print()
    print("=" * 50)
    print("  部署完成！")
    print()
    print("  HTTPS: https://dimerenglish.top")
    print("  服务: systemctl status english-quest")
    print("=" * 50)


if __name__ == "__main__":
    main()
