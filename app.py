from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# 帖子表（自定义接口使用）
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))

# 注册接口
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(username=data["username"], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(msg="register ok")

# 登录接口，返回JWT token
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if user and bcrypt.check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token)
    return jsonify(msg="invalid"),401

# 受保护接口1 GET /api/data
@app.route("/api/data", methods=["GET"])
@jwt_required()
def get_data():
    current_user = get_jwt_identity()
    return jsonify(user=current_user, data="secret information")

# 自定义受保护接口 POST /api/post
@app.route("/api/post", methods=["POST"])
@jwt_required()
def create_post():
    data = request.get_json()
    newpost = Post(content=data["content"])
    db.session.add(newpost)
    db.session.commit()
    return jsonify(post_id=newpost.id)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False)
