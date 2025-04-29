import csv
import logging
import re
import time
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Browser, Page

from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

URL = ("https://transparencia.e-publica.net/epublica-portal/#/"
       "palmeira/portal/compras/contratoTable")

BASE = "https://transparencia.e-publica.net/epublica-portal/"


# ── helpers ──────────────────────────────────────────────────────────────────
def _open_page(browser: Browser, url: str) -> Page:
    page = browser.new_page()
    page.set_default_timeout(60_000)
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector("table tbody tr", timeout=60_000)
    return page


def _parse_table(html: str) -> List[Dict[str, str]]:
    soup  = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table")
    if table is None:
        return []

    # cabeçalhos visíveis (ignora vazios como a coluna de ações)
    header = [th.get_text(strip=True) for th in table.select("thead th")
              if th.get_text(strip=True)]
    clean_header = header[1:]
    rows = []
    for tr in table.select("tbody tr[ng-repeat-start]"):
        # 1ª <tr> (a “principal” da dupla)
        cells = [td.get_text(strip=True) for td in tr.select("td")]

        # 2ª <tr> logo após a principal
        extra_tr = tr.find_next_sibling(
            lambda tag: tag.name == "tr" and not tag.get("ng-repeat-start")
        )
        if extra_tr:
            tds = extra_tr.select("td")
            if len(tds) >= 2:
                # concatena o 2º <td> da linha extra ao 2º <td> da linha principal
                cells[1] += "\n" + tds[1].get_text(strip=True)

        rows.append(dict(zip(clean_header, cells[: len(clean_header)])))  # descarta sobra

    return rows





def fetch_contracts(headless: bool = True) -> List[Dict[str, str]]:
    with sync_playwright() as p:
        logger.info("Launching browser...")
        browser = p.chromium.launch(headless=headless)
        logger.info("Opening main page...")
        page    = _open_page(browser, URL)

        all_rows: list[dict[str, str]] = []
        while True:
            logger.info(f"Collecting contracts")
            page_rows = _parse_table(page.content())
            trs       = page.query_selector_all('tbody tr[ng-repeat-start]')

            for i, tr in enumerate(trs):
                row = page_rows[i]

                link = tr.query_selector('td.epublica-table-actions a.btn')
                if link:
                    href = link.get_attribute("href") or ""
                    detail_url = BASE + href

                    # create a brand-new page (new context) for each detail view
                    logger.info(f"Opening detail page: {detail_url}")
                    detail = browser.new_page()
                    detail.goto(detail_url, wait_until="domcontentloaded")

                    h3    = detail.wait_for_selector(
                        "h3:has-text('Valor total')", timeout=60_000
                    )
                    match = re.search(r'R\$\s*([\d\.,]+)', h3.inner_text())
                    row["Valor total"] = match.group(1) if match else ""

                    detail.close()

                all_rows.append(row)

            next_btn = page.query_selector('a.pagination-next:not(.disabled)')
            if not next_btn:
                break
            next_btn.click()
            page.wait_for_selector("tbody tr[ng-repeat-start]", timeout=60_000)

        browser.close()
        logger.info(f"Finished. Total contracts collected: {len(all_rows)}")
    return all_rows




def save_csv(data: List[Dict[str, str]], dest: Path = Path("contratos.csv")) -> None:
    logger.info("save_csv")
    if not data:
        return
    fieldnames = list({k for row in data for k in row.keys()})
    with dest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    logger.info("Starting contract scraping...")

    start = time.time()
    contratos = fetch_contracts(headless=True)
    save_csv(contratos)
    duration = time.time() - start

    logger.info(f"Saved {len(contratos)} contracts → contratos.csv")
    logger.info(f"Total duration: {duration:.2f} seconds")
