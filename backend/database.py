"""
Persistência leve (SQLite, biblioteca padrão — sem dependência extra) do
histórico de predições feitas pela API. Implementa a Fase 2 do
IMPLEMENTATION_PLAN.md: sair do modelo "tudo calculado on-the-fly" para ter
rastro de predições, permitindo no futuro comparar a previsão do PreDis com
o que de fato aconteceu (ver CASE_STUDY_SJC.md, seção 7).
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# backend/data/ é montado como volume no Docker (ver docker-compose.yml),
# para que o histórico de predições e o modelo treinado sobrevivam a
# restarts/rebuilds do container.
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "predis.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT NOT NULL,
    created_at TEXT NOT NULL,
    risk_level INTEGER NOT NULL,
    risk_probability REAL NOT NULL,
    feature_importance TEXT NOT NULL,
    message TEXT
);
"""


@contextmanager
def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Cria a tabela de predições se ainda não existir. Chamado no startup da API."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _connect() as conn:
        conn.execute(_SCHEMA)


def save_prediction(
    region: str,
    risk_level: int,
    risk_probability: float,
    feature_importance: Dict[str, float],
    message: Optional[str] = None,
) -> None:
    """Persiste uma predição. Falhas aqui são responsabilidade do chamador
    tratar (não devem derrubar a resposta da API — ver main.py)."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO predictions (region, created_at, risk_level, risk_probability, feature_importance, message) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                region,
                datetime.now(timezone.utc).isoformat(),
                risk_level,
                risk_probability,
                json.dumps(feature_importance),
                message,
            ),
        )


def get_predictions(region: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Retorna as predições mais recentes, mais recente primeiro."""
    limit = max(1, min(limit, 500))
    with _connect() as conn:
        if region:
            rows = conn.execute(
                "SELECT * FROM predictions WHERE region = ? ORDER BY id DESC LIMIT ?",
                (region, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()

    results = []
    for row in rows:
        item = dict(row)
        item["feature_importance"] = json.loads(item["feature_importance"])
        results.append(item)
    return results
