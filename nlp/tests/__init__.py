import sys
import os
path = os.path.dirname(__file__)
path = os.path.join(path, 'data_access')
path = os.path.join(path, 'nlpql')
path = os.path.join(path, 'tasks')
path = os.path.join(path, 'algorithms')
path = os.path.join(path, 'custom_tasks')
if path not in sys.path:
    sys.path.append(path)
print(path)

