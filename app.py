from flask import Flask, request, jsonify

app = Flask(__name__)

# Примитивная "база" в памяти
posts = []
comments = []

@app.route('/')
def index():
    return "<h2>Flask Blog API работает!</h2><p>Используйте /posts для работы с постами.</p>"

@app.route('/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.json
        post_id = len(posts) + 1
        post = {'id': post_id, 'title': data['title'], 'content': data['content']}
        posts.append(post)
        return jsonify(post), 201
    return jsonify(posts)

@app.route('/posts/<int:post_id>/comments', methods=['GET', 'POST'])
def handle_comments(post_id):
    if request.method == 'POST':
        data = request.json
        comment_id = len(comments) + 1
        comment = {'id': comment_id, 'post_id': post_id, 'text': data['text']}
        comments.append(comment)
        return jsonify(comment), 201
    post_comments = [c for c in comments if c['post_id'] == post_id]
    return jsonify(post_comments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
