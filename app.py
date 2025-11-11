import os
import enum
from flask import Flask, render_template, redirect, url_for, request, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from prometheus_flask_exporter import PrometheusMetrics
from datetime import datetime
from functools import wraps
from sqlalchemy import or_

db = SQLAlchemy()

class UserRole(enum.Enum):
    VIEWER = 'viewer'
    EDITOR = 'editor'
    ADMIN = 'admin'

# --- Декоратор для проверки ролей ---
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Требуется авторизация', 'warning')
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            required_roles = []
            if role == UserRole.EDITOR:
                required_roles = [UserRole.EDITOR, UserRole.ADMIN]
            elif role == UserRole.ADMIN:
                required_roles = [UserRole.ADMIN]
            
            if user.role not in required_roles:
                flash('У вас недостаточно прав для этого действия.', 'danger')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    articles = db.relationship('Article', backref='author', lazy=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.EDITOR, nullable=False)

class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    key = db.Column(db.String(10), unique=True, nullable=False)
    articles = db.relationship('Article', backref='space', lazy=True)

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    children = db.relationship('Article', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    versions = db.relationship('ArticleVersion', backref='article', lazy='dynamic', cascade="all, delete-orphan")


class ArticleVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    author = db.relationship('User')


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')

    db.init_app(app)
    
    # Инициализация Prometheus метрик
    if os.environ.get('FLASK_ENV') != 'testing':
        metrics = PrometheusMetrics(app)
        # metrics.info('flask_blog_info', 'Flask Blog Application Info', version=__version__)

    # Инициализация БД при старте
    with app.app_context():
        try:
            db.create_all()
            if not Space.query.first():
                default_space = Space(name="General", key="GEN")
                db.session.add(default_space)
                db.session.commit()
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin', 
                    password=generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'admin')), 
                    role=UserRole.ADMIN
                )
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            pass

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = User.query.get(user_id)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'version': __version__}
        # return {'status': 'ok', 'version': __version__}
    
    @app.route('/health/db')
    def health_db():
        try:
            db.session.execute(db.text('SELECT 1'))
            return {'status': 'ok', 'database': 'connected'}
        except Exception as e:
            return {'status': 'error', 'database': 'disconnected', 'error': str(e)}, 503

    @app.route('/debug')
    def debug():
        try:
            db_status = 'connected' if db.session.execute(db.text('SELECT 1')) else 'disconnected'
        except:
            db_status = 'disconnected'
        
        return {
            'app_version': __version__,
            'database': db_status,
            'environment': os.environ.get('FLASK_ENV', 'unknown')
        }
    
    @app.route('/')
    def home():
        try:
            spaces = Space.query.order_by(Space.name).all()
        except:
            spaces = []
        return render_template('index.html', spaces=spaces)

    @app.route('/space/<string:space_key>')
    def space_home(space_key):
        space = Space.query.filter_by(key=space_key).first_or_404()
        articles = Article.query.filter_by(space_id=space.id, parent_id=None).order_by(Article.title).all()
        return render_template('space.html', space=space, articles=articles)

    @app.route('/space/<string:space_key>/<int:article_id>')
    def view_article(space_key, article_id):
        space = Space.query.filter_by(key=space_key).first_or_404()
        article = Article.query.filter_by(id=article_id, space_id=space.id).first_or_404()
        return render_template('view_article.html', article=article)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                
                if User.query.filter_by(username=username).first():
                    flash('Пользователь уже существует', 'warning')
                    return redirect(url_for('register'))
                
                # Назначаем первого пользователя админом
                role = UserRole.ADMIN if User.query.count() == 0 else UserRole.READER
                
                user = User(username=username, password=generate_password_hash(password), role=role)
                db.session.add(user)
                db.session.commit()
                flash('Регистрация успешна. Войдите.', 'success')
                return redirect(url_for('login'))
                
            except:
                flash('Ошибка регистрации', 'danger')
                return render_template('register.html')
        
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
                session['user_role'] = user.role.name
                flash(f'Вы вошли как {user.username}')
                return redirect(url_for('home'))
            
            flash('Неверные данные')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Вы вышли из аккаунта')
        return redirect(url_for('home'))

    @app.route('/create', methods=['GET', 'POST'])
    @role_required(UserRole.EDITOR)
    def create():
        if request.method == 'POST':
            parent_id = request.form.get('parent_id')
            if not parent_id or parent_id == 'None':
                parent_id = None
            else:
                parent_id = int(parent_id)

            article = Article(
                title=request.form['title'],
                content=request.form['content'],
                author_id=session['user_id'],
                space_id=request.form['space_id'],
                parent_id=parent_id
            )
            db.session.add(article)
            db.session.commit()

            # Создаем первую версию
            version = ArticleVersion(
                article_id=article.id,
                author_id=session['user_id'],
                title=article.title,
                content=article.content
            )
            db.session.add(version)
            db.session.commit()

            space = Space.query.get(article.space_id)
            return redirect(url_for('view_article', space_key=space.key, article_id=article.id))
        
        preselected_space_id = request.args.get('space_id', type=int)
        spaces = Space.query.all()
        articles_for_parent_dropdown = []
        if preselected_space_id:
            articles_for_parent_dropdown = Article.query.filter_by(space_id=preselected_space_id).all()
        
        return render_template('create.html', 
                               spaces=spaces, 
                               articles_for_parent_dropdown=articles_for_parent_dropdown,
                               preselected_space_id=preselected_space_id)

    @app.route('/edit/<int:article_id>', methods=['GET', 'POST'])
    def edit(article_id):
        article = Article.query.get_or_404(article_id)
        
        if 'user_id' not in session:
            flash('Нет доступа')
            return redirect(url_for('home'))
        
        current_user = User.query.get(session['user_id'])
        if current_user.role != UserRole.ADMIN and session['user_id'] != article.author_id:
            flash('Нет доступа')
            return redirect(url_for('home'))

        if request.method == 'POST':
            article.title = request.form['title']
            article.content = request.form['content']

            version = ArticleVersion(
                article_id=article.id,
                author_id=session['user_id'],
                title=article.title,
                content=article.content
            )
            db.session.add(version)
            db.session.commit()

            return redirect(url_for('view_article', space_key=article.space.key, article_id=article.id))
        
        return render_template('edit.html', article=article)

    @app.route('/history/<int:article_id>')
    def history(article_id):
        if 'user_id' not in session:
            flash('Только для авторизованных')
            return redirect(url_for('login'))
            
        article = Article.query.get_or_404(article_id)
        versions = article.versions.order_by(ArticleVersion.created_at.desc()).all()
        return render_template('history.html', article=article, versions=versions)

    @app.route('/search')
    def search():
        query = request.args.get('q')
        if not query:
            return redirect(url_for('home'))
        
        results = Article.query.filter(
            or_(
                Article.title.ilike(f'%{query}%'),
                Article.content.ilike(f'%{query}%')
            )
        ).all()
        
        return render_template('search_results.html', query=query, results=results, results_count=len(results))

    @app.route('/delete/<int:article_id>', methods=['POST'])
    def delete(article_id):
        article = Article.query.get_or_404(article_id)
        
        if 'user_id' not in session:
            flash('Нет доступа')
            return redirect(url_for('home'))

        current_user = User.query.get(session['user_id'])
        if current_user.role != UserRole.ADMIN and session['user_id'] != article.author_id:
            flash('Нет доступа')
            return redirect(url_for('home'))
        
        space_key = article.space.key
        db.session.delete(article)
        db.session.commit()
        flash('Статья удалена')
        return redirect(url_for('space_home', space_key=space_key))

    return app

__version__ = '2.7.0-dev'