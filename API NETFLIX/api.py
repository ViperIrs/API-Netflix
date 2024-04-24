from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streaming.db'
db = SQLAlchemy(app)

# Definição do modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Definição do modelo de Título (Filme ou Série)
class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    # Adicione outros campos conforme necessário

# Rota para registro de usuários
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Rota para autenticação de usuários
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401
    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return jsonify({'message': 'User not found', 'data': {}}), 401
    if check_password_hash(user.password, auth.password):
        # Aqui você pode gerar um token JWT para autenticação
        return jsonify({'message': 'Logged in successfully', 'data': {}}), 200
    return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401

# Rota para obter informações sobre um título específico
@app.route('/titles/<int:title_id>', methods=['GET'])
def get_title(title_id):
    title = Title.query.get(title_id)
    if not title:
        return jsonify({'message': 'Title not found', 'data': {}}), 404
    # Aqui você pode retornar as informações do título em formato JSON
    return jsonify({'message': 'Title found', 'data': {}}), 200

# Definição do modelo de Histórico de Visualização
class ViewingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'), nullable=False)
    # Adicione outros campos conforme necessário

# Definição do modelo de Listas de Reprodução
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Adicione outros campos conforme necessário

# Rota para adicionar um título ao histórico de visualização do usuário
@app.route('/history/add', methods=['POST'])
def add_to_history():
    data = request.json
    user_id = data.get('user_id')
    title_id = data.get('title_id')
    # Verifica se o usuário e o título existem
    user = User.query.get(user_id)
    title = Title.query.get(title_id)
    if not user or not title:
        return jsonify({'message': 'User or title not found', 'data': {}}), 404
    # Adiciona ao histórico de visualização
    history_entry = ViewingHistory(user_id=user_id, title_id=title_id)
    db.session.add(history_entry)
    db.session.commit()
    return jsonify({'message': 'Title added to viewing history', 'data': {}}), 200

# Rota para criar uma nova lista de reprodução
@app.route('/playlist/create', methods=['POST'])
def create_playlist():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    # Verifica se o usuário existe
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found', 'data': {}}), 404
    # Cria a lista de reprodução
    playlist = Playlist(name=name, user_id=user_id)
    db.session.add(playlist)
    db.session.commit()
    return jsonify({'message': 'Playlist created successfully', 'data': {}}), 201

# Rota para adicionar um título a uma lista de reprodução
@app.route('/playlist/add_title', methods=['POST'])
def add_to_playlist():
    data = request.json
    playlist_id = data.get('playlist_id')
    title_id = data.get('title_id')
    # Verifica se a lista de reprodução e o título existem
    playlist = Playlist.query.get(playlist_id)
    title = Title.query.get(title_id)
    if not playlist or not title:
        return jsonify({'message': 'Playlist or title not found', 'data': {}}), 404
    # Adiciona o título à lista de reprodução
    # Implemente sua lógica aqui
    return jsonify({'message': 'Title added to playlist', 'data': {}}), 200

# Rota para buscar títulos por nome
@app.route('/titles/search', methods=['GET'])
def search_titles():
    query = request.args.get('query')
    titles = Title.query.filter(Title.title.ilike(f'%{query}%')).all()
    # Retorna os títulos encontrados em formato JSON
    # Implemente sua lógica aqui
    return jsonify({'message': 'Titles found', 'data': {}}), 200


# Rota para obter todos os títulos disponíveis
@app.route('/titles', methods=['GET'])
def get_titles():
    titles = Title.query.all()
    # Retorna os títulos em formato JSON
    # Implemente sua lógica aqui
    return jsonify({'message': 'Titles found', 'data': {}}), 200

# Rota para obter detalhes de um título específico
@app.route('/titles/<int:title_id>', methods=['GET'])
def get_title_details(title_id):
    title = Title.query.get(title_id)
    if not title:
        return jsonify({'message': 'Title not found', 'data': {}}), 404
    # Retorna os detalhes do título em formato JSON
    # Implemente sua lógica aqui
    return jsonify({'message': 'Title found', 'data': {}}), 200

# Rota para simular a reprodução de vídeo
@app.route('/playback/<int:title_id>', methods=['GET'])
def playback(title_id):
    title = Title.query.get(title_id)
    if not title:
        return jsonify({'message': 'Title not found', 'data': {}}), 404
    # Implemente sua lógica de reprodução de vídeo aqui
    return jsonify({'message': 'Playback started', 'data': {}}), 200

if __name__ == '__main__':
    app.run(debug=True)
