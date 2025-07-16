# app.py
import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла---
load_dotenv()

# --- Инициализируем расширения здесь, но не привязываем их к приложению --------
db = SQLAlchemy()
migrate = Migrate()


# --- МОДЕЛИ (теперь они не зависят от 'app') --------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def create_app(config_name=None):
    """Фабрика приложений."""
    app = Flask(__name__)

    # --- Загружаем конфигурацию -----
    # Порядок приоритета:
    # 1. Из файла, указанного в `FLASK_CONFIG`
    # 2. Из переменных окружения
    if config_name:
        # Для будущих нужд (dev, prod, test configs)
        pass

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///blog.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')

    # --- Привязываем расширения к приложению ---
    db.init_app(app)
    migrate.init_app(app, db)

    # --- Регистрируем роуты (Blueprint'ы - лучший способ, но пока так) ----
    @app.route('/')
    def home():
        posts = Post.query.order_by(Post.id.desc()).all()
        return render_template('index.html', posts=posts)

    # ... (все остальные ваши роуты копируются сюда, без изменений) ...
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Пользователь уже существует')
                return redirect(url_for('register'))
            hashed = generate_password_hash(password)
            user = User(username=username, password=hashed)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна. Войдите.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Вы вошли как ' + user.username)
                return redirect(url_for('home'))
            flash('Неверные данные')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('username', None)
        flash('Вы вышли из аккаунта')
        return redirect(url_for('home'))

    @app.route('/create', methods=['GET', 'POST'])
    def create():
        if 'user_id' not in session:
            flash('Только для авторизованных')
            return redirect(url_for('login'))
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            post = Post(title=title, content=content, user_id=session['user_id'])
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('create.html')

    @app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
    def edit(post_id):
        post = Post.query.get_or_404(post_id)
        if 'user_id' not in session or session['user_id'] != post.user_id:
            flash('Нет доступа')
            return redirect(url_for('home'))
        if request.method == 'POST':
            post.title = request.form['title']
            post.content = request.form['content']
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('edit.html', post=post)

    @app.route('/delete/<int:post_id>', methods=['POST'])
    def delete(post_id):
        post = Post.query.get_or_404(post_id)
        if 'user_id' not in session or session['user_id'] != post.user_id:
            flash('Нет доступа')
            return redirect(url_for('home'))
        db.session.delete(post)
        db.session.commit()
        flash('Пост удалён')
        return redirect(url_for('home'))

    return app