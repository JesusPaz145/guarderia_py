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
        print(f"URL de Supabase: {supabase_url}")
        
        # Consulta simple usando el cliente
        print("\nEjecutando consulta...")
        response = supabase.from_('ninos').select('id,nombre,monto,"Representante"').execute()
        print(f"Respuesta completa: {response}")
        
        if hasattr(response, 'data'):
            # Convertir los datos para manejar la columna Representante
            data_converted = []
            for item in response.data:
                print(f"Item original: {item}")
                converted = {
                    'id': item['id'],
                    'nombre': item['nombre'],
                    'monto': item['monto'],
                    'representante': item['Representante']  # Convertir a minúscula para el template
                }
                data_converted.append(converted)
            print(f"Datos convertidos: {data_converted}")
            return data_converted
            print(f"\nDatos en bruto: {response.data}")
            # Convertir Representante a representante en los datos
            data_converted = []
            for item in response.data:
                print(f"Procesando item: {item}")
                new_item = item.copy()
                if 'Representante' in new_item:
                    new_item['representante'] = new_item.pop('Representante')
                data_converted.append(new_item)
            print(f"\nDatos convertidos: {data_converted}")
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
            response = supabase.table('ninos').select('id,nombre,monto,"Representante"').execute()
            print(f"Respuesta del método alternativo: {response}")
            
            if hasattr(response, 'data'):
                data_converted = []
                for item in response.data:
                    new_item = item.copy()
                    if 'Representante' in new_item:
                        new_item['representante'] = new_item.pop('Representante')
                    data_converted.append(new_item)
                return data_converted
            return []
        except Exception as e2:
            print(f"Error en método alternativo: {e2}")
            return []
        else:
            print("La respuesta no tiene el atributo 'data'")
            return []
    except Exception as e:
        print(f"Error al obtener niños: {e}")
        print(f"Error completo: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        return []

def add_nino(nombre, monto, representante):
    """Agregar un nuevo niño a la base de datos"""
    try:
        data = {
            "nombre": nombre,
            "monto": monto,
            "Representante": representante  # Nota la R mayúscula
        }
        response = supabase.table('ninos').insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al agregar niño: {e}")
        return None

def update_nino(id, nombre, monto, representante):
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
            
        data = {
            "nombre": nombre,
            "monto": monto,
            "Representante": representante  # Nota la R mayúscula
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
