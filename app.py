from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
from database import (get_ninos, add_nino, update_nino, delete_nino,
                      get_employees, add_employee, update_employee, delete_employee,
                      get_active_employees_count, get_active_ninos, get_active_employees,
                      add_asistencia, get_today_ninos_total, get_today_payment_per_hour,
                      get_date_ninos_asistencia, get_date_employees_asistencia,
                      update_asistencia, delete_asistencia, get_week_ninos_unique_count,
                      get_week_ninos_total, get_week_daily_amounts, get_week_employees_earnings, 
                      get_current_time, add_pago, get_recent_pagos, get_pending_payments, 
                      get_week_gastos, add_gasto, update_gasto, delete_gasto)

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
@app.route('/dashboard/<date>')
def dashboard(date=None):
    if 'user' not in session:
        return redirect(url_for('login'))

    if date:
        try:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            current_date = get_current_time().date()
    else:
        current_date = get_current_time().date()

    # Calcular inicio y fin de la semana (Lunes a Sábado)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=5)

    # Calcular semanas anterior y siguiente
    prev_week_start = start_of_week - timedelta(days=7)
    next_week_start = start_of_week + timedelta(days=7)

    # Formatear fechas para la plantilla
    week_start_str = start_of_week.strftime('%B %d')
    week_end_str = end_of_week.strftime('%B %d')

    # Obtener el número de empleados activos
    active_employees_count = get_active_employees_count()
    
    # Obtener datos dinámicos para hoy
    today_ninos_total = get_today_ninos_total()
    today_payment_per_hour = get_today_payment_per_hour()
    
    # Obtener datos de la semana
    week_ninos_unique_count = get_week_ninos_unique_count(start_of_week, end_of_week)
    week_ninos_total = get_week_ninos_total(start_of_week, end_of_week)
    
    # Obtener datos para el gráfico semanal
    week_daily_amounts = get_week_daily_amounts(start_of_week, end_of_week)
    week_employees_earnings = get_week_employees_earnings(start_of_week, end_of_week)
    
    # Get weekly expenses
    week_gastos_total = get_week_gastos(start_of_week, end_of_week)
    if week_gastos_total is None:
        week_gastos_total = 0

    return render_template('dashboard.html', 
                           week_start_str=start_of_week.strftime('%Y-%m-%d'),
                           week_end_str=end_of_week.strftime('%Y-%m-%d'),
                           prev_week_start_str=prev_week_start.strftime('%Y-%m-%d'),
                           next_week_start_str=next_week_start.strftime('%Y-%m-%d'),
                           today_ninos_total=today_ninos_total,
                           today_payment_per_hour=today_payment_per_hour,
                           week_ninos_unique_count=week_ninos_unique_count,
                           week_ninos_total=week_ninos_total,
                           week_gastos_total=week_gastos_total,
                           active_employees_count=active_employees_count,
                           week_daily_amounts=week_daily_amounts,
                           week_employees_earnings=week_employees_earnings)

@app.route('/gastos')
@app.route('/gastos/<date>')
def gastos(date=None):
    if 'user' not in session:
        return redirect(url_for('login'))

    if date:
        try:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            current_date = get_current_time().date()
    else:
        current_date = get_current_time().date()

    # Calcular inicio y fin de la semana (Lunes a Sábado)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=5)

    # Calcular semanas anterior y siguiente
    prev_week_start = start_of_week - timedelta(days=7)
    next_week_start = start_of_week + timedelta(days=7)

    # Formatear fechas para la plantilla
    week_start_str = start_of_week.strftime('%B %d')
    week_end_str = end_of_week.strftime('%B %d')

    # Obtener gastos de la semana
    gastos, total_gastos = get_week_gastos(start_of_week, end_of_week)
    
    # Debug: Imprimir los gastos
    print("\n=== DEBUG: Datos de gastos ===")
    print(f"Gastos recibidos: {gastos}")
    print(f"Total gastos: {total_gastos}")
    print("===========================\n")

    return render_template('gastos.html', 
                           active_page='gastos',
                           gastos=gastos,
                           total_gastos=total_gastos,
                           week_start_str=week_start_str,
                           week_end_str=week_end_str,
                           prev_week_start_str=prev_week_start.strftime('%Y-%m-%d'),
                           next_week_start_str=next_week_start.strftime('%Y-%m-%d'))

@app.route('/api/gastos', methods=['POST'])
def crear_gasto():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        result = add_gasto(
            data['fecha'],
            data['motivo'],
            data['monto']
        )
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'error': 'Error al crear el gasto'}), 500
    except Exception as e:
        print(f"Error al crear gasto: {e}")
        return jsonify({'error': str(e)}), 500
    try:
        data = request.json
        print(f"\n=== Actualizando gasto {id} ===")
        print(f"Datos recibidos: {data}")
        
        if not all(key in data for key in ['fecha', 'motivo', 'monto']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        try:
            monto = float(data['monto'])
        except ValueError:
            return jsonify({'error': 'El monto debe ser un número válido'}), 400
            
        result = update_gasto(id, data['fecha'], data['motivo'], monto)
        print(f"Resultado de la actualización: {result}")
        
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'error': 'Error al actualizar el gasto'}), 500
    except Exception as e:
        print(f"Error al actualizar gasto: {e}")
        return jsonify({'error': str(e)}), 500

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
        target_date = get_current_time().date().isoformat()
    else:
        # Validar que la fecha sea válida
        try:
            target_date = date_class.fromisoformat(date).isoformat()
        except ValueError:
            # Si la fecha no es válida, usar hoy
            target_date = get_current_time().date().isoformat()
    
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
        formatted_date = get_current_time().date().strftime('%d/%m/%Y')
    
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

@app.route('/pagos')
def pagos():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    recent_pagos = get_recent_pagos(limit=15)
    pending_payments = get_pending_payments()
    
    # Para el modal de agregar pago, necesito la lista de niños y empleados activos
    ninos_activos = get_active_ninos()
    employees_activos = get_active_employees()
    
    return render_template('pagos.html', 
                           active_page='pagos',
                           recent_pagos=recent_pagos,
                           pending_payments=pending_payments,
                           ninos_activos=ninos_activos,
                           employees_activos=employees_activos,
                           get_current_time=get_current_time)

@app.route('/api/pagos', methods=['POST'])
def crear_pago():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        result = add_pago(
            data['fecha'],
            data['id_nino'],
            data['id_empleado'],
            data['monto'],
            data['tipo']
        )
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'error': 'Error al crear el pago'}), 500
    except Exception as e:
        print(f"Error al crear pago: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/asistencia/multiple', methods=['POST'])
def crear_asistencia_multiple():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        fecha = data['fecha']
        ninos = data['ninos']
        
        for nino in ninos:
            add_asistencia(
                fecha,
                'nino',
                nino['id_persona'],
                nino['valor']
            )
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error al crear asistencia múltiple: {e}")
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
        return jsonify({'error': 'Error al eliminar el registro'}), 500
    except Exception as e:
        print(f"Error al eliminar asistencia: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gastos/<int:id>', methods=['PUT'])
def actualizar_gasto(id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.json
        print(f"\n=== Actualizando gasto {id} ===")
        print(f"Datos recibidos: {data}")
        
        if not all(key in data for key in ['fecha', 'motivo', 'monto']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        try:
            monto = float(data['monto'])
        except ValueError:
            return jsonify({'error': 'El monto debe ser un número válido'}), 400
            
        result = update_gasto(id, data['fecha'], data['motivo'], monto)
        print(f"Resultado de la actualización: {result}")
        
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'error': 'Error al actualizar el gasto'}), 500
    except Exception as e:
        print(f"Error al actualizar gasto: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gastos/<int:id>', methods=['DELETE'])
def eliminar_gasto(id):
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    
    if delete_gasto(id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Error al eliminar el gasto'})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

# Para Vercel
app.debug = False
False
False