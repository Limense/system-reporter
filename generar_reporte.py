#!/usr/bin/env python3
"""
Script para generar reporte de estado del sistema
Autor: @Limense
Fecha: 2025-05-27
"""

import json
import datetime
import platform
import psutil
import os
import subprocess

def obtener_info_git():
    """Obtiene información del repositorio Git"""
    try:
        # Obtener rama actual
        rama = subprocess.check_output(['git', 'branch', '--show-current'], 
                                     text=True).strip()
        # Obtener último commit
        ultimo_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                              text=True).strip()
        # Obtener mensaje del último commit
        mensaje_commit = subprocess.check_output(['git', 'log', '-1', '--pretty=%B'], 
                                               text=True).strip()
        return {
            "rama_actual": rama,
            "ultimo_commit": ultimo_commit[:7],  # Solo primeros 7 caracteres
            "mensaje_commit": mensaje_commit,
            "repositorio_limpio": len(subprocess.check_output(['git', 'status', '--porcelain'], text=True)) == 0
        }
    except subprocess.CalledProcessError:
        return {
            "error": "No es un repositorio Git o Git no está disponible"
        }

def obtener_info_sistema():
    """Obtiene información del sistema"""
    return {
        "sistema_operativo": platform.system(),
        "version_os": platform.release(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }

def obtener_recursos_sistema():
    """Obtiene información de recursos del sistema"""
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    
    return {
        "cpu": {
            "nucleos_fisicos": psutil.cpu_count(logical=False),
            "nucleos_logicos": psutil.cpu_count(logical=True),
            "uso_porcentaje": psutil.cpu_percent(interval=1)
        },
        "memoria": {
            "total_gb": round(memoria.total / (1024**3), 2),
            "disponible_gb": round(memoria.available / (1024**3), 2),
            "uso_porcentaje": memoria.percent
        },
        "disco": {
            "total_gb": round(disco.total / (1024**3), 2),
            "libre_gb": round(disco.free / (1024**3), 2),
            "uso_porcentaje": round((disco.used / disco.total) * 100, 2)
        }
    }

def obtener_archivos_proyecto():
    """Cuenta archivos por extensión en el proyecto"""
    extensiones = {}
    total_archivos = 0
    
    for root, dirs, files in os.walk('.'):
        # Ignorar directorios comunes
        dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', 'node_modules', '.venv'))]
        
        for file in files:
            total_archivos += 1
            ext = os.path.splitext(file)[1].lower()
            if not ext:
                ext = 'sin_extension'
            extensiones[ext] = extensiones.get(ext, 0) + 1
    
    return {
        "total_archivos": total_archivos,
        "por_extension": dict(sorted(extensiones.items(), key=lambda x: x[1], reverse=True))
    }

def generar_reporte():
    """Función principal que genera el reporte completo"""
    timestamp = datetime.datetime.utcnow()
    
    reporte = {
        "metadata": {
            "generado_por": "Script de Reporte de Sistema",
            "autor": "@Limense",
            "fecha_generacion": timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "timestamp_unix": int(timestamp.timestamp()),
            "version_script": "1.0.0"
        },
        "sistema": obtener_info_sistema(),
        "recursos": obtener_recursos_sistema(),
        "git": obtener_info_git(),
        "proyecto": obtener_archivos_proyecto(),
        "variables_entorno": {
            "usuario": os.getenv('USER', 'desconocido'),
            "home": os.getenv('HOME', 'desconocido'),
            "path_python": os.getenv('PYTHON_PATH', 'no_definido'),
            "ci": os.getenv('CI', 'false') == 'true'
        }
    }
    
    return reporte

def main():
    """Función principal"""
    print("🔍 Generando reporte de sistema...")
    
    try:
        reporte = generar_reporte()
        
        # Crear directorio de reportes si no existe
        os.makedirs('reportes', exist_ok=True)
        
        # Nombre del archivo con timestamp
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reportes/reporte_sistema_{timestamp}.json"
        
        # Guardar reporte
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        # También crear/actualizar el último reporte
        with open('reportes/ultimo_reporte.json', 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte generado exitosamente:")
        print(f"   📁 Archivo: {nombre_archivo}")
        print(f"   📊 Tamaño: {os.path.getsize(nombre_archivo)} bytes")
        print(f"   🕒 Fecha: {reporte['metadata']['fecha_generacion']}")
        
        # Mostrar resumen
        print(f"\n📋 Resumen del sistema:")
        print(f"   💻 OS: {reporte['sistema']['sistema_operativo']} {reporte['sistema']['version_os']}")
        print(f"   🐍 Python: {reporte['sistema']['python_version']}")
        print(f"   💾 Memoria: {reporte['recursos']['memoria']['uso_porcentaje']}% usada")
        print(f"   💽 Disco: {reporte['recursos']['disco']['uso_porcentaje']}% usado")
        print(f"   📁 Archivos: {reporte['proyecto']['total_archivos']} total")
        
        if 'rama_actual' in reporte['git']:
            print(f"   🌿 Git: rama '{reporte['git']['rama_actual']}' - {reporte['git']['ultimo_commit']}")
        
    except Exception as e:
        print(f"❌ Error al generar reporte: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())