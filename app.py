import os
import json
import subprocess
import tempfile
import shutil
import signal
import resource
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class PythonExecutor:
    def __init__(self):
        self.nsjail_config_path = "/app/nsjail.config.proto"
    
    def execute_script(self, script_content):
        """Execute Python script securely using nsjail"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                script_path = os.path.join(temp_dir, "script.py")                
                with open(script_path, 'w') as f:
                    f.write(script_content)                
                wrapper_script = f'''import sys
                                import json
                                import traceback

                                try:
                                    # Import and execute the script
                                    exec(open('{script_path}').read(), globals())
                                    
                                    # Check if main function exists
                                    if 'main' not in globals():
                                        print("ERROR: No main() function found", file=sys.stderr)
                                        sys.exit(1)
                                    
                                    # Execute main function
                                    result = main()
                                    
                                    # Check if result is JSON serializable
                                    try:
                                        json.dumps(result)
                                        print(json.dumps(result))
                                    except (TypeError, ValueError):
                                        print("ERROR: main() function must return JSON serializable data", file=sys.stderr)
                                        sys.exit(1)
                                        
                                except Exception as e:
                                    print(f"ERROR: {{str(e)}}", file=sys.stderr)
                                    traceback.print_exc(file=sys.stderr)
                                    sys.exit(1)
                                '''
                wrapper_path = os.path.join(temp_dir, "wrapper.py")
                with open(wrapper_path, 'w') as f:
                    f.write(wrapper_script)
                
                cmd = [
                    'nsjail',
                    '-C', self.nsjail_config_path,
                    '--', '/usr/local/bin/python3', wrapper_path
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=35,
                    cwd=temp_dir
                )
                
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                
                if result.returncode != 0:
                    return {
                        "error": stderr or "Script execution failed",
                        "stdout": stdout
                    }                
                try:
                    result_data = json.loads(stdout)
                    return {
                        "result": result_data,
                        "stdout": stdout
                    }
                except json.JSONDecodeError:
                    return {
                        "error": "main() function must return JSON serializable data",
                        "stdout": stdout
                    } 
        except subprocess.TimeoutExpired:
            return {
                "error": "Script execution timeout (30 seconds)",
                "stdout": ""
            }
        except Exception as e:
            return {
                "error": f"Execution error: {str(e)}",
                "stdout": ""
            }

executor = PythonExecutor()

@app.route('/execute', methods=['POST'])
def execute_script():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Request must contain 'script' field"}), 400
        
        script_content = data['script']
        if not isinstance(script_content, str) or not script_content.strip():
            return jsonify({"error": "Script content must be a non-empty string"}), 400
        
        dangerous_patterns = [
            # System access
            'import subprocess',
            'import sys',
            'import shutil',
            'import tempfile',
            'import glob',
            'import fnmatch',
            'import pathlib',
            'import stat',
            'import pwd',
            'import grp',
            # Network access
            'import socket',
            'import urllib',
            'import urllib2',
            'import urllib3',
            'import http',
            'import requests',
            'import ftplib',
            'import smtplib',
            'import telnetlib',
            'import poplib',
            'import imaplib',
            'import nntplib',
            'import ssl',
            # Process/threading control
            'import ctypes',
            'import multiprocessing',
            'import threading',
            'import queue',
            'import mmap',
            # Dangerous functions
            '__import__',
            'eval(',
            'exec(',
            'open(',
            'file(',
            'input(',
            'raw_input(',
            'compile(',
        ]
        script_lower = script_content.lower()
        for pattern in dangerous_patterns:
            if pattern in script_lower:
                return jsonify({
                    "error": f"Script contains potentially dangerous import or function: {pattern}",
                    "stdout": ""
                }), 400        
        execution_result = executor.execute_script(script_content) 
        if "error" in execution_result:
            return jsonify(execution_result), 400
        return jsonify(execution_result)
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "stdout": ""
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
