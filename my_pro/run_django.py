import os
import sys
import subprocess

# Suppress gRPC logs
os.environ["GRPC_VERBOSITY"] = "error"
os.environ["GRPC_CPP_VERBOSITY"] = "error"

# Run Django server
with open(os.devnull, 'w') as devnull:
    subprocess.run([sys.executable, "manage.py", "runserver"], stderr=devnull)
