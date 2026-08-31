"""Session and theme management for NovaCode TUI."""

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path


DEFAULT_DB_PATH = Path.home() / ".local" / "share" / "novacode" / "sessions.db"
THEME_DB_PATH = Path.home() / ".local" / "share" / "novacode" / "themes.db"

THEMES = {
    "dark": {
        "primary": "#61afef",
        "secondary": "#c678dd",
        "accent": "#e5c07b",
        "background": "#282c34",
        "foreground": "#abb2bf",
        "success": "#98c379",
        "warning": "#d19a66",
        "error": "#e06c75",
        "info": "#56b6c2",
        "user_message": "#61afef",
        "assistant_message": "#abb2bf",
        "system_message": "#98c379",
        "border": "#3e4451",
        "selection": "#3e4451",
    },
    "light": {
        "primary": "#0969da",
        "secondary": "#8250df",
        "accent": "#bf8700",
        "background": "#ffffff",
        "foreground": "#1f2328",
        "success": "#1a7f37",
        "warning": "#9a6700",
        "error": "#cf222e",
        "info": "#0550ae",
        "user_message": "#0969da",
        "assistant_message": "#1f2328",
        "system_message": "#1a7f37",
        "border": "#d0d7de",
        "selection": "#b6d7ff",
    },
    "nord": {
        "primary": "#88c0d0",
        "secondary": "#b48ead",
        "accent": "#ebcb8b",
        "background": "#2e3440",
        "foreground": "#eceff4",
        "success": "#a3be8c",
        "warning": "#d08770",
        "error": "#bf616a",
        "info": "#5e81ac",
        "user_message": "#88c0d0",
        "assistant_message": "#eceff4",
        "system_message": "#a3be8c",
        "border": "#3b4252",
        "selection": "#434c5e",
    },
    "gruvbox": {
        "primary": "#fabd2f",
        "secondary": "#d3869b",
        "accent": "#fe8019",
        "background": "#282828",
        "foreground": "#ebdbb2",
        "success": "#b8bb26",
        "warning": "#d79921",
        "error": "#fb4934",
        "info": "#83a598",
        "user_message": "#fabd2f",
        "assistant_message": "#ebdbb2",
        "system_message": "#b8bb26",
        "border": "#504945",
        "selection": "#3c3836",
    },
}


class SessionManager:
    """Manages TUI sessions with SQLite storage."""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock:
            conn = self._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    messages TEXT DEFAULT '[]',
                    token_count INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()

    def create_session(self, model, mode, language="en", metadata=None):
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        meta = json.dumps(metadata or {})
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """INSERT INTO sessions
                   (id, model, mode, language, messages, token_count, metadata, created_at, updated_at)
                   VALUES (?, ?, ?, ?, '[]', 0, ?, ?, ?)""",
                (session_id, model, mode, language, meta, now, now),
            )
            conn.commit()
            conn.close()
        return session_id

    def save_session(self, session_id, messages, token_count=None, metadata=None):
        now = datetime.utcnow().isoformat()
        msgs = json.dumps(messages)
        with self._lock:
            conn = self._get_conn()
            if token_count is not None and metadata is not None:
                conn.execute(
                    """UPDATE sessions SET messages=?, token_count=?, metadata=?, updated_at=?
                       WHERE id=?""",
                    (msgs, token_count, json.dumps(metadata), now, session_id),
                )
            elif token_count is not None:
                conn.execute(
                    """UPDATE sessions SET messages=?, token_count=?, updated_at=?
                       WHERE id=?""",
                    (msgs, token_count, now, session_id),
                )
            elif metadata is not None:
                conn.execute(
                    """UPDATE sessions SET messages=?, metadata=?, updated_at=?
                       WHERE id=?""",
                    (msgs, json.dumps(metadata), now, session_id),
                )
            else:
                conn.execute(
                    "UPDATE sessions SET messages=?, updated_at=? WHERE id=?",
                    (msgs, now, session_id),
                )
            conn.commit()
            conn.close()

    def load_session(self, session_id):
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
            conn.close()
        if row is None:
            return None
        return {
            "id": row["id"],
            "model": row["model"],
            "mode": row["mode"],
            "language": row["language"],
            "messages": json.loads(row["messages"]),
            "token_count": row["token_count"],
            "metadata": json.loads(row["metadata"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def list_sessions(self):
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM sessions ORDER BY updated_at DESC"
            ).fetchall()
            conn.close()
        return [
            {
                "id": r["id"],
                "model": r["model"],
                "mode": r["mode"],
                "language": r["language"],
                "messages": json.loads(r["messages"]),
                "token_count": r["token_count"],
                "metadata": json.loads(r["metadata"]),
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            }
            for r in rows
        ]

    def delete_session(self, session_id):
        with self._lock:
            conn = self._get_conn()
            conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
            conn.commit()
            conn.close()

    def fork_session(self, session_id):
        original = self.load_session(session_id)
        if original is None:
            return None
        new_id = self.create_session(
            model=original["model"],
            mode=original["mode"],
            language=original["language"],
            metadata=original["metadata"],
        )
        self.save_session(
            new_id,
            messages=original["messages"],
            token_count=original["token_count"],
            metadata=original["metadata"],
        )
        return new_id

    def export_session(self, session_id):
        session = self.load_session(session_id)
        if session is None:
            return None
        lines = [
            f"# Session: {session['id']}",
            f"**Model:** {session['model']}",
            f"**Mode:** {session['mode']}",
            f"**Language:** {session['language']}",
            f"**Created:** {session['created_at']}",
            f"**Updated:** {session['updated_at']}",
            f"**Tokens:** {session['token_count']}",
            "",
            "---",
            "",
        ]
        for msg in session["messages"]:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"## {role}")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)

    def get_statistics(self):
        with self._lock:
            conn = self._get_conn()
            total_sessions = conn.execute(
                "SELECT COUNT(*) FROM sessions"
            ).fetchone()[0]
            total_tokens = conn.execute(
                "SELECT COALESCE(SUM(token_count), 0) FROM sessions"
            ).fetchone()[0]
            avg_length = conn.execute(
                "SELECT COALESCE(AVG(json_array_length(messages)), 0) FROM sessions"
            ).fetchone()[0]
            model_rows = conn.execute(
                "SELECT model, COUNT(*) as count FROM sessions GROUP BY model ORDER BY count DESC"
            ).fetchall()
            mode_rows = conn.execute(
                "SELECT mode, COUNT(*) as count FROM sessions GROUP BY mode ORDER BY count DESC"
            ).fetchall()
            conn.close()
        return {
            "total_sessions": total_sessions,
            "total_tokens": total_tokens,
            "per_model_usage": {r["model"]: r["count"] for r in model_rows},
            "per_mode_usage": {r["mode"]: r["count"] for r in mode_rows},
            "average_session_length": round(avg_length, 2),
        }


class ThemeManager:
    """Manages TUI themes with persistence."""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else THEME_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._current_theme = None
        self._custom_themes = {}
        self._init_db()
        self._load_current()

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock:
            conn = self._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS theme_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS custom_themes (
                    name TEXT PRIMARY KEY,
                    colors TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()

    def _load_current(self):
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT value FROM theme_state WHERE key='current_theme'"
            ).fetchone()
            custom_rows = conn.execute("SELECT name, colors FROM custom_themes").fetchall()
            conn.close()
        if row:
            self._current_theme = row["value"]
        else:
            self._current_theme = "dark"
        for r in custom_rows:
            self._custom_themes[r["name"]] = json.loads(r["colors"])

    @property
    def current_theme(self):
        return self._current_theme

    @property
    def available_themes(self):
        builtins = list(THEMES.keys())
        customs = list(self._custom_themes.keys())
        return builtins + customs

    def get_colors(self, theme_name=None):
        name = theme_name or self._current_theme
        if name in self._custom_themes:
            return dict(self._custom_themes[name])
        if name in THEMES:
            return dict(THEMES[name])
        return dict(THEMES["dark"])

    def switch_theme(self, theme_name):
        if theme_name not in THEMES and theme_name not in self._custom_themes:
            return False
        self._current_theme = theme_name
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """INSERT OR REPLACE INTO theme_state (key, value)
                   VALUES ('current_theme', ?)""",
                (theme_name,),
            )
            conn.commit()
            conn.close()
        return True

    def add_custom_theme(self, name, colors):
        required_keys = [
            "primary", "secondary", "accent", "background", "foreground",
            "success", "warning", "error", "info",
            "user_message", "assistant_message", "system_message",
            "border", "selection",
        ]
        for key in required_keys:
            if key not in colors:
                raise ValueError(f"Missing required color key: {key}")
        self._custom_themes[name] = dict(colors)
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """INSERT OR REPLACE INTO custom_themes (name, colors)
                   VALUES (?, ?)""",
                (name, json.dumps(colors)),
            )
            conn.commit()
            conn.close()

    def remove_custom_theme(self, name):
        if name in THEMES:
            return False
        if name in self._custom_themes:
            del self._custom_themes[name]
            with self._lock:
                conn = self._get_conn()
                conn.execute("DELETE FROM custom_themes WHERE name=?", (name,))
                conn.commit()
                conn.close()
            if self._current_theme == name:
                self.switch_theme("dark")
            return True
        return False
