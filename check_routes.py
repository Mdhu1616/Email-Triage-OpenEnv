from app import create_interface, register_api_routes

demo = create_interface()
register_api_routes(demo.app)
print([r.path for r in demo.app.routes if '/api' in r.path])
print(any(r.path == '/api/reset' for r in demo.app.routes))
