from flask import Flask, request, jsonify
from models import db, Post, Comment

app = Flask(__name__)

# Конфиг для PostgreSQL (используем Docker)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return "<h2>Flask Blog API работает с PostgreSQL!</h2>"

@app.route('/posts', methods=['GET', 'POST'])
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

@app.route('/posts/<int:post_id>/comments', methods=['GET', 'POST'])
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
