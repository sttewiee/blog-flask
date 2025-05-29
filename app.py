from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, Post, Comment

app = Flask(__name__)

# Настройка подключения к Postgres (для Docker Compose)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# HTML интерфейс

@app.route('/', methods=['GET'])
def home():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    post = Post(title=title, content=content)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('comments.html', post=post, comments=comments)

@app.route('/post/<int:post_id>/add_comment', methods=['POST'])
def add_comment(post_id):
    text = request.form['text']
    comment = Comment(post_id=post_id, text=text)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))

# REST API

@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.json
        post = Post(title=data['title'], content=data['content'])
        db.session.add(post)
        db.session.commit()
        return jsonify({'id': post.id, 'title': post.title, 'content': post.content}), 201

    posts = Post.query.all()
    return jsonify([
        {'id': p.id, 'title': p.title, 'content': p.content}
        for p in posts
    ])

@app.route('/api/posts/<int:post_id>/comments', methods=['GET', 'POST'])
def handle_comments(post_id):
    if request.method == 'POST':
        data = request.json
        comment = Comment(post_id=post_id, text=data['text'])
        db.session.add(comment)
        db.session.commit()
        return jsonify({'id': comment.id, 'post_id': comment.post_id, 'text': comment.text}), 201

    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([
        {'id': c.id, 'post_id': c.post_id, 'text': c.text}
        for c in comments
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
