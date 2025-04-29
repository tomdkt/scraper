# Contracts Scraper

Fetch every contract from portal and export the data—including _Valor total_—to `contratos.csv`.

---
## Run
```bash
  python -m transparencia.main 
```

Or 
```bash
  pytest tests/integrations/test_main.py::test_scrape_integration 
```

## Requirements
* Python ≥ 3.10
* Chromium (downloaded automatically by Playwright)
#  Installation

```bash
  pipx install uv 
```

# inside the project root:
```bash  
  uv venv .venv
  source .venv/bin/activate
```
# Install runtime deps
//double check this
```bash
  uv pip install beautifulsoup4 playwright pytest
  playwright install
```
```bash
  uv pip install -r requirements.txt
```

# Minimal project layout
```markdown
scraper/
│
├─ transparencia/
│   └─ main.py
│
└─ tests/
    ├─ integration/
    │   └─ transparencia/
    │       └─ test_main.py
```
