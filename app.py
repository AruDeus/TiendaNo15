import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_por_defecto")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client['tienda_db']

db.usuarios.create_index("email", unique=True)

@app.before_request
def seed_data():
    demo_email = "demo@demo.com"
    if not db.usuarios.find_one({"email": demo_email}):
        db.usuarios.insert_one({
            "email": demo_email,
            "password": generate_password_hash("Demo1234")
        })
    
    if db.productos.count_documents({}) == 0:
        db.productos.insert_many([
            {"nombre": "Laptop Pro", "precio": 1200.0, "stock": 10},
            {"nombre": "Mouse Optico", "precio": 25.0, "stock": 50},
            {"nombre": "Teclado Mecanico", "precio": 75.0, "stock": 20}
        ])

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash("Debes iniciar sesión para acceder.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = db.usuarios.find_one({"email": email})
        if usuario and check_password_hash(usuario['password'], password):
            session['usuario'] = email
            return redirect(url_for('listar_productos'))
        else:
            flash("Credenciales incorrectas.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/productos')
@login_required
def listar_productos():
    productos = list(db.productos.find())
    return render_template('productos.html', productos=productos)

@app.route('/productos/crear', methods=['POST'])
@login_required
def crear_producto():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    stock = request.form.get('stock')
    
    if not nombre or not precio or not stock:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('listar_productos'))
        
    db.productos.insert_one({
        "nombre": nombre,
        "precio": float(precio),
        "stock": int(stock)
    })
    flash("Producto creado exitosamente.", "success")
    return redirect(url_for('listar_productos'))

@app.route('/productos/editar/<id>', methods=['POST'])
@login_required
def editar_producto(id):
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    stock = request.form.get('stock')
    
    db.productos.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "nombre": nombre,
            "precio": float(precio),
            "stock": int(stock)
        }}
    )
    flash("Producto actualizado.", "success")
    return redirect(url_for('listar_productos'))

@app.route('/productos/eliminar/<id>')
@login_required
def eliminar_producto(id):
    db.productos.delete_one({"_id": ObjectId(id)})
    flash("Producto eliminado.", "warning")
    return redirect(url_for('listar_productos'))

@app.route('/pedidos')
@login_required
def listar_pedidos():
    pedidos_cursor = db.pedidos.find()
    pedidos = []
    
    for ped in pedidos_cursor:
        producto = db.productos.find_one({"_id": ObjectId(ped['producto_id'])})
        ped['producto_nombre'] = producto['nombre'] if producto else "Producto no disponible"
        pedidos.append(ped)
        
    productos = list(db.productos.find())
    return render_template('pedidos.html', pedidos=pedidos, productos=productos)

@app.route('/pedidos/crear', methods=['POST'])
@login_required
def crear_pedido():
    producto_id = request.form.get('producto_id')
    cantidad = request.form.get('cantidad')
    cliente = request.form.get('cliente')
    
    if not producto_id or not cantidad or not cliente:
        flash("Rellene todos los campos del pedido.", "danger")
        return redirect(url_for('listar_pedidos'))

    db.pedidos.insert_one({
        "producto_id": ObjectId(producto_id),
        "cantidad": int(cantidad),
        "cliente": cliente
    })
    flash("Pedido registrado correctamente.", "success")
    return redirect(url_for('listar_pedidos'))

@app.route('/pedidos/editar/<id>', methods=['POST'])
@login_required
def editar_pedido(id):
    producto_id = request.form.get('producto_id')
    cantidad = request.form.get('cantidad')
    cliente = request.form.get('cliente')
    
    db.pedidos.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "producto_id": ObjectId(producto_id),
            "cantidad": int(cantidad),
            "cliente": cliente
        }}
    )
    flash("Pedido modificado.", "success")
    return redirect(url_for('listar_pedidos'))

@app.route('/pedidos/eliminar/<id>')
@login_required
def eliminar_pedido(id):
    db.pedidos.delete_one({"_id": ObjectId(id)})
    flash("Pedido cancelado/eliminado.", "warning")
    return redirect(url_for('listar_pedidos'))

if __name__ == '__main__':
    app.run(debug=True)