import os
from app import app
import subprocess
import sys

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ.setdefault('FLASK_PORT', '5000')

def start_http_server():
    print("正在启动HTTP服务器...")
    print(f"环境: {os.environ['FLASK_ENV']}")
    print(f"HTTP地址: http://localhost:{os.environ['FLASK_PORT']}")
    print(f"HTTP地址: http://127.0.0.1:{os.environ['FLASK_PORT']}")
    
    try:
        # 运行Flask应用
        app.run(
            host='0.0.0.0',
            port=int(os.environ['FLASK_PORT']),
            debug=(os.environ['FLASK_ENV'] == 'development')
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_http_server()