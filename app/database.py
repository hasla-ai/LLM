import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "forge_h2.sqlite3"

def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS geo_nodes (
      project_id TEXT NOT NULL,
      node_id TEXT NOT NULL,
      node_type TEXT NOT NULL,
      lat REAL NOT NULL,
      lon REAL NOT NULL,
      properties_json TEXT NOT NULL,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (project_id, node_id)
    );
    CREATE TABLE IF NOT EXISTS geo_edges (
      project_id TEXT NOT NULL,
      edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
      source_id TEXT NOT NULL,
      target_id TEXT NOT NULL,
      edge_type TEXT NOT NULL,
      properties_json TEXT NOT NULL,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS geo_events (
      event_id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id TEXT NOT NULL,
      event_type TEXT NOT NULL,
      payload_json TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS geo_task_states (
      project_id TEXT NOT NULL,
      task_id TEXT NOT NULL,
      status TEXT NOT NULL,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (project_id, task_id)
    );
    CREATE TABLE IF NOT EXISTS geo_project_profiles (
      project_id TEXT PRIMARY KEY,
      profile_json TEXT NOT NULL,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    return db

def save_graph(project_id: str, nodes: list[dict], edges: list[dict]):
    with connection() as db:
        existing_nodes = {row[0] for row in db.execute("SELECT node_id FROM geo_nodes WHERE project_id = ?", (project_id,))}
        existing_edges = {(row[0], row[1], row[2]) for row in db.execute("SELECT source_id,target_id,edge_type FROM geo_edges WHERE project_id = ?", (project_id,))}
        new_nodes = 0
        new_edges = 0
        for node in nodes:
            node_id = str(node["id"])
            if node_id in existing_nodes:
                continue
            db.execute("INSERT INTO geo_nodes(project_id,node_id,node_type,lat,lon,properties_json) VALUES(?,?,?,?,?,?)", (
                project_id, node_id, str(node.get("type", "unknown")), float(node["lat"]), float(node["lon"]), json.dumps(node.get("properties", {}), ensure_ascii=False)))
            db.execute("INSERT INTO geo_events(project_id,event_type,payload_json) VALUES(?,?,?)", (project_id, "node.created", json.dumps(node, ensure_ascii=False)))
            existing_nodes.add(node_id)
            new_nodes += 1
        for edge in edges:
            edge_key = (str(edge["from"]), str(edge["to"]), str(edge.get("type", "process-flow")))
            if edge_key in existing_edges:
                continue
            db.execute("INSERT INTO geo_edges(project_id,source_id,target_id,edge_type,properties_json) VALUES(?,?,?,?,?)", (
                project_id, edge_key[0], edge_key[1], edge_key[2], json.dumps(edge.get("properties", {}), ensure_ascii=False)))
            db.execute("INSERT INTO geo_events(project_id,event_type,payload_json) VALUES(?,?,?)", (project_id, "edge.created", json.dumps(edge, ensure_ascii=False)))
            existing_edges.add(edge_key)
            new_edges += 1
        return {"new_nodes": new_nodes, "new_edges": new_edges}

def record_event(project_id: str, event_type: str, payload: dict):
    with connection() as db:
        db.execute("INSERT INTO geo_events(project_id,event_type,payload_json) VALUES(?,?,?)", (project_id, event_type, json.dumps(payload, ensure_ascii=False)))

def set_task_status(project_id: str, task_id: str, status: str):
    with connection() as db:
        db.execute("INSERT INTO geo_task_states(project_id,task_id,status) VALUES(?,?,?) ON CONFLICT(project_id,task_id) DO UPDATE SET status=excluded.status,updated_at=CURRENT_TIMESTAMP", (project_id, task_id, status))
        db.execute("INSERT INTO geo_events(project_id,event_type,payload_json) VALUES(?,?,?)", (project_id, "task.status_changed", json.dumps({"task_id": task_id, "status": status}, ensure_ascii=False)))

def get_task_states(project_id: str):
    with connection() as db:
        return {row["task_id"]: row["status"] for row in db.execute("SELECT task_id,status FROM geo_task_states WHERE project_id=?", (project_id,))}

def save_profile(project_id: str, profile: dict):
    with connection() as db:
        db.execute(
            "INSERT INTO geo_project_profiles(project_id,profile_json) VALUES(?,?) ON CONFLICT(project_id) DO UPDATE SET profile_json=excluded.profile_json,updated_at=CURRENT_TIMESTAMP",
            (project_id, json.dumps(profile, ensure_ascii=False)),
        )
        db.execute(
            "INSERT INTO geo_events(project_id,event_type,payload_json) VALUES(?,?,?)",
            (project_id, "project.profile_saved", json.dumps(profile, ensure_ascii=False)),
        )

def load_profile(project_id: str):
    with connection() as db:
        row = db.execute("SELECT profile_json FROM geo_project_profiles WHERE project_id=?", (project_id,)).fetchone()
    return json.loads(row["profile_json"]) if row else None

def load_graph(project_id: str):
    with connection() as db:
        nodes = [dict(row) for row in db.execute("SELECT * FROM geo_nodes WHERE project_id=? ORDER BY updated_at,node_id", (project_id,))]
        edges = [dict(row) for row in db.execute("SELECT * FROM geo_edges WHERE project_id=? ORDER BY edge_id", (project_id,))]
    return {
        "project_id": project_id,
        "nodes": [{"id": n["node_id"], "type": n["node_type"], "lat": n["lat"], "lon": n["lon"], "properties": json.loads(n["properties_json"])} for n in nodes],
        "edges": [{"from": e["source_id"], "to": e["target_id"], "type": e["edge_type"], "properties": json.loads(e["properties_json"])} for e in edges],
    }
