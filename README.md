# Calculator App (Example for CI/CD Exam)

Pure-Python calculator logic + small stateful CalculatorApp + healthcheck API.

## Run unit/integration tests
```bash
python -m unittest discover -s tests -v
```

## Healthcheck
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python api.py
curl -fsS http://localhost:5000/health
```
