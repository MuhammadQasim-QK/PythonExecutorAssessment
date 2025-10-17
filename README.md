# Python Code Execution Service

A secure API service that executes arbitrary Python code in a sandboxed environment using nsjail.

## Test Cases

### Input Validation Tests

1. **Missing main() Function**
```python

script = """
def some_function():
    return {"data": "test"}
"""
```
Expected Response:
```json
{
  "error": "ERROR: No main() function found",
  "stdout": ""
}
```

2. **Non-JSON Return Value**
```python

script = """
def main():
    return set([1, 2, 3])  # Sets are not JSON serializable
"""
```
Expected Response:
```json
{
  "error": "ERROR: main() function must return JSON serializable data",
  "stdout": ""
}
```

### Security Tests

1. **Resource Limit Test**
```python

script = """
def main():
    large_list = list(range(100000000))  # Tries to allocate too much memory
    return {"data": large_list}
"""
```
Expected Response:
```json
{
  "error": "Script execution error: Memory limit exceeded",
  "stdout": ""
}
```

### Valid Use Cases

1. **Basic Calculation**
```python

script = """
def main():
    x = 10
    y = 20
    return {"sum": x + y, "product": x * y}
"""
```
Expected Response:
```json
{
  "result": {
    "sum": 30,
    "product": 200
  },
  "stdout": ""
}
```

2. **Pandas DataFrame Operations**
```python

script = """
def main():
    import pandas as pd
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    return {
        "mean_A": float(df['A'].mean()),
        "sum_B": float(df['B'].sum())
    }
"""
```
Expected Response:
```json
{
  "result": {
    "mean_A": 2.0,
    "sum_B": 15.0
  },
  "stdout": ""
}
```

3. **NumPy Computations**
```python

script = """
def main():
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr))
    }
"""
```
Expected Response:
```json
{
  "result": {
    "mean": 3.0,
    "std": 1.4142135623730951
  },
  "stdout": ""
}
```

## Features

- 🔒 **Secure execution** using nsjail sandboxing
- 🐳 **Docker containerized** for easy deployment
- 📦 **Minimal image size** using Python 3.11 slim
- 🛡️ **Input validation** and security checks
- 📚 **Basic libraries included** (pandas, numpy)
- ⚡ **Fast execution** with resource limits

## Security

The service uses nsjail to provide:
- Resource limits (memory, CPU, file size)
- Network isolation
- File system restrictions
- Process isolation
- Time limits (30 seconds max)

## API Endpoints

### POST /execute

Execute a Python script and return the result of the `main()` function.

**Request:**
```json
{
  "script": "def main():\n    return {'message': 'Hello, World!', 'number': 42}"
}
```

**Response:**
```json
{
  "result": {
    "message": "Hello, World!",
    "number": 42
  },
  "stdout": "{\"message\": \"Hello, World!\", \"number\": 42}"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Requirements

- The script must contain a `main()` function
- The `main()` function must return JSON-serializable data
- No dangerous imports (os, subprocess, sys, etc.) are allowed
- Script execution is limited to 30 seconds

## Quick Start

### Local Development

1. **Clone and build the Docker image:**
```bash
docker build -t python-executor-secure .
```

2. **Run the service (Windows with PowerShell):**
```powershell
.\run_local.ps1
```

**Or manually:**
```bash
docker run --rm -p 8080:8080 --privileged python-executor-secure
```

3. **Test with cURL:**
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import pandas as pd\n    import numpy as np\n    data = {\"values\": np.array([1, 2, 3, 4, 5]).tolist(), \"mean\": float(np.mean([1, 2, 3, 4, 5]))}\n    return data"
  }'
```

## Example Scripts

### Basic JSON Return
```python
def main():
    return {
        "status": "success",
        "data": [1, 2, 3, 4, 5],
        "message": "Script executed successfully"
    }
```

### Using Pandas and NumPy
```python
def main():
    import pandas as pd
    import numpy as np
    
    data = {
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'score': [85, 92, 78]
    }
    
    df = pd.DataFrame(data)
    
    result = {
        'total_records': len(df),
        'average_age': float(df['age'].mean()),
        'average_score': float(df['score'].mean()),
        'highest_score': int(df['score'].max()),
        'lowest_score': int(df['score'].min())
    }
    
    return result
```

### Mathematical Operations
```python
def main():
    import numpy as np
    
    random_data = np.random.normal(100, 15, 1000)
    
    stats = {
        'mean': float(np.mean(random_data)),
        'std': float(np.std(random_data)),
        'min': float(np.min(random_data)),
        'max': float(np.max(random_data)),
        'median': float(np.median(random_data))
    }
    
    return stats
```

## Error Handling

The service returns appropriate error messages for various scenarios:

### Missing main() function
```json
{
  "error": "ERROR: No main() function found",
  "stdout": ""
}
```

### Non-JSON return value
```json
{
  "error": "ERROR: main() function must return JSON serializable data",
  "stdout": ""
}
```

### Execution timeout
```json
{
  "error": "Script execution timeout (30 seconds)",
  "stdout": ""
}
```

### Invalid request format
```json
{
  "error": "Request must contain 'script' field",
  "stdout": ""
}
```

## Security Considerations

- Scripts are executed in a sandboxed environment using nsjail
- Resource limits prevent excessive CPU/memory usage
- Network access is restricted
- File system access is limited to /tmp
- Dangerous imports and functions are blocked
- Execution time is limited to 30 seconds

## Limitations

- Maximum execution time: 30 seconds
- Memory limit: 512MB
- No network access from within scripts
- No file system access outside /tmp
- Only basic Python libraries available (pandas, numpy)

## Development

### Project Structure
```
.
├── app.py                 # Main Flask application
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── nsjail.config.proto   # nsjail security configuration
├── run_local.ps1        # Windows PowerShell run script
├── .dockerignore        # Docker ignore file
└── README.md            # This file
```

### Building and Testing Locally

```powershell
.\test_service.ps1
```

**Or manually:**
```bash
docker build -t python-executor-secure .

docker run --rm -p 8080:8080 --privileged python-executor-secure

curl http://localhost:8080/health

curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"test\": \"success\"}"}'
```

## License

This project is provided as-is for educational and development purposes.
