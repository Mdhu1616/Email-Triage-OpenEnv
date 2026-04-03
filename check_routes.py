from app import create_interface, register_openenv_routes

demo = create_interface()
register_openenv_routes(demo.app)
print([r.path for r in demo.app.routes if '/openenv' in r.path])
print(any(r.path == '/openenv/reset' for r in demo.app.routes))
