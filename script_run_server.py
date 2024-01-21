import os

if __name__ == '__main__': 
    conda_env_name = 'senv'
    os.system(f'C:\\Users\\%USERNAME%\\.conda\\envs\\{conda_env_name}\\python.exe -m uvicorn drf_signal_simplejwt.asgi:application --reload --host 0.0.0.0 --port 8000 --use-colors --log-level info --workers 1')
