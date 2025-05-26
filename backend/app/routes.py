from flask import request, jsonify, current_app as app
from .models import db, Post, Comment

@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    return jsonify([{"id": p.id, "title": p.title, "content": p.content} for p in posts])

@app.route("/posts", methods=["POST"])
def create_post():
    data = request.json
    post = Post(title=data["title"], content=data["content"])
    db.session.add(post)
    db.session.commit()
    return jsonify({"id": post.id, "title": post.title, "content": post.content}), 201

@app.route("/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([{"id": c.id, "text": c.text} for c in comments])

@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):
    data = request.json
    comment = Comment(text=data["text"], post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"id": comment.id, "text": comment.text}), 201
