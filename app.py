import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER): 
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Diocli2021@localhost/loja_camisas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Camisa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    preco = db.Column(db.Float)
    descricao = db.Column(db.Text)
    imagem_url = db.Column(db.String(255)) 
    qtd_p = db.Column(db.Integer, default=0)
    qtd_m = db.Column(db.Integer, default=0)
    qtd_g = db.Column(db.Integer, default=0)
    qtd_gg = db.Column(db.Integer, default=0)

    imagens = db.relationship('ImagemCamisa', backref='camisa', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id, 
            "nome": self.nome, 
            "preco": self.preco,
            "descricao": self.descricao, 
            "imagem": self.imagem_url,
            "outras_fotos": [{"id": img.id, "url": img.url} for img in self.imagens], 
            "qtd_p": self.qtd_p, 
            "qtd_m": self.qtd_m, 
            "qtd_g": self.qtd_g, 
            "qtd_gg": self.qtd_gg
    }

class ImagemCamisa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    camisa_id = db.Column(db.Integer, db.ForeignKey('camisa.id'), nullable=False)

class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

class Avaliacao(db.Model):
    __tablename__ = 'avaliacao'
    id = db.Column(db.Integer, primary_key=True)
    camisa_id = db.Column(db.Integer, db.ForeignKey('camisa.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=False)

@app.route('/uploads/<filename>')
def servir_imagem(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/camisas', methods=['GET', 'POST'])
def rota_camisas():
    if request.method == 'GET':
        camisas = Camisa.query.all()
        return jsonify([c.to_dict() for c in camisas])

    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            preco = request.form.get('preco')
            descricao = request.form.get('descricao') 
            qtd_p = request.form.get('qtd_p', 0)
            qtd_m = request.form.get('qtd_m', 0)
            qtd_g = request.form.get('qtd_g', 0)
            qtd_gg = request.form.get('qtd_gg', 0)

            nova_camisa = Camisa(
                nome=nome,
                preco=float(preco) if preco else 0.0,
                descricao=descricao,
                qtd_p=int(qtd_p) if qtd_p else 0,
                qtd_m=int(qtd_m) if qtd_m else 0,
                qtd_g=int(qtd_g) if qtd_g else 0,
                qtd_gg=int(qtd_gg) if qtd_gg else 0
            )

            fotos = request.files.getlist('fotos')
            if fotos:
                for i, foto in enumerate(fotos):
                    if foto.filename != '':
                        nome_arq = secure_filename(f"{i}_{foto.filename}")
                        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arq))
                        url_foto = f"http://127.0.0.1:5000/uploads/{nome_arq}"
                        
                        if i == 0:
                            nova_camisa.imagem_url = url_foto
                        
                        nova_imagem = ImagemCamisa(url=url_foto, camisa=nova_camisa)
                        db.session.add(nova_imagem)

            db.session.add(nova_camisa)
            db.session.commit()
            return jsonify({"msg": "Camisa cadastrada com sucesso!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": str(e)}), 400

@app.route('/camisas/<int:id>', methods=['PUT', 'DELETE'])
def gerenciar_camisa(id):
    camisa = Camisa.query.get(id)
    if not camisa:
        return jsonify({"erro": "Produto não encontrado"}), 404

    if request.method == 'DELETE':
        try:
            db.session.delete(camisa)
            db.session.commit()
            return jsonify({"mensagem": "Removido com sucesso"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": str(e)}), 400
    
    if request.method == 'PUT':
        try:
            dados = request.form if request.form else request.json
            
            if 'nome' in dados: camisa.nome = dados['nome']
            if 'preco' in dados: camisa.preco = float(dados['preco'])
            if 'descricao' in dados: camisa.descricao = dados['descricao']
            if 'qtd_p' in dados: camisa.qtd_p = int(dados['qtd_p'])
            if 'qtd_m' in dados: camisa.qtd_m = int(dados['qtd_m'])
            if 'qtd_g' in dados: camisa.qtd_g = int(dados['qtd_g'])
            if 'qtd_gg' in dados: camisa.qtd_gg = int(dados['qtd_gg'])

            novas_fotos = request.files.getlist('fotos')
            if novas_fotos:
                for foto in novas_fotos:
                    if foto.filename != '':
                        nome_arq = secure_filename(foto.filename)
                        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arq))
                        url_foto = f"http://127.0.0.1:5000/uploads/{nome_arq}"
                        nova_img = ImagemCamisa(url=url_foto, camisa=camisa)
                        db.session.add(nova_img)

            db.session.commit()
            return jsonify({"msg": "Produto atualizado com sucesso!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": str(e)}), 400

@app.route('/registrar_fornecedor', methods=['POST'])
def registrar():
    dados = request.json
    try:
        novo_f = Fornecedor(email=dados['email'], senha=dados['senha'])
        db.session.add(novo_f)
        db.session.commit()
        return jsonify({"msg": "Fornecedor criado!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao cadastrar fornecedor"}), 400

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    fornecedor = Fornecedor.query.filter_by(email=dados['email'], senha=dados['senha']).first()
    if fornecedor:
        return jsonify({"status": "sucesso", "mensagem": "Login realizado"}), 200
    return jsonify({"status": "erro", "mensagem": "Email ou senha incorretos"}), 401

@app.route('/avaliar', methods=['POST'])
def avaliar():
    try:
        dados = request.get_json() 
        if not dados:
            return jsonify({"error": "Dados não recebidos"}), 400
            
        nova_aval = Avaliacao(
            camisa_id=int(dados['camisa_id']), 
            nome=dados['nome'],
            nota=int(dados['nota']),           
            comentario=dados['comentario']
        )
        db.session.add(nova_aval)
        db.session.commit()
        return jsonify({"message": "Sucesso!"}), 201
    except Exception as e:
        print(f"Erro no Servidor: {e}") 
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@app.route('/avaliacoes/<int:camisa_id>', methods=['GET'])
def listar_avaliacoes(camisa_id):
    avals = Avaliacao.query.filter_by(camisa_id=camisa_id).all()
    return jsonify([{
        "nome": a.nome, 
        "nota": a.nota, 
        "comentario": a.comentario
    } for a in avals])    
    
@app.route('/fotos/<int:foto_id>', methods=['DELETE'])
def deletar_foto(foto_id):
    try:
        foto = ImagemCamisa.query.get(foto_id)
        if not foto:
            return jsonify({"erro": "Foto não encontrada"}), 404
        
        # Opcional: deletar o arquivo físico da pasta uploads aqui
        
        db.session.delete(foto)
        db.session.commit()
        return jsonify({"msg": "Foto removida com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)