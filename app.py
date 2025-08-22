import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from prometheus_flask_exporter import PrometheusMetrics

db = SQLAlchemy()

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


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')

    db.init_app(app)
    
    metrics = PrometheusMetrics(app)
    metrics.info('flask_blog_info', 'Flask Blog Application Info', version=__version__)

    # Инициализация БД при старте
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created successfully')
        except Exception as e:
            app.logger.error(f'Failed to create database tables: {e}')
            app.logger.info('Continuing without database initialization')

    @app.route('/health')
    def health():
        return {'status': 'ok', 'version': __version__}
    
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
            db_status = 'connected'
            db_error = None
            try:
                db.session.execute(db.text('SELECT 1'))
            except Exception as e:
                db_status = 'disconnected'
                db_error = str(e)
            
            # Проверяем доступность шаблонов
            import os
            templates_available = []
            templates_dir = app.template_folder
            if os.path.exists(templates_dir):
                for file in os.listdir(templates_dir):
                    if file.endswith('.html'):
                        templates_available.append(file)
            
            return {
                'app_version': __version__,
                'database': db_status,
                'database_error': db_error,
                'templates_dir': app.template_folder,
                'templates_available': templates_available,
                'static_dir': app.static_folder,
                'environment': os.environ.get('FLASK_ENV', 'unknown')
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/')
    def home():
        try:
            posts = Post.query.order_by(Post.id.desc()).all()
            return render_template('index.html', posts=posts)
        except Exception as e:
            app.logger.error(f'Home error: {e}')
            return render_template('index.html', posts=[])

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        app.logger.info(f'Register route accessed: {request.method}')
        
        try:
            # Проверяем подключение к БД
            db.session.execute(db.text('SELECT 1'))
            app.logger.info('Database connection OK')
            
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                app.logger.info(f'Processing registration for user: {username}')
                
                if User.query.filter_by(username=username).first():
                    flash('Пользователь уже существует')
                    return redirect(url_for('register'))
                
                user = User(username=username, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                flash('Регистрация успешна. Войдите.')
                return redirect(url_for('login'))
            
            app.logger.info('Rendering register template')
            try:
                return render_template('register.html')
            except Exception as template_error:
                app.logger.error(f'Template rendering error: {template_error}')
                app.logger.error(f'Template error type: {type(template_error)}')
                app.logger.error(f'Available templates: {app.template_folder}')
                raise template_error
            
        except Exception as e:
            app.logger.error(f'Registration error: {e}')
            app.logger.error(f'Error type: {type(e)}')
            app.logger.error(f'Error details: {str(e)}')
            
            # Fallback - показываем простую страницу без шаблона
            return f'''
            <html>
            <body>
                <h1>Регистрация</h1>
                <p>Временно недоступно. Попробуйте позже.</p>
                <a href="/">На главную</a>
            </body>
            </html>
            ''', 200

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
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
    def create():
        if 'user_id' not in session:
            flash('Только для авторизованных')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            post = Post(
                title=request.form['title'],
                content=request.form['content'],
                user_id=session['user_id']
            )
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

__version__ = '2.6.5'