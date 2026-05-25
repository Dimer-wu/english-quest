"""快速部署 — 仅上传 tts.py + 清缓存 + 重启"""
import os, sys, getpass
import paramiko

SERVER = "47.239.122.123"
REMOTE_DIR = "/opt/english-quest"

password = os.getenv("SSH_PASSWORD") or getpass.getpass("服务器 root 密码: ")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, 22, "root", password, timeout=15)
print("已连接")

# 上传 tts.py
sftp = ssh.open_sftp()
local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts.py")
sftp.put(local, f"{REMOTE_DIR}/tts.py")
sftp.close()
print("tts.py 上传完成")

# 清缓存 + 重启
cmds = f"""
cd {REMOTE_DIR}
rm -rf static/audio/tts_cache/*.mp3 2>/dev/null
echo "缓存已清除"
fuser -k 8001/tcp 2>/dev/null || true
sleep 1
nohup python3 app.py > app.log 2>&1 &
sleep 3
cat app.log | tail -3
echo "---"
curl -s "http://localhost:8001/api/tts?text=Hey+there+how+are+you" -o /tmp/tts_test.mp3 -w "TTS: HTTP %{{http_code}}, size: %{{size_download}} bytes"
"""
stdin, stdout, stderr = ssh.exec_command(cmds)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("stderr:", err[:300])

ssh.close()
print("\n部署完成！")
