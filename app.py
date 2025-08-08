from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import (get_ninos, add_nino, update_nino, delete_nino,
                      get_employees, add_employee, update_employee, delete_employee,
                      get_active_employees_count, get_active_ninos, get_active_employees,
                      add_asistencia, get_today_ninos_total, get_today_payment_per_hour,
                      get_today_ninos_asistencia, get_today_employees_asistencia,
                      get_date_ninos_asistencia, get_date_employees_asistencia, # Estas son las líneas importantes
                      update_asistencia, delete_asistencia, get_week_ninos_unique_count,
                      get_week_ninos_total, get_week_daily_amounts, get_week_employees_earnings)

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
    
    # Obtener el número de empleados activos
    active_employees_count = get_active_employees_count()
    
    # Obtener datos dinámicos para hoy
    today_ninos_total = get_today_ninos_total()
    today_payment_per_hour = get_today_payment_per_hour()
    
    # Obtener datos de la semana actual
    week_ninos_unique_count = get_week_ninos_unique_count()
    week_ninos_total = get_week_ninos_total()
    
    # Obtener datos para el gráfico semanal
    week_daily_amounts = get_week_daily_amounts()
    week_employees_earnings = get_week_employees_earnings()
    
    return render_template('dashboard.html', 
                           active_page='dashboard',
                           active_employees_count=active_employees_count,
                           today_ninos_total=today_ninos_total,
                           today_payment_per_hour=today_payment_per_hour,
                           week_ninos_unique_count=week_ninos_unique_count,
                           week_ninos_total=week_ninos_total,
                           week_daily_amounts=week_daily_amounts,
                           week_employees_earnings=week_employees_earnings)

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
        status = int(data.get('status', 1)) # Por defecto será 1 (activo) si no se proporciona
        result = add_nino(data['nombre'], data['monto'], data['representante'], status)
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
        if not all(key in data for key in ['nombre', 'monto', 'representante', 'status']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        try:
            monto = float(data['monto'])
        except ValueError:
            return jsonify({'error': 'El monto debe ser un número válido'}), 400
            
        result = update_nino(id, data['nombre'], monto, data['representante'], data['status'])
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

@app.route('/employees')
def employees():
    if 'user' not in session:
        return redirect(url_for('login'))
    print("Obteniendo lista de empleados...")
    employees_list = get_employees()
    print(f"Lista de empleados obtenida: {employees_list}")
    return render_template('employees.html', active_page='employees', employees=employees_list)

@app.route('/api/employees', methods=['POST'])
def crear_employee():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        status = int(data.get('status', 1))
        result = add_employee(
            data['nombre'], 
            data['horas'], 
            data['usuario'], 
            data.get('contrasena', ''), # La contraseña es opcional en actualizaciones
            data['nivel'],
            status
        )
        if result:
            return jsonify(result)
        return jsonify({'error': 'Error al crear el registro'}), 500
    except Exception as e:
        print(f"Error al crear empleado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:id>', methods=['PUT'])
def actualizar_employee(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        print(f"Datos recibidos: {data}")
        
        if not all(key in data for key in ['nombre', 'horas', 'usuario', 'nivel', 'status']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
            
        result = update_employee(
            id,
            data['nombre'],
            data['horas'],
            data['usuario'],
            data['nivel'],
            data['status']
        )
        
        if result:
            return jsonify(result)
        return jsonify({'error': 'Error al actualizar el registro'}), 500
    except Exception as e:
        print(f"Error al actualizar empleado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:id>', methods=['DELETE'])
def eliminar_employee(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        result = delete_employee(id)
        if result:
            return jsonify({'success': True})
        return jsonify({'error': 'Error al eliminar el registro'}), 500
    except Exception as e:
        print(f"Error al eliminar empleado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ninos-activos')
def get_ninos_activos():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        ninos = get_active_ninos()
        return jsonify(ninos)
    except Exception as e:
        print(f"Error al obtener niños activos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees-activos')
def get_employees_activos():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        employees = get_active_employees()
        return jsonify(employees)
    except Exception as e:
        print(f"Error al obtener empleados activos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/hoy')
@app.route('/hoy/<date>')
def hoy(date=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Usar datetime.date del import global
    from datetime import date as date_class 
    if date is None:
        # Si no se proporciona fecha, usar hoy
        target_date = date_class.today().isoformat()
    else:
        # Validar que la fecha sea válida
        try:
            target_date = date_class.fromisoformat(date).isoformat()
        except ValueError:
            # Si la fecha no es válida, usar hoy
            target_date = date_class.today().isoformat()
    
    # Obtener datos de asistencia para la fecha especificada
    ninos_asistencia, total_ninos = get_date_ninos_asistencia(target_date)
    employees_asistencia, total_horas = get_date_employees_asistencia(target_date)
    
    # Calcular pago por hora
    pago_por_hora = 0
    if total_horas > 0:
        pago_por_hora = total_ninos / total_horas
    
    # Obtener información del día para el título
    try:
        target_date_obj = date_class.fromisoformat(target_date)
        day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        day_name = day_names[target_date_obj.weekday()]
        formatted_date = target_date_obj.strftime('%d/%m/%Y')
    except:
        day_name = 'Hoy'
        formatted_date = date_class.today().strftime('%d/%m/%Y')
    
    print(f"DEBUG - Fecha objetivo: {target_date}")
    print(f"DEBUG - ninos_asistencia: {ninos_asistencia}")
    print(f"DEBUG - employees_asistencia: {employees_asistencia}")
    print(f"DEBUG - total_ninos: ${total_ninos}")
    print(f"DEBUG - total_horas: {total_horas}")
    print(f"DEBUG - pago_por_hora: ${pago_por_hora}")
    
    return render_template('hoy.html', 
                           active_page='hoy',
                           ninos_asistencia=ninos_asistencia,
                           employees_asistencia=employees_asistencia,
                           total_ninos=total_ninos,
                           total_horas=total_horas,
                           pago_por_hora=pago_por_hora,
                           current_date=target_date,
                           day_name=day_name,
                           formatted_date=formatted_date)

@app.route('/api/asistencia', methods=['POST'])
def crear_asistencia():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        result = add_asistencia(
            data['fecha'],
            data['tipo'],
            data['id_persona'],
            data['valor']
        )
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'error': 'Error al crear el registro de asistencia'}), 500
    except Exception as e:
        print(f"Error al crear asistencia: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/asistencia/<int:id>', methods=['PUT'])
def actualizar_asistencia(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        result = update_asistencia(id, data['valor'])
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'error': 'Error al actualizar el registro de asistencia'}), 500
    except Exception as e:
        print(f"Error al actualizar asistencia: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/asistencia/<int:id>', methods=['DELETE'])
def eliminar_asistencia(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        result = delete_asistencia(id)
        if result:
            return jsonify({'success': True})
        return jsonify({'error': 'Error al eliminar el registro de asistencia'}), 500
    except Exception as e:
        print(f"Error al eliminar asistencia: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

# Para Vercel
app.debug = False
