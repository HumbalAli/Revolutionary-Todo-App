import sys
import os

# Add the backend/src directory to Python path to import the actual app
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_path)

# Import the actual FastAPI app from the backend
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(backend_src_path, "main.py"))
backend_main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_main_module)
app = backend_main_module.app

def main():
    print("Hello from todo-app!")


if __name__ == "__main__":
    main()
