
import os
import pandas as pd
import pytest

from logging_config import setup_logging
from transparencia.main import fetch_contracts, save_csv

@pytest.mark.integration
def test_scrape_integration():
    setup_logging()
    #headless = os.getenv("HEADLESS", "true").lower() == "true"
    contratos = fetch_contracts(headless=False)
    save_csv(contratos)