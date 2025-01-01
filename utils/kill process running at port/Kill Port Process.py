import subprocess
import os

def kill_process_on_port(port):
    if os.name == 'nt':  # For Windows
        kill_process_on_port_windows(port)
    else:  # For UNIX (Linux, macOS)
        kill_process_on_port_unix(port)


def kill_process_on_port_windows(port):
    command = f'netstat -ano | findstr :{port}'
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        for line in output.splitlines():
            if 'LISTENING' in line:
                pid = line.split()[-1]
                try:
                    kill_command = f'taskkill /PID {pid} /F'
                    subprocess.check_output(kill_command, shell=True, stderr=subprocess.STDOUT, text=True)
                    print(f'Killed process with PID {pid} running on port {port}')
                except subprocess.CalledProcessError:
                    print(f"Failed to kill process with PID {pid}. It might have already been terminated or you might need elevated permissions.")
    except subprocess.CalledProcessError as e:
        print(f"Error while trying to identify processes on port {port}: {e}")



def kill_process_on_port_unix(port):
    command = f'lsof -i :{port} | awk \'{{print $2}}\' | tail -n +2'
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        for pid in output.splitlines():
            kill_command = f'kill -9 {pid}'
            subprocess.check_output(kill_command, shell=True, stderr=subprocess.STDOUT, text=True)
            print(f'Killed process with PID {pid} running on port {port}')
    except subprocess.CalledProcessError as e:
        print(f"Error while trying to kill process on port {port}: {e}")


# Test
port = 7000
kill_process_on_port(port)
