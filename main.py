import sys
import os

# Add the project root and backend/src to Python path to import the actual app
project_root = os.path.dirname(__file__)
backend_src_path = os.path.join(project_root, 'backend', 'src')

# Insert paths at the beginning to ensure proper import resolution
sys.path.insert(0, project_root)
sys.path.insert(0, backend_src_path)

# Import the actual FastAPI app from the backend
try:
    from backend.src.main import app
except ImportError as e:
    # Fallback to importlib approach if direct import fails
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", os.path.join(backend_src_path, "main.py"))
    backend_main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend_main_module)
    app = backend_main_module.app

def main():
    print("Hello from todo-app!")


if __name__ == "__main__":
    main()
