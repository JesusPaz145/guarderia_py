
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import get_ninos, add_nino, update_nino, delete_nino

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', active_page='dashboard')

@app.route('/ninos')
def ninos():
    if 'user' not in session:
        return redirect(url_for('login'))
    print("Obteniendo lista de niños...")
    ninos_list = get_ninos()
    print(f"Lista de niños obtenida: {ninos_list}")
    return render_template('ninos.html', active_page='ninos', ninos=ninos_list)

@app.route('/api/ninos', methods=['POST'])
def crear_nino():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        result = add_nino(data['nombre'], data['monto'], data['representante'])
        if result:
            return jsonify(result)
        return jsonify({'error': 'Error al crear el registro'}), 500
    except Exception as e:
        print(f"Error al crear niño: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ninos/<int:id>', methods=['PUT'])
def actualizar_nino(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        print(f"\n=== Procesando actualización para niño {id} ===")
        data = request.json
        print(f"Datos recibidos: {data}")
        
        # Validar datos
        if not all(key in data for key in ['nombre', 'monto', 'representante']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        try:
            monto = float(data['monto'])
        except ValueError:
            return jsonify({'error': 'El monto debe ser un número válido'}), 400
            
        result = update_nino(id, data['nombre'], monto, data['representante'])
        print(f"Resultado de la actualización: {result}")
        
        if result:
            return jsonify(result)
        return jsonify({'error': 'Error al actualizar el registro. Por favor, verifica los datos.'}), 500
    except Exception as e:
        print(f"Error al actualizar niño: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Error completo: {str(e)}")
        return jsonify({'error': f'Error del servidor: {str(e)}'}), 500

@app.route('/api/ninos/<int:id>', methods=['DELETE'])
def eliminar_nino(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        result = delete_nino(id)
        if result:
            return jsonify({'success': True})
        return jsonify({'error': 'Error al eliminar el registro'}), 500
    except Exception as e:
        print(f"Error al eliminar niño: {e}")
        return jsonify({'error': str(e)}), 500
    return render_template('ninos.html', active_page='ninos')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
