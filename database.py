# database.py - Archivo completo y corregido (Versión con más Debug)

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta # Asegúrate de que esta línea esté aquí al principio
import pytz

def get_current_time():
    """Returns the current time in 'America/Chicago' timezone."""
    return datetime.now(pytz.timezone('America/Chicago'))

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"URL de Supabase: {supabase_url}")
print(f"Key de Supabase: {supabase_key[:10]}...") # Solo mostramos el inicio de la key por seguridad

# Crear cliente de Supabase
try:
    supabase = create_client(supabase_url, supabase_key)
    print("Cliente de Supabase creado exitosamente")
except Exception as e:
    print(f"Error al crear cliente de Supabase: {e}")

def get_ninos():
    """Obtener todos los niños de la base de datos"""
    try:
        print("\n=== Iniciando obtención de niños ===")
        
        # Consulta simple usando el cliente
        print("\nEjecutando consulta...")
        response = supabase.from_('ninos').select('*').execute()
        print(f"Respuesta completa: {response}")
        
        if hasattr(response, 'data'):
            print(f"Datos obtenidos: {response.data}")
            # Convertir los datos para manejar la columna Representante
            data_converted = []
            for item in response.data:
                converted = {
                    'id': item['id'],
                    'nombre': item['nombre'],
                    'monto': int(float(item.get('monto', 0))),
                    'representante': item.get('Representante', ''),
                    'status': int(item.get('status', 0))
                }
                data_converted.append(converted)
            
            # Ordenar la lista: primero por status (descendente) y luego por nombre
            data_converted.sort(key=lambda x: (-x['status'], x['nombre']))
            
            print(f"Datos convertidos y ordenados: {data_converted}")
            return data_converted
        else:
            print("No se encontraron datos")
            return []
    except Exception as e:
        print(f"\nError al obtener niños: {e}")
        print(f"Tipo de error: {type(e)}")
        
        # Intentar con el método alternativo
        try:
            print("\nIntentando método alternativo...")
            response = supabase.table('ninos').select('*').execute()
            print(f"Respuesta del método alternativo: {response}")
            
            if hasattr(response, 'data'):
                # Usar la misma lógica que en el método principal
                data_converted = []
                for item in response.data:
                    converted = {
                        'id': item['id'],
                        'nombre': item['nombre'],
                        'monto': int(float(item.get('monto', 0))),
                        'representante': item.get('Representante', ''),
                        'status': int(item.get('status', 0))
                    }
                    data_converted.append(converted)
                
                # Ordenar la lista: primero por status (descendente) y luego por nombre
                data_converted.sort(key=lambda x: (-x['status'], x['nombre']))
                return data_converted
            return []
        except Exception as e2:
            print(f"Error en método alternativo: {e2}")
            return []
    except Exception as e: # Este catch es redundante si el anterior ya captura todo
        print(f"Error al obtener niños: {e}")
        print(f"Error completo: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        return []

def add_nino(nombre, monto, representante, status=1):
    """Agregar un nuevo niño a la base de datos"""
    try:
        # Convertir status a número si viene como string
        status = 1 if str(status).lower() in ['1', 'true', 'activo'] else 0
        # Convertir monto a entero
        monto = int(float(monto))
        
        data = {
            "nombre": nombre,
            "monto": monto,
            "Representante": representante, # Nota la R mayúscula
            "status": status # Ahora siempre será 0 o 1
        }
        response = supabase.table('ninos').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al agregar niño: {e}")
        return None

def update_nino(id, nombre, monto, representante, status):
    """Actualizar datos de un niño"""
    try:
        print(f"\n=== Iniciando actualización de niño {id} ===")
        
        # Primero verificamos si el niño existe
        print("Verificando existencia del niño...")
        check = supabase.from_('ninos').select('*').eq('id', id).execute()
        print(f"Resultado de verificación: {check}")
        
        if not check.data:
            print(f"No se encontró el niño con ID {id}")
            return None
        
        # Convertir monto a entero
        monto = int(float(monto))
            
        data = {
            "nombre": nombre,
            "monto": monto,
            "Representante": representante, # Nota la R mayúscula
            "status": status
        }
        print(f"Datos a actualizar: {data}")
        
        response = supabase.from_('ninos').update(data).eq('id', id).execute()
        print(f"Respuesta de Supabase: {response}")
        
        if hasattr(response, 'data') and response.data:
            print(f"Datos actualizados: {response.data[0]}")
            return response.data[0]
        else:
            print("No se recibieron datos en la respuesta")
            print("Intentando verificar si la actualización fue exitosa...")
            
            # Verificar si la actualización fue exitosa consultando el registro
            verify = supabase.from_('ninos').select('*').eq('id', id).execute()
            if verify.data and verify.data[0]:
                print(f"Verificación exitosa, datos actualizados: {verify.data[0]}")
                return verify.data[0]
            
            print("No se pudo verificar la actualización")
            return None
    except Exception as e:
        print(f"Error al actualizar niño: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Error completo: {str(e)}")
        return None

def delete_nino(id):
    """Eliminar un niño de la base de datos"""
    try:
        response = supabase.table('ninos').delete().eq('id', id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar niño: {e}")
        return False

def get_employees():
    """Obtener todos los empleados de la base de datos"""
    try:
        print("\n=== Iniciando obtención de empleados ===")
        
        # Consulta simple usando el cliente
        print("\nEjecutando consulta...")
        response = supabase.from_('employees').select('*').execute()
        print(f"Respuesta completa: {response}")
        
        if hasattr(response, 'data'):
            print(f"Datos obtenidos: {response.data}")
            data_converted = []
            for item in response.data:
                # Imprimir cada item para debug
                print(f"Procesando item: {item}")
                # Convertir todo a minúsculas para manejar posibles diferencias en nombres de columnas
                item_lower = {k.lower(): v for k, v in item.items()}
                converted = {
                    'id': item_lower.get('id'),
                    'nombre': item_lower.get('nombre', ''),
                    'horas': int(float(item_lower.get('horas', 0))),
                    'usuario': item_lower.get('usuario', ''),
                    'nivel': item_lower.get('nivel', 'Regular'),
                    'status': int(item_lower.get('status', 0))
                }
                data_converted.append(converted)
            
            # Ordenar la lista: primero por status (descendente) y luego por nombre
            data_converted.sort(key=lambda x: (-x['status'], x['nombre']))
            
            print(f"Datos convertidos y ordenados: {data_converted}")
            return data_converted
        else:
            print("No se encontraron datos")
            return []
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return []

def add_employee(nombre, horas, usuario, contrasena, nivel, status=1):
    """Agregar un nuevo empleado a la base de datos"""
    try:
        # Validaciones
        if nivel not in ['Admin', 'Regular']:
            raise ValueError("El nivel debe ser 'Admin' o 'Regular'")
        
        # Convertir status a número
        status = 1 if str(status).lower() in ['1', 'true', 'activo'] else 0
        # Convertir horas a entero
        horas = int(float(horas))
        
        data = {
            "nombre": nombre,
            "horas": horas,
            "usuario": usuario,
            "contrasena": contrasena,
            "nivel": nivel,
            "status": status
        }
        response = supabase.table('employees').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al agregar empleado: {e}")
        return None

def update_employee(id, nombre, horas, usuario, nivel, status):
    """Actualizar datos de un empleado"""
    try:
        print(f"\n=== Iniciando actualización de empleado {id} ===")
        
        # Validaciones
        if nivel not in ['Admin', 'Regular']:
            raise ValueError("El nivel debe ser 'Admin' o 'Regular'")
        
        # Convertir horas a entero
        horas = int(float(horas))
        # Convertir status a número
        status = int(status)
            
        data = {
            "nombre": nombre,
            "horas": horas,
            "usuario": usuario,
            "nivel": nivel,
            "status": status
        }
        print(f"Datos a actualizar: {data}")
        
        response = supabase.from_('employees').update(data).eq('id', id).execute()
        print(f"Respuesta de Supabase: {response}")
        
        if hasattr(response, 'data') and response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error al actualizar empleado: {e}")
        return None

def delete_employee(id):
    """Eliminar un empleado de la base de datos"""
    try:
        response = supabase.table('employees').delete().eq('id', id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar empleado: {e}")
        return False

def get_active_employees_count():
    """Obtener el número de empleados activos (status = 1)"""
    try:
        print("\n=== Obteniendo conteo de empleados activos ===")
        
        # Consulta para contar empleados con status = 1
        response = supabase.from_('employees').select('*', count='exact').eq('status', 1).execute()
        print(f"Respuesta de conteo: {response}")
        
        if hasattr(response, 'count'):
            print(f"Número de empleados activos: {response.count}")
            return response.count
        else:
            # Fallback: contar manualmente
            response = supabase.from_('employees').select('*').eq('status', 1).execute()
            if hasattr(response, 'data'):
                count = len(response.data)
                print(f"Número de empleados activos (fallback): {count}")
                return count
            return 0
    except Exception as e:
        print(f"Error al obtener conteo de empleados activos: {e}")
        return 0

def get_active_ninos():
    """Obtener solo los niños activos (status = 1)"""
    try:
        print("\n=== Obteniendo niños activos ===")
        response = supabase.from_('ninos').select('*').eq('status', 1).execute()
        
        if hasattr(response, 'data'):
            data_converted = []
            for item in response.data:
                converted = {
                    'id': item['id'],
                    'nombre': item['nombre'],
                    'monto': int(float(item.get('monto', 0))),
                    'representante': item.get('Representante', ''),
                    'status': int(item.get('status', 0))
                }
                data_converted.append(converted)
            
            # Ordenar por nombre
            data_converted.sort(key=lambda x: x['nombre'])
            return data_converted
        return []
    except Exception as e:
        print(f"Error al obtener niños activos: {e}")
        return []

def get_active_employees():
    """Obtener solo los empleados activos (status = 1)"""
    try:
        print("\n=== Obteniendo empleados activos ===")
        response = supabase.from_('employees').select('*').eq('status', 1).execute()
        
        if hasattr(response, 'data'):
            data_converted = []
            for item in response.data:
                item_lower = {k.lower(): v for k, v in item.items()}
                converted = {
                    'id': item_lower.get('id'),
                    'nombre': item_lower.get('nombre', ''),
                    'horas': int(float(item_lower.get('horas', 0))),
                    'usuario': item_lower.get('usuario', ''),
                    'nivel': item_lower.get('nivel', 'Regular'),
                    'status': int(item_lower.get('status', 0))
                }
                data_converted.append(converted)
            
            # Ordenar por nombre
            data_converted.sort(key=lambda x: x['nombre'])
            return data_converted
        return []
    except Exception as e:
        print(f"Error al obtener empleados activos: {e}")
        return []

def add_asistencia(fecha, tipo, id_persona, valor):
    """Agregar un nuevo registro de asistencia"""
    try:
        print(f"\n=== Agregando asistencia ===")
        print(f"Fecha: {fecha}, Tipo: {tipo}, ID Persona: {id_persona}, Valor: {valor}")
        
        data = {
            "fecha": fecha,
            "tipo": tipo,
            "id_persona": id_persona,
            "valor": valor
        }
        
        response = supabase.table('asistencia').insert(data).execute()
        if response.data:
            print(f"Asistencia agregada exitosamente: {response.data[0]}")
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error al agregar asistencia: {e}")
        return None

def get_today_ninos_total():
    """Obtener la suma total de montos de niños para hoy"""
    try:
        today = get_current_time().date().isoformat() # Usar datetime.now().date()
        
        print(f"\n=== Obteniendo total de niños para hoy ({today}) ===")
        
        response = supabase.from_('asistencia').select('valor').eq('fecha', today).eq('tipo', 'nino').execute()
        
        if hasattr(response, 'data'):
            total = sum(float(item['valor']) for item in response.data)
            print(f"Total de niños para hoy: ${total}")
            return total
        return 0
    except Exception as e:
        print(f"Error al obtener total de niños para hoy: {e}")
        return 0

def get_today_payment_per_hour():
    """Obtener el pago por hora de hoy (total niños / total horas trabajadoras)"""
    try:
        today = get_current_time().date().isoformat() # Usar datetime.now().date()
        
        print(f"\n=== Calculando pago por hora para hoy ({today}) ===")
        
        # Obtener total de niños
        ninos_response = supabase.from_('asistencia').select('valor').eq('fecha', today).eq('tipo', 'nino').execute()
        total_ninos = 0
        if hasattr(ninos_response, 'data'):
            total_ninos = sum(float(item['valor']) for item in ninos_response.data)
        
        # Obtener total de horas trabajadoras
        trabajadoras_response = supabase.from_('asistencia').select('valor').eq('fecha', today).eq('tipo', 'trabajadora').execute()
        total_horas = 0
        if hasattr(trabajadoras_response, 'data'):
            total_horas = sum(float(item['valor']) for item in trabajadoras_response.data)
        
        # Calcular pago por hora
        if total_horas > 0:
            payment_per_hour = total_ninos / total_horas
            print(f"Total niños: ${total_ninos}, Total horas: {total_horas}, Pago por hora: ${payment_per_hour:.2f}")
            return round(payment_per_hour, 2)
        else:
            print("No hay horas registradas para hoy")
            return 0
    except Exception as e:
        print(f"Error al calcular pago por hora: {e}")
        return 0

def get_date_ninos_asistencia(target_date):
    """Obtener asistencia de niños para una fecha específica con información del niño"""
    try:
        print(f"\n=== Obteniendo asistencia de niños para {target_date} ===")
        
        # Primero obtener los registros de asistencia
        response = supabase.from_('asistencia').select('*').eq('fecha', target_date).eq('tipo', 'nino').execute()
        
        if hasattr(response, 'data') and response.data:
            data_converted = []
            total_monto = 0
            for item in response.data:
                # Obtener el nombre del niño usando el id_persona
                try:
                    nino_response = supabase.from_('ninos').select('nombre').eq('id', item['id_persona']).execute()
                    nombre = 'N/A'
                    if hasattr(nino_response, 'data') and nino_response.data:
                        nombre = nino_response.data[0]['nombre']
                    
                    valor = float(item['valor'])
                    total_monto += valor
                    
                    converted = {
                        'id': item['id'],
                        'id_persona': item['id_persona'],
                        'valor': valor,
                        'fecha': item['fecha'],
                        'tipo': item['tipo'],
                        'nombre': nombre
                    }
                    data_converted.append(converted)
                except Exception as e:
                    print(f"Error al obtener nombre del niño {item['id_persona']}: {e}")
                    continue
            
            # Ordenar por nombre
            data_converted.sort(key=lambda x: x['nombre'])
            print(f"Asistencia de niños obtenida: {data_converted}")
            print(f"Total monto niños: ${total_monto}")
            return data_converted, total_monto
        else:
            print(f"No se encontraron registros de asistencia de niños para {target_date}")
            return [], 0
    except Exception as e:
        print(f"Error al obtener asistencia de niños: {e}")
        return [], 0
# DEBUG LINE: get_date_ninos_asistencia function is loaded.

def get_today_ninos_asistencia(): # ESTA ES LA FUNCIÓN QUE SE SUGIRIÓ EN EL ERROR ANTERIOR
    """Obtener asistencia de niños para hoy con información del niño"""
    # Esta función debería estar llamando a get_date_ninos_asistencia con la fecha de hoy
    # Para evitar duplicación de lógica, haremos que llame a la función general
    return get_date_ninos_asistencia(get_current_time().date().isoformat())


def get_date_employees_asistencia(target_date):
    """Obtener asistencia de empleados para una fecha específica con información del empleado"""
    try:
        print(f"\n=== Obteniendo asistencia de empleados para {target_date} ===")
        
        # Primero obtener los registros de asistencia
        response = supabase.from_('asistencia').select('*').eq('fecha', target_date).eq('tipo', 'trabajadora').execute()
        
        if hasattr(response, 'data') and response.data:
            data_converted = []
            total_horas = 0
            for item in response.data:
                # Obtener el nombre del empleado usando el id_persona
                try:
                    employee_response = supabase.from_('employees').select('nombre').eq('id', item['id_persona']).execute()
                    nombre = 'N/A'
                    if hasattr(employee_response, 'data') and employee_response.data:
                        nombre = employee_response.data[0]['nombre']
                    
                    valor = float(item['valor'])
                    total_horas += valor
                    
                    converted = {
                        'id': item['id'],
                        'id_persona': item['id_persona'],
                        'valor': valor,
                        'fecha': item['fecha'],
                        'tipo': item['tipo'],
                        'nombre': nombre
                    }
                    data_converted.append(converted)
                except Exception as e:
                    print(f"Error al obtener nombre del empleado {item['id_persona']}: {e}")
                    continue
            
            # Ordenar por nombre
            data_converted.sort(key=lambda x: x['nombre'])
            print(f"Asistencia de empleados obtenida: {data_converted}")
            print(f"Total horas empleados: {total_horas}")
            return data_converted, total_horas
        else:
            print(f"No se encontraron registros de asistencia de empleados para {target_date}")
            return [], 0
    except Exception as e:
        print(f"Error al obtener asistencia de empleados: {e}")
        return [], 0

def get_today_employees_asistencia(): # ESTA ES LA FUNCIÓN QUE SE SUGIRIÓ EN EL ERROR ANTERIOR
    """Obtener asistencia de empleados para hoy con información del empleado"""
    # Esta función debería estar llamando a get_date_employees_asistencia con la fecha de hoy
    # Para evitar duplicación de lógica, haremos que llame a la función general
    return get_date_employees_asistencia(get_current_time().date().isoformat())

def update_asistencia(id, valor):
    """Actualizar el valor de un registro de asistencia"""
    try:
        print(f"\n=== Actualizando asistencia {id} ===")
        print(f"Nuevo valor: {valor}")
        
        data = {
            "valor": valor
        }
        
        response = supabase.from_('asistencia').update(data).eq('id', id).execute()
        
        if hasattr(response, 'data') and response.data:
            print(f"Asistencia actualizada exitosamente: {response.data[0]}")
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error al actualizar asistencia: {e}")
        return None

def delete_asistencia(id):
    """Eliminar un registro de asistencia"""
    try:
        print(f"\n=== Eliminando asistencia {id} ===")
        
        response = supabase.from_('asistencia').delete().eq('id', id).execute()
        
        print(f"Asistencia eliminada exitosamente")
        return True
    except Exception as e:
        print(f"Error al eliminar asistencia: {e}")
        return False

def get_week_ninos_unique_count():
    """Obtener el número de niños únicos que han asistido en la semana actual"""
    try:
        #today = date.today() # Eliminada
        today = get_current_time().date()
        
        # Calcular el inicio de la semana (lunes)
        # weekday() devuelve 0=lunes, 1=martes, ..., 6=domingo
        days_since_monday = today.weekday()
        start_of_week = today - timedelta(days=days_since_monday)
        
        print(f"\n=== Obteniendo niños únicos de la semana ===")
        print(f"Fecha actual: {today}")
        print(f"Inicio de semana (lunes): {start_of_week}")
        
        # Obtener todos los registros de asistencia de niños desde el lunes hasta hoy
        response = supabase.from_('asistencia').select('id_persona').eq('tipo', 'nino').gte('fecha', start_of_week.isoformat()).lte('fecha', today.isoformat()).execute()
        
        if hasattr(response, 'data') and response.data:
            # Obtener IDs únicos de niños
            unique_ninos_ids = set()
            for item in response.data:
                unique_ninos_ids.add(item['id_persona'])
            
            count = len(unique_ninos_ids)
            print(f"Niños únicos en la semana: {count}")
            print(f"IDs únicos: {unique_ninos_ids}")
            return count
        else:
            print("No se encontraron registros de asistencia de niños en la semana")
            return 0
    except Exception as e:
        print(f"Error al obtener conteo de niños únicos de la semana: {e}")
        return 0

def get_week_ninos_total():
    """Obtener la suma total de montos de niños para la semana actual"""
    try:
        #today = date.today() # Eliminada
        today = get_current_time().date()
        
        # Calcular el inicio de la semana (lunes)
        days_since_monday = today.weekday()
        start_of_week = today - timedelta(days=days_since_monday)
        
        print(f"\n=== Obteniendo total de niños de la semana ===")
        print(f"Fecha actual: {today}")
        print(f"Inicio de semana (lunes): {start_of_week}")
        
        # Obtener todos los registros de asistencia de niños desde el lunes hasta hoy
        response = supabase.from_('asistencia').select('valor').eq('tipo', 'nino').gte('fecha', start_of_week.isoformat()).lte('fecha', today.isoformat()).execute()
        
        if hasattr(response, 'data') and response.data:
            total = sum(float(item['valor']) for item in response.data)
            print(f"Total de niños de la semana: ${total}")
            return total
        else:
            print("No se encontraron registros de asistencia de niños en la semana")
            return 0
    except Exception as e:
        print(f"Error al obtener total de niños de la semana: {e}")
        return 0


def get_week_daily_amounts():
    """Obtener los montos diarios de la semana actual (lunes a domingo) de manera eficiente.
    Esto incluye los nombres de niños y trabajadoras que asistieron ese día.
    """
    try:
        today = get_current_time().date()
        # weekday() devuelve 0 para lunes, 6 para domingo.
        # Restamos los días desde el lunes para obtener el inicio de la semana actual.
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week_query = start_of_week + timedelta(days=6) # Rango hasta el domingo

        print(f"\n--- DEBUG get_week_daily_amounts ---")
        print(f"Fecha actual: {today.isoformat()}")
        print(f"Inicio de semana (Lunes): {start_of_week.isoformat()}")
        print(f"Fin de semana para consulta (Domingo): {end_of_week_query.isoformat()}")

        # Crear una estructura para los 7 días de la semana, inicializando los montos a 0
        # y las listas de nombres vacías.
        week_data = {
            (start_of_week + timedelta(days=i)).isoformat(): {
                'day': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][i],
                'date': (start_of_week + timedelta(days=i)).isoformat(), # Añadir la fecha aquí también
                'amount': 0,
                'ninos': [],
                'trabajadoras': []
            }
            for i in range(7)
        }
        print(f"Estructura week_data inicializada: {week_data}")

        # 1. Obtener todos los registros de asistencia de niños para la semana en una sola consulta.
        # El rango de fechas va desde el lunes de la semana actual hasta el domingo de la semana actual.
        ninos_asistencia_response = supabase.from_('asistencia').select('fecha, valor, id_persona').eq('tipo', 'nino').gte('fecha', start_of_week.isoformat()).lte('fecha', end_of_week_query.isoformat()).execute()
        
        print(f"Respuesta cruda de asistencia de niños: {ninos_asistencia_response}")

        # 2. Obtener los nombres de todos los niños que asistieron en la semana en una sola consulta.
        nino_names_map = {}
        if hasattr(ninos_asistencia_response, 'data') and ninos_asistencia_response.data:
            nino_ids = list(set(item['id_persona'] for item in ninos_asistencia_response.data)) # Obtener IDs únicos
            print(f"IDs de niños con asistencia esta semana: {nino_ids}")
            if nino_ids: # Solo consultar si hay IDs
                ninos_data_response = supabase.from_('ninos').select('id, nombre').in_('id', nino_ids).execute()
                if hasattr(ninos_data_response, 'data'):
                    nino_names_map = {item['id']: item['nombre'] for item in ninos_data_response.data}
                    print(f"Mapa de nombres de niños: {nino_names_map}")
            
            # Procesar los datos de asistencia de niños y agregarlos a week_data
            for item in ninos_asistencia_response.data:
                fecha = item['fecha']
                valor = float(item['valor'])
                id_persona = item['id_persona']
                
                print(f"Procesando asistencia de niño: Fecha={fecha}, Valor={valor}, ID_Persona={id_persona}")
                
                if fecha in week_data:
                    week_data[fecha]['amount'] += valor
                    # Añadir nombre del niño si existe, si no, 'Desconocido'
                    week_data[fecha]['ninos'].append(nino_names_map.get(id_persona, 'Desconocido'))

        # 3. Obtener todos los registros de asistencia de trabajadoras para la semana en una sola consulta.
        employees_asistencia_response = supabase.from_('asistencia').select('fecha, id_persona').eq('tipo', 'trabajadora').gte('fecha', start_of_week.isoformat()).lte('fecha', end_of_week_query.isoformat()).execute()
        
        print(f"Respuesta cruda de asistencia de trabajadoras: {employees_asistencia_response}")

        # 4. Obtener los nombres de todas las trabajadoras que asistieron en la semana en una sola consulta.
        employee_names_map = {}
        if hasattr(employees_asistencia_response, 'data') and employees_asistencia_response.data:
            employee_ids = list(set(item['id_persona'] for item in employees_asistencia_response.data)) # Obtener IDs únicos
            print(f"IDs de trabajadoras con asistencia esta semana: {employee_ids}")
            if employee_ids: # Solo consultar si hay IDs
                employees_data_response = supabase.from_('employees').select('id, nombre').in_('id', employee_ids).execute()
                if hasattr(employees_data_response, 'data'):
                    employee_names_map = {item['id']: item['nombre'] for item in employees_data_response.data}
                    print(f"Mapa de nombres de trabajadoras: {employee_names_map}")
            
            # Procesar los datos de asistencia de trabajadoras y agregarlos a week_data
            for item in employees_asistencia_response.data:
                fecha = item['fecha']
                id_persona = item['id_persona']
                
                print(f"Procesando asistencia de trabajadora: Fecha={fecha}, ID_Persona={id_persona}")
                
                if fecha in week_data:
                    # Añadir nombre de la trabajadora si existe
                    week_data[fecha]['trabajadoras'].append(employee_names_map.get(id_persona, 'Desconocido'))

        # 5. Convertir el diccionario de datos semanales en una lista ordenada por fecha para el frontend
        daily_amounts = sorted(list(week_data.values()), key=lambda x: x['date'])
        
        print(f"DEBUG: Datos finales enviados al gráfico: {daily_amounts}")
        print(f"--- FIN DEBUG get_week_daily_amounts ---")
        return daily_amounts

    except Exception as e:
        print(f"ERROR: Fallo en get_week_daily_amounts: {e}")
        return []

def get_week_employees_earnings():
    """Obtener los montos de ganancias de empleados de la semana actual (lunes a domingo)."""
    try:
        today = get_current_time().date()
        days_since_monday = today.weekday()
        start_of_week = today - timedelta(days=days_since_monday)
        end_of_week = start_of_week + timedelta(days=6) # Domingo

        print(f"\n--- DEBUG get_week_employees_earnings ---")
        print(f"Fecha actual: {today.isoformat()}")
        print(f"Inicio de semana (Lunes): {start_of_week.isoformat()}")
        print(f"Fin de semana para consulta (Domingo): {end_of_week.isoformat()}")

        # 1. Obtener todos los registros de asistencia (niños y trabajadoras) de la semana en una sola consulta.
        asistencia_response = supabase.from_('asistencia').select('fecha, tipo, valor, id_persona').gte('fecha', start_of_week.isoformat()).lte('fecha', end_of_week.isoformat()).execute()
        
        if not (hasattr(asistencia_response, 'data') and asistencia_response.data):
            print("DEBUG: No se encontraron registros de asistencia para la semana en get_week_employees_earnings.")
            return []

        print(f"DEBUG: Registros de asistencia obtenidos para ganancias de empleados: {asistencia_response.data}")

        # 2. Calcular el total de montos de niños y horas de trabajadoras por día
        daily_summary = {}
        for item in asistencia_response.data:
            fecha = item['fecha']
            tipo = item['tipo']
            valor = float(item['valor'])
            
            if fecha not in daily_summary:
                daily_summary[fecha] = {'total_ninos_monto': 0, 'total_empleados_horas': 0}
            
            if tipo == 'nino':
                daily_summary[fecha]['total_ninos_monto'] += valor
            elif tipo == 'trabajadora':
                daily_summary[fecha]['total_empleados_horas'] += valor
        
        print(f"DEBUG: Resumen diario de montos/horas: {daily_summary}")

        # 3. Calcular el pago por hora para cada día
        daily_payment_per_hour = {}
        for fecha, data in daily_summary.items():
            pago_por_hora = 0
            if data['total_empleados_horas'] > 0:
                pago_por_hora = data['total_ninos_monto'] / data['total_empleados_horas']
            daily_payment_per_hour[fecha] = pago_por_hora
        print(f"DEBUG: Pago por hora diario: {daily_payment_per_hour}")

        # 4. Calcular las ganancias de cada empleado
        employee_earnings = {}
        employee_ids_in_week = set()

        for item in asistencia_response.data:
            if item['tipo'] == 'trabajadora':
                fecha = item['fecha']
                id_persona = item['id_persona']
                horas_trabajadas = float(item['valor'])
                
                pago_por_hora_del_dia = daily_payment_per_hour.get(fecha, 0)
                ganancia_diaria = horas_trabajadas * pago_por_hora_del_dia

                if id_persona not in employee_earnings:
                    employee_earnings[id_persona] = {'total_ganancia': 0, 'total_horas': 0, 'dias_trabajados': set()}
                
                employee_earnings[id_persona]['total_ganancia'] += ganancia_diaria
                employee_earnings[id_persona]['total_horas'] += horas_trabajadas
                employee_earnings[id_persona]['dias_trabajados'].add(fecha)
                employee_ids_in_week.add(id_persona)
        
        print(f"DEBUG: Ganancias de empleados calculadas (por ID): {employee_earnings}")
        print(f"DEBUG: IDs de empleados con ganancias esta semana: {employee_ids_in_week}")


        # 5. Obtener los nombres de todos los empleados relevantes en una sola consulta
        employee_names_map = {}
        if employee_ids_in_week:
            employees_data_response = supabase.from_('employees').select('id, nombre').in_('id', list(employee_ids_in_week)).execute()
            if hasattr(employees_data_response, 'data'):
                employee_names_map = {item['id']: item['nombre'] for item in employees_data_response.data}
        print(f"DEBUG: Mapa de nombres de empleados: {employee_names_map}")
        
        # 6. Formatear la salida para el frontend
        final_earnings = []
        for id_persona, data in employee_earnings.items():
            nombre = employee_names_map.get(id_persona, 'Nombre no encontrado')
            final_earnings.append({
                'nombre': nombre,
                'total_horas': data['total_horas'],
                'total_ganancia': data['total_ganancia'],
                'dias_trabajados': len(data['dias_trabajados']) # Contar días únicos trabajados
            })

        # Opcional: Ordenar las ganancias finales si lo necesitas
        final_earnings.sort(key=lambda x: x['total_ganancia'], reverse=True)
        
        print(f"DEBUG: Ganancias finales de empleados para el frontend: {final_earnings}")
        print(f"--- FIN DEBUG get_week_employees_earnings ---")
        return final_earnings

    except Exception as e:
        print(f"ERROR: Fallo en get_week_employees_earnings: {e}")
        return []
