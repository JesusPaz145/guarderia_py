# database.py - Archivo completo y corregido (Versión con más Debug)

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta # Asegúrate de que esta línea esté aquí al principio
import pytz

def get_current_time():
    """Returns the current time in 'America/Chicago' timezone."""
    utc_now = datetime.now(pytz.UTC)
    local_tz = pytz.timezone('America/Chicago')
    return utc_now.astimezone(local_tz)

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

def verify_employee_credentials(usuario, contrasena):
    """Verificar credenciales del empleado y retornar sus datos si son válidos"""
    try:
        print(f"\n=== Verificando credenciales para usuario: {usuario} ===")
        response = supabase.from_('employees').select('*').eq('usuario', usuario).eq('contrasena', contrasena).eq('status', 1).execute()
        
        if hasattr(response, 'data') and len(response.data) > 0:
            employee = response.data[0]
            return {
                'id': employee['id'],
                'nombre': employee['nombre'],
                'nivel': employee['nivel'],
                'status': employee['status']
            }
        return None
    except Exception as e:
        print(f"Error al verificar credenciales: {e}")
        return None

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

def get_week_ninos_unique_count(start_date, end_date):
    """Obtener el número de niños únicos en un rango de fechas"""
    try:
        print(f"\n=== Obteniendo niños únicos del período ===")
        print(f"Fecha inicio: {start_date}")
        print(f"Fecha fin: {end_date}")
        
        # Obtener todos los registros de asistencia de niños para el período especificado
        response = supabase.from_('asistencia').select('id_persona').eq('tipo', 'nino').gte('fecha', start_date.isoformat()).lte('fecha', end_date.isoformat()).execute()
        
        if hasattr(response, 'data') and response.data:
            # Obtener IDs únicos de niños
            unique_ninos_ids = set()
            for item in response.data:
                unique_ninos_ids.add(item['id_persona'])
            
            count = len(unique_ninos_ids)
            print(f"Niños únicos en el período: {count}")
            print(f"IDs únicos: {unique_ninos_ids}")
            return count
        else:
            print("No se encontraron registros de asistencia de niños en el período especificado")
            return 0
    except Exception as e:
        print(f"Error al obtener conteo de niños únicos del período: {e}")
        return 0

def get_week_ninos_total(start_date, end_date):
    """Obtener la suma total de montos de niños para un rango de fechas específico"""
    try:
        print(f"\n=== Obteniendo total de niños del período ===")
        print(f"Fecha inicio: {start_date}")
        print(f"Fecha fin: {end_date}")
        
        # Obtener todos los registros de asistencia de niños para el período especificado
        response = supabase.from_('asistencia').select('valor').eq('tipo', 'nino').gte('fecha', start_date.isoformat()).lte('fecha', end_date.isoformat()).execute()
        
        if hasattr(response, 'data') and response.data:
            total = sum(float(item['valor']) for item in response.data)
            print(f"Total de niños del período: ${total}")
            return total
        else:
            print("No se encontraron registros de asistencia de niños en la semana")
            return 0
    except Exception as e:
        print(f"Error al obtener total de niños del período: {e}")
        return 0


def get_week_daily_amounts(start_date, end_date):
    """Obtener los montos diarios para un rango de fechas específico.
    Esto incluye los nombres de niños y trabajadoras que asistieron cada día.
    """
    try:
        print(f"\n--- DEBUG get_week_daily_amounts ---")
        print(f"Fecha inicio: {start_date.isoformat()}")
        print(f"Fecha fin: {end_date.isoformat()}")

        # Calcular el número de días en el rango
        days_range = (end_date - start_date).days + 1
        
        # Crear una estructura para los días en el rango, inicializando los montos a 0
        # y las listas de nombres vacías.
        week_data = {
            (start_date + timedelta(days=i)).isoformat(): {
                'day': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][(start_date + timedelta(days=i)).weekday()],
                'date': (start_date + timedelta(days=i)).isoformat(),
                'amount': 0,
                'ninos': [],
                'trabajadoras': []
            }
            for i in range(days_range)
        }
        print(f"Estructura week_data inicializada: {week_data}")

        # 1. Obtener todos los registros de asistencia de niños para la semana en una sola consulta.
        # Obtener asistencia de niños para el rango de fechas especificado
        ninos_asistencia_response = supabase.from_('asistencia').select('fecha, valor, id_persona').eq('tipo', 'nino').gte('fecha', start_date.isoformat()).lte('fecha', end_date.isoformat()).execute()
        
        print(f"Respuesta cruda de asistencia de niños: {ninos_asistencia_response}")

        # 2. Obtener los nombres de todos los niños que asistieron en el período
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

        # 3. Obtener todos los registros de asistencia de trabajadoras para el período especificado
        employees_asistencia_response = supabase.from_('asistencia').select('fecha, id_persona').eq('tipo', 'trabajadora').gte('fecha', start_date.isoformat()).lte('fecha', end_date.isoformat()).execute()
        
        print(f"Respuesta cruda de asistencia de trabajadoras: {employees_asistencia_response}")

        # 4. Obtener los nombres de todas las trabajadoras que asistieron en el período
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

def get_week_employees_earnings(start_of_week, end_of_week):
    """Obtener los montos de ganancias de empleados de la semana especificada."""
    try:
        print(f"\n--- DEBUG get_week_employees_earnings ---")
        print(f"Inicio de semana: {start_of_week.isoformat()}")
        print(f"Fin de semana: {end_of_week.isoformat()}")

        # Obtener asistencias
        asistencia_response = supabase.from_('asistencia').select('fecha, tipo, valor, id_persona').gte('fecha', start_of_week.isoformat()).lte('fecha', end_of_week.isoformat()).execute()
        
        if not (hasattr(asistencia_response, 'data') and asistencia_response.data):
            return []

        # Obtener gastos diarios
        gastos_response = supabase.from_('gastos').select('fecha, monto').gte('fecha', start_of_week.isoformat()).lte('fecha', end_of_week.isoformat()).execute()
        
        # Inicializar diccionario de gastos diarios
        daily_gastos = {}
        if hasattr(gastos_response, 'data'):
            for gasto in gastos_response.data:
                fecha = gasto['fecha']
                if fecha not in daily_gastos:
                    daily_gastos[fecha] = 0
                daily_gastos[fecha] += float(gasto.get('monto', 0))

        # Procesar asistencias diarias
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
        
        # Calcular pago por hora teniendo en cuenta los gastos
        daily_payment_per_hour = {}
        for fecha, data in daily_summary.items():
            pago_por_hora = 0
            if data['total_empleados_horas'] > 0:
                # Restar los gastos del día (si existen) del monto total
                gastos_del_dia = daily_gastos.get(fecha, 0)
                ingreso_neto = data['total_ninos_monto'] - gastos_del_dia
                if ingreso_neto > 0:  # Solo si hay ganancia después de gastos
                    pago_por_hora = ingreso_neto / data['total_empleados_horas']
            daily_payment_per_hour[fecha] = pago_por_hora
            print(f"DEBUG - Fecha: {fecha}, Monto: {data['total_ninos_monto']}, Gastos: {daily_gastos.get(fecha, 0)}, Horas: {data['total_empleados_horas']}, Pago/hora: {pago_por_hora}")

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
        
        employee_names_map = {}
        if employee_ids_in_week:
            employees_data_response = supabase.from_('employees').select('id, nombre').in_('id', list(employee_ids_in_week)).execute()
            if hasattr(employees_data_response, 'data'):
                employee_names_map = {item['id']: item['nombre'] for item in employees_data_response.data}
        
        final_earnings = []
        for id_persona, data in employee_earnings.items():
            nombre = employee_names_map.get(id_persona, 'Nombre no encontrado')
            final_earnings.append({
                'nombre': nombre,
                'total_horas': data['total_horas'],
                'total_ganancia': data['total_ganancia'],
                'dias_trabajados': len(data['dias_trabajados'])
            })

        final_earnings.sort(key=lambda x: x['total_ganancia'], reverse=True)
        
        print(f"DEBUG: Ganancias finales de empleados para el frontend: {final_earnings}")
        return final_earnings

    except Exception as e:
        print(f"ERROR: Fallo en get_week_employees_earnings: {e}")
        return []

def add_pago(fecha, id_nino, id_empleado, monto, tipo):
    """Agregar un nuevo pago a la base de datos."""
    try:
        data = {
            "date": fecha,
            "id_nino": id_nino,
            "id_empleado": id_empleado,
            "monto": float(monto),
            "tipo": tipo  # 'Efectivo' o 'Zelle'
        }
        
        response = supabase.table('pagos').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al agregar pago: {e}")
        return None

def get_recent_pagos(limit=10):
    """Obtener los pagos más recientes."""
    try:
        print("\n--- DEBUG: Iniciando get_recent_pagos ---")
        query = '*, ninos(nombre), employees(nombre)'
        print(f"Ejecutando consulta: .from_('pagos').select('{query}')")
        
        response = supabase.from_('pagos').select(query).order('date', desc=True).order('id', desc=True).limit(limit).execute()
        
        print(f"Respuesta cruda de Supabase: {response}")
        
        if hasattr(response, 'data'):
            print(f"Datos recibidos: {response.data}")
            if not response.data:
                print("La consulta no devolvió datos.")
                return []

            pagos = []
            print("Procesando registros...")
            for i, item in enumerate(response.data):
                print(f"  Item {i}: {item}")
                
                nombre_nino = 'No encontrado'
                if item.get('ninos'):
                    if isinstance(item['ninos'], dict):
                        nombre_nino = item['ninos'].get('nombre', 'Nombre Ausente')
                    else:
                        print(f"  Advertencia: 'ninos' no es un diccionario: {item['ninos']}")
                else:
                    print("  Advertencia: No se encontró la clave 'ninos' en el item.")

                nombre_empleada = 'No encontrada'
                if item.get('employees'):
                    if isinstance(item['employees'], dict):
                        nombre_empleada = item['employees'].get('nombre', 'Nombre Ausente')
                    else:
                        print(f"  Advertencia: 'employees' no es un diccionario: {item['employees']}")
                else:
                    print("  Advertencia: No se encontró la clave 'employees' en el item.")

                pago_procesado = {
                    'id': item.get('id', 'N/A'),
                    'date': item.get('date', 'N/A'),
                    'monto': float(item.get('monto', 0)),
                    'tipo': item.get('tipo', 'N/A'),
                    'nombre_nino': nombre_nino,
                    'nombre_empleada': nombre_empleada
                }
                print(f"  Pago procesado {i}: {pago_procesado}")
                pagos.append(pago_procesado)
            
            print(f"--- DEBUG: Finalizando get_recent_pagos. Total de pagos procesados: {len(pagos)} ---")
            return pagos
        else:
            print("El objeto de respuesta de Supabase no tiene el atributo 'data'.")
            return []
    except Exception as e:
        print(f"ERROR CATASTRÓFICO en get_recent_pagos: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_pending_payments():
    """Calcula los saldos pendientes de todos los niños."""
    try:
        # 1. Obtener todos los niños activos
        ninos_response = supabase.from_('ninos').select('id, nombre, status').eq('status', 1).execute()
        if not (hasattr(ninos_response, 'data') and ninos_response.data):
            return []
        
        ninos = ninos_response.data
        nino_ids = [nino['id'] for nino in ninos]

        # 2. Obtener el total de asistencia para todos los niños activos en una consulta
        asistencia_response = supabase.from_('asistencia').select('id_persona, valor').eq('tipo', 'nino').in_('id_persona', nino_ids).execute()
        
        total_asistencia = {}
        if hasattr(asistencia_response, 'data'):
            for record in asistencia_response.data:
                nino_id = record['id_persona']
                total_asistencia[nino_id] = total_asistencia.get(nino_id, 0) + float(record['valor'])

        # 3. Obtener el total de pagos para todos los niños activos en una consulta
        pagos_response = supabase.from_('pagos').select('id_nino, monto').in_('id_nino', nino_ids).execute()
        
        total_pagos = {}
        if hasattr(pagos_response, 'data'):
            for record in pagos_response.data:
                nino_id = record['id_nino']
                total_pagos[nino_id] = total_pagos.get(nino_id, 0) + float(record['monto'])

        # 4. Calcular saldos pendientes
        pending_payments = []
        for nino in ninos:
            nino_id = nino['id']
            deuda = total_asistencia.get(nino_id, 0)
            pagado = total_pagos.get(nino_id, 0)
            saldo = deuda - pagado
            
            # Solo mostrar niños con deuda o que han asistido/pagado algo
            if deuda > 0 or pagado > 0:
                pending_payments.append({
                    'id_nino': nino_id,
                    'nombre': nino['nombre'],
                    'total_deuda': deuda,
                    'total_pagado': pagado,
                    'saldo_pendiente': saldo
                })
        
        # Ordenar por saldo pendiente (de mayor a menor deuda)
        pending_payments.sort(key=lambda x: x['saldo_pendiente'], reverse=True)
        
        return pending_payments

    except Exception as e:
        print(f"Error al obtener pagos pendientes: {e}")
        return []

def get_week_gastos(start_date, end_date):
    """Obtener todos los gastos de la semana"""
    try:
        print(f"\n=== Obteniendo gastos de la semana: {start_date} a {end_date} ===")
        response = supabase.from_('gastos').select('*').gte('fecha', start_date.isoformat()).lte('fecha', end_date.isoformat()).order('fecha', desc=True).execute()
        
        if hasattr(response, 'data'):
            gastos_converted = []
            total_gastos = 0
            
            for gasto in response.data:
                monto = float(gasto.get('monto', 0))
                total_gastos += monto
                
                converted = {
                    'id': gasto.get('id'),
                    'fecha': gasto.get('fecha'),
                    'motivo': gasto.get('motivo', ''),
                    'monto': monto
                }
                gastos_converted.append(converted)
            
            print(f"Total gastos de la semana: ${total_gastos}")
            return gastos_converted, total_gastos
            
        return [], 0
        return 0
    except Exception as e:
        print(f"Error al obtener gastos de la semana: {e}")
        return 0
            


        return [], 0
    except Exception as e:
        print(f"Error al obtener gastos de la semana: {e}")
        return [], 0

def add_gasto(fecha, motivo, monto):
    """Agregar un nuevo gasto a la base de datos."""
    try:
        data = {
            "fecha": fecha,
            "motivo": motivo,
            "monto": float(monto)
        }
        response = supabase.table('gastos').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al agregar gasto: {e}")
        return None

def update_gasto(id, fecha, motivo, monto):
    """Actualizar un gasto existente"""
    try:
        print(f"\n=== Actualizando gasto {id} ===")
        data = {
            "fecha": fecha,
            "motivo": motivo,
            "monto": float(monto)
        }
        response = supabase.from_('gastos').update(data).eq('id', id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al actualizar gasto: {e}")
        return None

def delete_gasto(id):
    """Eliminar un gasto"""
    try:
        print(f"\n=== Eliminando gasto {id} ===")
        response = supabase.from_('gastos').delete().eq('id', id).execute()
        return True
    except Exception as e:
        print(f"Error al eliminar gasto: {e}")
        return False
