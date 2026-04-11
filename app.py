import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Diocli2021@localhost/loja_camisas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Camisa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    preco = db.Column(db.Float)
    imagem_url = db.Column(db.String(255))
    qtd_p = db.Column(db.Integer, default=0)
    qtd_m = db.Column(db.Integer, default=0)
    qtd_g = db.Column(db.Integer, default=0)
    qtd_gg = db.Column(db.Integer, default=0)
    def to_dict(self):
        return {
            "id": self.id, 
            "nome": self.nome, 
            "preco": self.preco, 
            "imagem": self.imagem_url,
            "qtd_p": self.qtd_p, 
            "qtd_m": self.qtd_m, 
            "qtd_g": self.qtd_g, 
            "qtd_gg": self.qtd_gg
        }
    
class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

@app.route('/uploads/<filename>')
def servir_imagem(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/camisas', methods=['GET', 'POST'])
def gerenciar_camisas():
    if request.method == 'POST':
        try:
            nova = Camisa(
                nome=request.form.get('nome'),
                preco=float(request.form.get('preco', 0)),
                qtd_p=int(request.form.get('qtd_p') or 0),
                qtd_m=int(request.form.get('qtd_m') or 0),
                qtd_g=int(request.form.get('qtd_g') or 0),
                qtd_gg=int(request.form.get('qtd_gg') or 0)
            )
            foto = request.files.get('foto')
            if foto and foto.filename != '':
                nome_arq = secure_filename(foto.filename)
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arq))
                nova.imagem_url = f"http://127.0.0.1:5000/uploads/{nome_arq}"
            
            db.session.add(nova)
            db.session.commit()
            return jsonify({"mensagem": "Sucesso"}), 201
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    return jsonify([c.to_dict() for c in Camisa.query.all()])

@app.route('/camisas/<int:id>', methods=['DELETE', 'PUT'])
def acao_camisa(id):
    camisa = Camisa.query.get(id)
    if not camisa: return jsonify({"erro": "Não encontrado"}), 404
    
    if request.method == 'DELETE':
        db.session.delete(camisa)
        db.session.commit()
        return jsonify({"mensagem": "Removido"}), 200
    
    if request.method == 'PUT':
        dados = request.json
        print(f"Dados recebidos para editar ID {id}: {dados}")
        
        try:
            if 'nome' in dados: camisa.nome = dados['nome']
            if 'preco' in dados: camisa.preco = float(dados['preco'])
            if 'qtd_p' in dados: camisa.qtd_p = int(dados['qtd_p'])
            if 'qtd_m' in dados: camisa.qtd_m = int(dados['qtd_m'])
            if 'qtd_g' in dados: camisa.qtd_g = int(dados['qtd_g'])
            if 'qtd_gg' in dados: camisa.qtd_gg = int(dados['qtd_gg'])
            
            db.session.commit()
            return jsonify({"msg": "Sucesso"}), 200
        except Exception as e:
            return jsonify({"err": str(e)}), 400

@app.route('/registrar_fornecedor', methods=['POST'])
def registrar():
    dados = request.json
    if not dados or 'email' not in dados or 'senha' not in dados:
        return jsonify({"erro": "Dados incompletos"}), 400
    
    try:
        novo_f = Fornecedor(email=dados['email'], senha=dados['senha'])
        db.session.add(novo_f)
        db.session.commit()
        return jsonify({"msg": "Fornecedor criado!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Email já cadastrado ou erro no banco"}), 400

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    fornecedor = Fornecedor.query.filter_by(email=dados['email'], senha=dados['senha']).first()
    
    if fornecedor:
        return jsonify({"status": "sucesso", "mensagem": "Login realizado"}), 200
    else:
        return jsonify({"status": "erro", "mensagem": "Email ou senha incorretos"}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
