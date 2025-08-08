from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"URL de Supabase: {supabase_url}")
print(f"Key de Supabase: {supabase_key[:10]}...")  # Solo mostramos el inicio de la key por seguridad

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
    except Exception as e:
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
            "Representante": representante,  # Nota la R mayúscula
            "status": status  # Ahora siempre será 0 o 1
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
            "Representante": representante,  # Nota la R mayúscula
            "status": status
        }
        print(f"Datos a actualizar: {data}")
        
        # Intentar actualización usando from_ en lugar de table
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
        from datetime import date
        today = date.today().isoformat()
        
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
        from datetime import date
        today = date.today().isoformat()
        
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

def get_today_ninos_asistencia():
    """Obtener asistencia de niños para hoy con información del niño"""
    try:
        from datetime import date
        today = date.today().isoformat()
        
        print(f"\n=== Obteniendo asistencia de niños para hoy ({today}) ===")
        
        # Primero obtener los registros de asistencia
        response = supabase.from_('asistencia').select('*').eq('fecha', today).eq('tipo', 'nino').execute()
        
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
            print("No se encontraron registros de asistencia de niños para hoy")
            return [], 0
    except Exception as e:
        print(f"Error al obtener asistencia de niños: {e}")
        return [], 0

def get_today_employees_asistencia():
    """Obtener asistencia de empleados para hoy con información del empleado"""
    try:
        from datetime import date
        today = date.today().isoformat()
        
        print(f"\n=== Obteniendo asistencia de empleados para hoy ({today}) ===")
        
        # Primero obtener los registros de asistencia
        response = supabase.from_('asistencia').select('*').eq('fecha', today).eq('tipo', 'trabajadora').execute()
        
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
            print("No se encontraron registros de asistencia de empleados para hoy")
            return [], 0
    except Exception as e:
        print(f"Error al obtener asistencia de empleados: {e}")
        return [], 0

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
