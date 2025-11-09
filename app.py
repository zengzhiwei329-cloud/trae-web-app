from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 数据库配置
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')
driver = os.getenv('DB_DRIVER')

# 对密码中的特殊字符进行URL编码
encoded_password = urllib.parse.quote_plus(password)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pyodbc://{user}:{encoded_password}"
    f"@{server}/{database}"
    f"?driver={driver}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 数据模型定义
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    price = db.Column(Numeric(10, 2))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': float(self.price) if self.price else None,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }

class CaseStudy(db.Model):
    __tablename__ = 'case_studies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client = db.Column(db.String(100))
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'client': self.client,
            'category': self.category,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    service_type = db.Column(db.String(50), nullable=False)
    preferred_date = db.Column(db.Date, nullable=True)  # 改为可选字段
    preferred_time = db.Column(db.String(20))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    address = db.Column(db.String(255), nullable=False, default='')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'service_type': self.service_type,
            'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
            'preferred_time': self.preferred_time,
            'description': self.description,
            'status': self.status,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }



# API路由
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        category = request.args.get('category')
        query = Product.query
        
        if category:
            query = query.filter_by(category=category)
        
        products = query.all()
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cases', methods=['GET'])
def get_cases():
    try:
        category = request.args.get('category')
        query = CaseStudy.query
        
        if category:
            query = query.filter_by(category=category)
        
        cases = query.all()
        return jsonify([case.to_dict() for case in cases])
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'database': str(e)}), 500

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'service_type', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # 验证电话号码：必须是11位纯数字
        phone = data.get('phone')
        # 检查是否只包含数字字符
        if not phone.isdigit():
            return jsonify({'error': '电话只能包含数字字符'}), 400
        # 检查长度是否为11位
        if len(phone) != 11:
            return jsonify({'error': '电话必须是11位数字'}), 400
        
        # 创建预约记录
        appointment = Appointment(
            name=data.get('name'),
            phone=data.get('phone', ''),
            service_type=data.get('service_type'),
            preferred_time=data.get('preferred_time', ''),
            description=data.get('description', ''),
            address=data.get('address', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
        return jsonify([appointment.to_dict() for appointment in appointments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """提供主页"""
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def custom_static(filename):
    """提供静态文件"""
    return app.send_static_file(filename)

# 创建数据库表
with app.app_context():
    try:
        db.create_all()
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库连接失败: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv('p', 5000)))