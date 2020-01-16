from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

DB_USER = 'root'
DB_PASS =  'passwd' 
DB_HOST = '127.0.0.1'
DATABASE = 'desafio'

app.config['SQLALCHEMY_DATABASE_URI']='mysql://'+DB_USER+':'+ DB_PASS+'@'+DB_HOST+'/'+DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key = 'passwd'
db = SQLAlchemy(app)

statusList = {"A": "Ativo", "I": "Inativo"}
sexoList = {"M": "Masculino", "F": "Feminino", "O": "Outros"}

empresas = db.Table('empresa_usuario',
    db.Column('empresa_id', db.Integer, db.ForeignKey('empresa.id'), primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
)

class Empresa(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(10))
    nome = db.Column(db.String(150))
    cnpj = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    usuarios = db.relationship('Usuario', secondary=empresas, lazy='subquery',
        backref=db.backref('empresa', lazy=True))
    def __init__(self, status, nome, cnpj, endereco):
        self.status = status
        self.nome = nome
        self.cnpj = cnpj
        self.endereco = endereco
    def getStatus(self):
        return statusList[self.status]
        
class Usuario(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255))
    cpf = db.Column(db.String(255))
    sexo = db.Column(db.String(255))
    empresas = db.relationship('Empresa', secondary=empresas, lazy='subquery',
        backref=db.backref('usuario', lazy=True))
    def __init__(self, nome, cpf, sexo):
        self.nome = nome  
        self.cpf = cpf
        self.sexo = sexo
        
    def getSexo(self):
        return sexoList[self.sexo]
        
# --------------------------- ROTAS EMPRESA ------------------------------------------------------
@app.route('/')
@app.route('/empresas')
def indexEmpresa():
    empresas = Empresa.query.all()
    return render_template('empresaIndex.html', active_page="/empresas" ,titulo="Empresas", empresas=empresas)

@app.route('/empresa/visualizar/<int:id>', methods=["GET"])
def visualizarEmpresa(id):
    try:
        empresa = Empresa.query.get_or_404(id)
    except: 
        flash("Erro ao visualizar empresa", "danger")
        return redirect(url_for('indexEmpresa'))
    
    return render_template('empresaVisualizar.html', active_page="/empresas", titulo="Empresa - visualização", empresa=empresa)

@app.route('/empresa/cadastrar', methods=["GET", "POST"])
def cadastrarEmpresa():
    if request.method == 'POST':
        empresa = Empresa(request.form["status"],
            request.form["nome"],
            request.form["cnpj"], 
            request.form["endereco"])
        db.session.add(empresa)
        db.session.commit()
        flash('Empresa cadastrada com sucesso!', 'success')
        return redirect(url_for('indexEmpresa'))
    
    return render_template('empresaCadastrar.html', active_page="/empresas", titulo="Empresa - cadastro")

@app.route('/empresa/editar/<int:id>', methods=['GET', 'POST'])
def editarEmpresa(id):
    try:
        empresa = Empresa.query.get_or_404(id)
    except: 
        flash('Erro ao editar empresa', 'danger')
        return redirect(url_for('indexEmpresa'))
    if request.method == 'POST':
        empresa.status = request.form['status']
        empresa.nome = request.form['nome']
        empresa.cnpj = request.form['cnpj']
        empresa.endereco = request.form['endereco']
        db.session.commit()
        flash('Empresa editada com sucesso!', 'success')
        return redirect(url_for('indexEmpresa'))
    
    return render_template('empresaEditar.html', active_page="/empresas", titulo="Empresa - edição", empresa=empresa)
        
@app.route('/empresa/deletar/<int:id>')
def deletarEmpresa(id):
    try:
        empresa = Empresa.query.get_or_404(id)
        db.session.delete(empresa)
        db.session.commit()
        flash("Empresa excluída com sucesso!", "success")
    except:
        flash("Erro ao excluir empresa", "danger")
        return redirect(url_for('indexEmpresa'))
    
    return redirect(url_for('indexEmpresa'))

# --------------------------- ROTAS USUARIO ------------------------------------------------------
@app.route('/usuarios')
def indexUsuario():
    usuarios = Usuario.query.all()
    return render_template('usuarioIndex.html', active_page="/usuarios", titulo="Usuários", usuarios=usuarios)

@app.route('/usuario/visualizar/<int:id>', methods=["GET"])
def visualizarUsuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
    except:
        flash("Erro ao visualizar usuário", "danger")
        return redirect(url_for('indexUsuario'))
    return render_template('usuarioVisualizar.html', active_page="/usuarios", titulo="Usuário - visualização", usuario=usuario)

@app.route('/usuario/cadastrar', methods=["GET", "POST"])
def cadastrarUsuario():
    listaEmpresa = Empresa.query.filter_by(status="A").all()
    if request.method == 'POST':
        usuario = Usuario(request.form["nome"],
            request.form["cpf"], 
            request.form["sexo"])
        db.session.add(usuario)
        db.session.commit()
        for emp in request.form.getlist("empresa"):
            statement = empresas.insert().values(empresa_id=emp, usuario_id=usuario.id)
            db.session.execute(statement)
        db.session.commit()
        flash('Usuário cadastrado com sucesso.', 'success')
        return redirect(url_for('indexUsuario'))
    
    return render_template('usuarioCadastrar.html', active_page="/usuarios", titulo="Usuário - cadastro", listaEmpresa=listaEmpresa)

@app.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editarUsuario(id):
    listaEmpresa = Empresa.query.filter_by(status="A").all()
    try:
        usuario = Usuario.query.get_or_404(id)
    except:
        flash('Erro ao editar usuário', 'danger')
        return redirect(url_for('indexUsuario'))
        
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.cpf = request.form['cpf']
        usuario.sexo = request.form['sexo']
        usuario.empresas.clear()
        db.session.commit()
        for emp in request.form.getlist("empresa"):
            statement = empresas.insert().values(empresa_id=emp, usuario_id=id)
            db.session.execute(statement)
        db.session.commit()
        flash('Usuário editado com sucesso.', 'success')
        return redirect(url_for('indexUsuario'))
    
    return render_template('usuarioEditar.html', active_page="/usuarios", titulo="Usuário - edição", usuario=usuario, listaEmpresa=listaEmpresa)
        
@app.route('/usuario/deletar/<int:id>')
def deletarUsuario(id):
    try:
        usuario = Usuario.query.get_or_404(id)
        usuario.empresas.clear()
        db.session.commit()
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuário excluído com sucesso.', 'success')
    except:
        flash('Erro ao excluir o usuário.', 'danger')
        return redirect(url_for('indexUsuario'))
    
    return redirect(url_for('indexUsuario'))
    
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=3000)