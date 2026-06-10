from waitress import serve
from solar_panel_monitoring_system_project.wsgi import application

if __name__ == '__main__':
    host = '10.147.18.196'
    port = 8000
    print("=" * 60)
    print(f"✅ Waitress server running! Click the URL below to open:")
    print(f"👉 http://{host}:{port}")
    print("=" * 60)
    serve(application, host=host, port=port)