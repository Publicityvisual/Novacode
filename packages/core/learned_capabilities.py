#!/usr/bin/env python3
"""NovaCode Self-Learning Engine.

Provides capabilities for the CLI to learn from interactions, auto-improve prompts,
evolve model selection, and maintain a knowledge base of solutions.

Classes:
    SelfLearningEngine: Stores and retrieves learned patterns from SQLite.
    AutoImprover: Analyzes past sessions and suggests optimizations.
    ModelEvolver: Tracks model performance and auto-selects optimal models.

Functions:
    learn_from_interaction: Record a session interaction for learning.
    get_improved_prompt: Retrieve an optimized prompt for a task type.
    get_best_model_for_task: Get the best-performing model for a task.
    record_outcome: Record success/failure metrics for a session.
    auto_tune_parameters: Run automatic parameter tuning based on history.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = Path.home() / ".local" / "share" / "novacode" / "learning.db"

SCHEMA_VERSION = 1

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    pattern TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence REAL DEFAULT 0.5,
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    model_used TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response_summary TEXT DEFAULT '',
    success_score REAL DEFAULT 0.0,
    duration_seconds REAL DEFAULT 0.0,
    tokens_used INTEGER DEFAULT 0,
    user_feedback INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    task_type TEXT NOT NULL,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_latency REAL DEFAULT 0.0,
    avg_tokens INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model, task_type)
);

CREATE TABLE IF NOT EXISTS prompt_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    original_prompt TEXT NOT NULL,
    improved_prompt TEXT NOT NULL,
    success_rate REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_hash TEXT UNIQUE NOT NULL,
    problem TEXT NOT NULL,
    solution TEXT NOT NULL,
    task_type TEXT NOT NULL,
    success_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patterns_task_type ON patterns(task_type);
CREATE INDEX IF NOT EXISTS idx_sessions_task_type ON sessions(task_type);
CREATE INDEX IF NOT EXISTS idx_sessions_model ON sessions(model_used);
CREATE INDEX IF NOT EXISTS idx_model_perf_task ON model_performance(task_type);
CREATE INDEX IF NOT EXISTS idx_kb_problem_hash ON knowledge_base(problem_hash);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_task ON prompt_templates(task_type);
"""


def _get_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode and foreign keys enabled."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    """Initialize the database schema if not already present."""
    conn.executescript(SCHEMA_SQL)
    existing = conn.execute(
        "SELECT value FROM schema_meta WHERE key = 'version'"
    ).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO schema_meta (key, value) VALUES (?, ?)",
            ("version", str(SCHEMA_VERSION)),
        )
        conn.commit()


def _classify_task_type(text: str) -> str:
    """Classify a task type from text content using keyword matching."""
    text_lower = text.lower()
    task_keywords: Dict[str, List[str]] = {
        "code_generation": [
            "write", "create", "implement", "build", "develop", "code",
            "function", "class", "module", "script", "program",
        ],
        "code_review": [
            "review", "analyze", "check", "audit", "inspect", "evaluate",
            "assess", "examine", "verify", "validate",
        ],
        "debugging": [
            "debug", "fix", "bug", "error", "issue", "problem", "crash",
            "trace", "exception", "stack trace", "fault",
        ],
        "refactoring": [
            "refactor", "restructure", "reorganize", "clean", "optimize",
            "improve", "simplify", "modularize",
        ],
        "documentation": [
            "document", "comment", "explain", "describe", "readme", "docs",
            "guide", "tutorial", "manual",
        ],
        "testing": [
            "test", "unit test", "integration test", "coverage", "assert",
            "mock", "fixture", "pytest", "jest",
        ],
        "security": [
            "security", "vulnerability", "exploit", "injection", "xss",
            "csrf", "auth", "encrypt", "sanitize", "cve",
        ],
        "data_processing": [
            "parse", "transform", "convert", "extract", "filter", "aggregate",
            "csv", "json", "xml", "database", "sql",
        ],
        "multimodal": [
            "image", "video", "audio", "music", "speech", "vision",
            "generate image", "generate video", "generate audio",
        ],
        "reasoning": [
            "reason", "analyze", "deduce", "infer", "logic", "complex",
            "algorithm", "optimize", "strategy", "architecture",
        ],
    }
    scores: Dict[str, int] = {}
    for task_type, keywords in task_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[task_type] = score
    if scores:
        return max(scores, key=scores.get)  # type: ignore[arg-type]
    return "general"


def _compute_hash(text: str) -> str:
    """Compute a SHA-256 hash of the given text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


class SelfLearningEngine:
    """Stores learned patterns and manages the knowledge base.

    Uses SQLite for persistence. Learns from user interactions and successful
    code generations to improve future responses.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize the SelfLearningEngine.

        Args:
            db_path: Optional custom path for the SQLite database.
        """
        self.db_path = db_path or DB_PATH
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._get_conn()

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None

    def _get_conn(self) -> sqlite3.Connection:
        """Get the active connection, reconnecting if closed."""
        with self._lock:
            if self._conn is None:
                self._conn = _get_db(self.db_path)
                _init_db(self._conn)
            return self._conn

    def __enter__(self) -> SelfLearningEngine:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def record_pattern(
        self,
        task_type: str,
        pattern: str,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a pattern observation.

        Args:
            task_type: The category of task.
            pattern: The pattern string to store.
            success: Whether the pattern was successful.
            metadata: Optional additional metadata dict.
        """
        meta_json = json.dumps(metadata or {})
        conn = self._get_conn()
        existing = conn.execute(
            "SELECT id, success_count, failure_count FROM patterns WHERE task_type = ? AND pattern = ?",
            (task_type, pattern),
        ).fetchone()
        if existing:
            if success:
                conn.execute(
                    "UPDATE patterns SET success_count = ?, last_used = CURRENT_TIMESTAMP, "
                    "confidence = CAST((success_count + 1) AS REAL) / (success_count + 1 + failure_count) "
                    "WHERE id = ?",
                    (existing["success_count"] + 1, existing["id"]),
                )
            else:
                conn.execute(
                    "UPDATE patterns SET failure_count = ?, last_used = CURRENT_TIMESTAMP, "
                    "confidence = CAST(success_count AS REAL) / (success_count + failure_count + 1) "
                    "WHERE id = ?",
                    (existing["failure_count"] + 1, existing["id"]),
                )
        else:
            conn.execute(
                "INSERT INTO patterns (task_type, pattern, success_count, failure_count, confidence, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    task_type,
                    pattern,
                    1 if success else 0,
                    0 if success else 1,
                    1.0 if success else 0.0,
                    meta_json,
                ),
            )
        conn.commit()

    def get_patterns(
        self, task_type: str, min_confidence: float = 0.3, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve patterns for a task type with minimum confidence.

        Args:
            task_type: The task category.
            min_confidence: Minimum confidence threshold (0.0 to 1.0).
            limit: Maximum number of patterns to return.

        Returns:
            List of pattern dicts sorted by confidence descending.
        """
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT pattern, success_count, failure_count, confidence, metadata "
            "FROM patterns WHERE task_type = ? AND confidence >= ? "
            "ORDER BY confidence DESC, success_count DESC LIMIT ?",
            (task_type, min_confidence, limit),
        ).fetchall()
        return [
            {
                "pattern": row["pattern"],
                "success_count": row["success_count"],
                "failure_count": row["failure_count"],
                "confidence": row["confidence"],
                "metadata": json.loads(row["metadata"] or "{}"),
            }
            for row in rows
        ]

    def add_knowledge(
        self, problem: str, solution: str, task_type: str = "general"
    ) -> None:
        """Add a solution to the knowledge base.

        Args:
            problem: Description of the problem.
            solution: The solution text.
            task_type: Category of the problem.
        """
        problem_hash = _compute_hash(problem)
        conn = self._get_conn()
        existing = conn.execute(
            "SELECT id, success_count FROM knowledge_base WHERE problem_hash = ?",
            (problem_hash,),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE knowledge_base SET success_count = ?, solution = ? WHERE id = ?",
                (existing["success_count"] + 1, solution, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO knowledge_base (problem_hash, problem, solution, task_type) "
                "VALUES (?, ?, ?, ?)",
                (problem_hash, problem, solution, task_type),
            )
        conn.commit()

    def search_knowledge(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant solutions.

        Args:
            query: Search query string.
            limit: Maximum results to return.

        Returns:
            List of knowledge entries sorted by relevance.
        """
        terms = [t for t in re.split(r"\s+", query.lower()) if len(t) > 2]
        if not terms:
            return []
        where_clause = " OR ".join(["LOWER(problem) LIKE ?"] * len(terms))
        params = [f"%{t}%" for t in terms]
        conn = self._get_conn()
        rows = conn.execute(
            f"SELECT problem, solution, task_type, success_count FROM knowledge_base "
            f"WHERE {where_clause} ORDER BY success_count DESC LIMIT ?",
            params + [limit],
        ).fetchall()
        return [
            {
                "problem": row["problem"],
                "solution": row["solution"],
                "task_type": row["task_type"],
                "success_count": row["success_count"],
            }
            for row in rows
        ]

    def record_session(self, session_data: Dict[str, Any]) -> str:
        """Record a complete session for learning.

        Args:
            session_data: Dict with keys: id, task_type, model_used, prompt,
                          response_summary, success_score, duration_seconds,
                          tokens_used, user_feedback.

        Returns:
            The session ID.
        """
        sid = session_data.get("id") or _compute_hash(
            f"{session_data.get('prompt', '')}{time.time()}"
        )
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO sessions "
            "(id, task_type, model_used, prompt, response_summary, success_score, "
            "duration_seconds, tokens_used, user_feedback) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                sid,
                session_data.get("task_type", "general"),
                session_data.get("model_used", "unknown"),
                session_data.get("prompt", ""),
                session_data.get("response_summary", ""),
                session_data.get("success_score", 0.0),
                session_data.get("duration_seconds", 0.0),
                session_data.get("tokens_used", 0),
                session_data.get("user_feedback", 0),
            ),
        )
        conn.commit()
        return sid

    def get_session_history(
        self, task_type: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve session history, optionally filtered by task type.

        Args:
            task_type: Optional task type filter.
            limit: Maximum number of sessions to return.

        Returns:
            List of session dicts ordered by most recent first.
        """
        conn = self._get_conn()
        if task_type:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE task_type = ? "
                "ORDER BY created_at DESC LIMIT ?",
                (task_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_top_patterns(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the most successful patterns across all task types.

        Args:
            limit: Maximum number of patterns to return.

        Returns:
            List of pattern dicts sorted by success count.
        """
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT task_type, pattern, success_count, confidence FROM patterns "
            "ORDER BY success_count DESC, confidence DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


class AutoImprover:
    """Analyzes past sessions to identify improvement opportunities.

    Learns user preferences over time and suggests code optimizations
    and prompt improvements.

    Attributes:
        engine: The SelfLearningEngine instance for data access.
    """

    def __init__(self, engine: Optional[SelfLearningEngine] = None) -> None:
        """Initialize the AutoImprover.

        Args:
            engine: Optional SelfLearningEngine instance. Creates one if not provided.
        """
        self.engine = engine or SelfLearningEngine()
        self._owns_engine = engine is None

    def close(self) -> None:
        """Close resources."""
        if self._owns_engine:
            self.engine.close()

    def __enter__(self) -> AutoImprover:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def analyze_sessions(
        self, days: int = 30, task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze past sessions to identify improvement opportunities.

        Args:
            days: Number of days to look back.
            task_type: Optional task type filter.

        Returns:
            Analysis results dict with insights and suggestions.
        """
        conn = self.engine._get_conn()
        since = datetime.now() - timedelta(days=days)
        since_str = since.isoformat()

        if task_type:
            sessions = conn.execute(
                "SELECT * FROM sessions WHERE created_at >= ? AND task_type = ?",
                (since_str, task_type),
            ).fetchall()
        else:
            sessions = conn.execute(
                "SELECT * FROM sessions WHERE created_at >= ?",
                (since_str,),
            ).fetchall()

        if not sessions:
            return {
                "total_sessions": 0,
                "avg_success": 0.0,
                "suggestions": ["No se encontraron sesiones para el período de análisis."],
            }

        total = len(sessions)
        avg_success = sum(s["success_score"] for s in sessions) / total
        avg_duration = sum(s["duration_seconds"] for s in sessions) / total

        model_scores: Dict[str, List[float]] = defaultdict(list)
        task_scores: Dict[str, List[float]] = defaultdict(list)
        for s in sessions:
            model_scores[s["model_used"]].append(s["success_score"])
            task_scores[s["task_type"]].append(s["success_score"])

        suggestions: List[str] = []

        if avg_success < 0.6:
            suggestions.append(
                f"Tasa de éxito general baja ({avg_success:.1%}). "
                "Considera revisar las plantillas de prompts."
            )

        best_model = max(
            model_scores, key=lambda m: sum(model_scores[m]) / len(model_scores[m])
        )
        worst_model = min(
            model_scores, key=lambda m: sum(model_scores[m]) / len(model_scores[m])
        )
        if best_model != worst_model:
            best_avg = sum(model_scores[best_model]) / len(model_scores[best_model])
            worst_avg = sum(model_scores[worst_model]) / len(model_scores[worst_model])
            if best_avg - worst_avg > 0.2:
                suggestions.append(
                    f"Modelo '{best_model}' supera significativamente a '{worst_model}' "
                    f"({best_avg:.1%} vs {worst_avg:.1%}). Prefer '{best_model}'."
                )

        if avg_duration > 30:
            suggestions.append(
                f"Average session duration is high ({avg_duration:.1f}s). "
                "Consider using faster models for simple tasks."
            )

        for task, scores in task_scores.items():
            task_avg = sum(scores) / len(scores)
            if task_avg < 0.4:
                suggestions.append(
                    f"Task type '{task}' has low success rate ({task_avg:.1%}). "
                    "Review patterns and knowledge base for this task type."
                )

        return {
            "total_sessions": total,
            "avg_success": avg_success,
            "avg_duration": avg_duration,
            "best_model": best_model,
            "worst_model": worst_model,
            "model_breakdown": {
                m: {"avg_success": sum(s) / len(s), "count": len(s)}
                for m, s in model_scores.items()
            },
            "task_breakdown": {
                t: {"avg_success": sum(s) / len(s), "count": len(s)}
                for t, s in task_scores.items()
            },
            "suggestions": suggestions,
        }

    def suggest_optimizations(self, code: str, task_type: str = "general") -> List[str]:
        """Suggest code optimizations based on learned patterns.

        Args:
            code: The source code to analyze.
            task_type: The type of task the code relates to.

        Returns:
            List of optimization suggestion strings.
        """
        suggestions: List[str] = []
        patterns = self.engine.get_patterns(task_type, min_confidence=0.5)

        if "for " in code and "range(len(" in code:
            suggestions.append(
                "Consider using enumerate() instead of range(len()) for cleaner iteration."
            )

        if "== None" in code or "!= None" in code:
            suggestions.append(
                "Use 'is None' or 'is not None' instead of == None for identity checks."
            )

        if code.count("except:") > 0:
            suggestions.append(
                "Avoid bare 'except:' clauses. Catch specific exceptions."
            )

        if "import *" in code:
            suggestions.append(
                "Avoid 'import *' as it pollutes the namespace. Use explicit imports."
            )

        if "time.sleep(" in code and task_type == "code_generation":
            suggestions.append(
                "Consider using async/await patterns instead of time.sleep for concurrency."
            )

        for pattern in patterns[:3]:
            if pattern["confidence"] > 0.7:
                suggestions.append(
                    f"Learned pattern (confidence {pattern['confidence']:.0%}): "
                    f"{pattern['pattern']}"
                )

        return suggestions

    def learn_preference(self, key: str, value: str, weight: float = 1.0) -> None:
        """Record a user preference.

        Args:
            key: Preference key (e.g., 'indentation', 'language').
            value: Preference value.
            weight: Importance weight (higher = more important).
        """
        conn = self.engine._get_conn()
        existing = conn.execute(
            "SELECT weight FROM user_preferences WHERE key = ?", (key,)
        ).fetchone()
        if existing:
            new_weight = min(existing["weight"] + weight * 0.1, 10.0)
            conn.execute(
                "UPDATE user_preferences SET value = ?, weight = ?, "
                "updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (value, new_weight, key),
            )
        else:
            conn.execute(
                "INSERT INTO user_preferences (key, value, weight) VALUES (?, ?, ?)",
                (key, value, weight),
            )
        conn.commit()

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a user preference.

        Args:
            key: The preference key.
            default: Default value if not found.

        Returns:
            The preference value or default.
        """
        row = self.engine._get_conn().execute(
            "SELECT value FROM user_preferences WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def get_all_preferences(self) -> Dict[str, str]:
        """Get all stored user preferences.

        Returns:
            Dict of preference key-value pairs.
        """
        rows = self.engine._get_conn().execute(
            "SELECT key, value FROM user_preferences ORDER BY weight DESC"
        ).fetchall()
        return {row["key"]: row["value"] for row in rows}

    def improve_prompt(
        self, task_type: str, original_prompt: str
    ) -> str:
        """Generate an improved prompt based on past successful patterns.

        Args:
            task_type: The type of task.
            original_prompt: The original prompt text.

        Returns:
            An improved prompt string.
        """
        patterns = self.engine.get_patterns(task_type, min_confidence=0.6, limit=5)
        knowledge = self.engine.search_knowledge(original_prompt, limit=3)
        preferences = self.get_all_preferences()

        improved = original_prompt

        if patterns:
            top_patterns = [p["pattern"] for p in patterns[:3]]
            pattern_hint = " Consider these proven approaches: " + "; ".join(top_patterns)
            improved = improved + pattern_hint

        if knowledge:
            relevant = knowledge[0]
            kb_hint = f"\n\nReference solution: {relevant['solution'][:200]}"
            improved = improved + kb_hint

        if "style" in preferences:
            improved = improved + f"\nStyle: {preferences['style']}"
        if "language" in preferences:
            improved = improved + f"\nLanguage: {preferences['language']}"

        existing = self.engine._get_conn().execute(
            "SELECT id, improved_prompt, success_rate FROM prompt_templates "
            "WHERE task_type = ? AND original_prompt = ?",
            (task_type, original_prompt),
        ).fetchone()
        if existing:
            self.engine._get_conn().execute(
                "UPDATE prompt_templates SET usage_count = usage_count + 1 WHERE id = ?",
                (existing["id"],),
            )
        else:
            self.engine._get_conn().execute(
                "INSERT INTO prompt_templates "
                "(task_type, original_prompt, improved_prompt) "
                "VALUES (?, ?, ?)",
                (task_type, original_prompt, improved),
            )
        self.engine._get_conn().commit()

        return improved


class ModelEvolver:
    """Tracks model performance and auto-selects optimal models.

    Maintains performance metrics per model per task type and suggests
    when to switch models based on task characteristics.

    Attributes:
        engine: The SelfLearningEngine instance for data access.
    """

    def __init__(self, engine: Optional[SelfLearningEngine] = None) -> None:
        """Initialize the ModelEvolver.

        Args:
            engine: Optional SelfLearningEngine instance.
        """
        self.engine = engine or SelfLearningEngine()
        self._owns_engine = engine is None

    def close(self) -> None:
        """Close resources."""
        if self._owns_engine:
            self.engine.close()

    def __enter__(self) -> ModelEvolver:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def record_performance(
        self,
        model: str,
        task_type: str,
        success: bool,
        latency: float = 0.0,
        tokens: int = 0,
    ) -> None:
        """Record model performance for a task type.

        Args:
            model: The model identifier.
            task_type: The task category.
            success: Whether the task was successful.
            latency: Response time in seconds.
            tokens: Number of tokens used.
        """
        conn = self.engine._get_conn()
        existing = conn.execute(
            "SELECT * FROM model_performance WHERE model = ? AND task_type = ?",
            (model, task_type),
        ).fetchone()

        if existing:
            new_total = existing["total_requests"] + 1
            new_success = existing["success_count"] + (1 if success else 0)
            new_failure = existing["failure_count"] + (0 if success else 1)
            new_avg_latency = (
                (existing["avg_latency"] * existing["total_requests"] + latency)
                / new_total
            )
            new_avg_tokens = (
                (existing["avg_tokens"] * existing["total_requests"] + tokens)
                / new_total
            )
            conn.execute(
                "UPDATE model_performance SET "
                "success_count = ?, failure_count = ?, avg_latency = ?, "
                "avg_tokens = ?, total_requests = ?, last_used = CURRENT_TIMESTAMP "
                "WHERE model = ? AND task_type = ?",
                (
                    new_success,
                    new_failure,
                    new_avg_latency,
                    int(new_avg_tokens),
                    new_total,
                    model,
                    task_type,
                ),
            )
        else:
            conn.execute(
                "INSERT INTO model_performance "
                "(model, task_type, success_count, failure_count, avg_latency, avg_tokens, total_requests) "
                "VALUES (?, ?, ?, ?, ?, ?, 1)",
                (
                    model,
                    task_type,
                    1 if success else 0,
                    0 if success else 1,
                    latency,
                    tokens,
                ),
            )
        conn.commit()

    def get_best_model(self, task_type: str) -> Optional[str]:
        """Get the best-performing model for a task type.

        Args:
            task_type: The task category.

        Returns:
            The model identifier with the highest success rate, or None.
        """
        row = self.engine._get_conn().execute(
            "SELECT model, "
            "CAST(success_count AS REAL) / MAX(total_requests, 1) as success_rate "
            "FROM model_performance WHERE task_type = ? AND total_requests >= 2 "
            "ORDER BY success_rate DESC, avg_latency ASC LIMIT 1",
            (task_type,),
        ).fetchone()
        return row["model"] if row else None

    def get_model_ranking(
        self, task_type: str
    ) -> List[Dict[str, Any]]:
        """Get a ranked list of models for a task type.

        Args:
            task_type: The task category.

        Returns:
            List of model performance dicts sorted by success rate.
        """
        rows = self.engine._get_conn().execute(
            "SELECT model, success_count, failure_count, avg_latency, avg_tokens, "
            "total_requests, "
            "CAST(success_count AS REAL) / MAX(total_requests, 1) as success_rate "
            "FROM model_performance WHERE task_type = ? "
            "ORDER BY success_rate DESC, avg_latency ASC",
            (task_type,),
        ).fetchall()
        return [dict(row) for row in rows]

    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all model performance metrics grouped by task type.

        Returns:
            Dict mapping task_type to list of model performance dicts.
        """
        rows = self.engine._get_conn().execute(
            "SELECT * FROM model_performance ORDER BY task_type, "
            "CAST(success_count AS REAL) / MAX(total_requests, 1) DESC"
        ).fetchall()
        result: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            result[row["task_type"]].append(dict(row))
        return dict(result)

    def should_switch_model(
        self, current_model: str, task_type: str
    ) -> Tuple[bool, Optional[str]]:
        """Determine if a model switch is recommended.

        Args:
            current_model: The currently used model.
            task_type: The task category.

        Returns:
            Tuple of (should_switch, recommended_model).
        """
        ranking = self.get_model_ranking(task_type)
        if not ranking:
            return False, None

        current_entry = next(
            (r for r in ranking if r["model"] == current_model), None
        )
        best = ranking[0]

        if current_entry is None:
            if best["total_requests"] >= 3:
                return True, best["model"]
            return False, None

        current_rate = current_entry.get("success_rate", 0.0)
        best_rate = best.get("success_rate", 0.0)

        if best["model"] != current_model and best_rate - current_rate > 0.15:
            if best["total_requests"] >= 3:
                return True, best["model"]

        return False, None

    def get_model_recommendation(
        self, task_description: str
    ) -> Dict[str, Any]:
        """Get a model recommendation for a task description.

        Args:
            task_description: Description of the task.

        Returns:
            Recommendation dict with model, confidence, and reasoning.
        """
        task_type = _classify_task_type(task_description)
        best_model = self.get_best_model(task_type)
        ranking = self.get_model_ranking(task_type)

        if best_model:
            return {
                "model": best_model,
                "task_type": task_type,
                "confidence": "high" if ranking and ranking[0]["total_requests"] > 5 else "medium",
                "reasoning": f"Based on {ranking[0]['total_requests']} previous requests "
                f"with {ranking[0].get('success_rate', 0):.0%} success rate.",
            }

        return {
            "model": None,
            "task_type": task_type,
            "confidence": "low",
            "reasoning": "Insufficient data. Using default model selection.",
        }


def learn_from_interaction(session_data: Dict[str, Any]) -> str:
    """Record a session interaction for learning.

    Args:
        session_data: Dict containing session details.

    Returns:
        The session ID.
    """
    with SelfLearningEngine() as engine:
        task_type = session_data.get(
            "task_type",
            _classify_task_type(session_data.get("prompt", "")),
        )
        session_data["task_type"] = task_type
        sid = engine.record_session(session_data)

        if "patterns" in session_data:
            for pattern_info in session_data["patterns"]:
                engine.record_pattern(
                    task_type=pattern_info.get("task_type", task_type),
                    pattern=pattern_info.get("pattern", ""),
                    success=pattern_info.get("success", True),
                    metadata=pattern_info.get("metadata"),
                )

        if "knowledge" in session_data:
            kb_entry = session_data["knowledge"]
            engine.add_knowledge(
                problem=kb_entry.get("problem", ""),
                solution=kb_entry.get("solution", ""),
                task_type=kb_entry.get("task_type", task_type),
            )

        return sid


def get_improved_prompt(task_type: str, original_prompt: str) -> str:
    """Get an improved prompt based on learned patterns.

    Args:
        task_type: The type of task.
        original_prompt: The original prompt text.

    Returns:
        An improved prompt string.
    """
    with AutoImprover() as improver:
        return improver.improve_prompt(task_type, original_prompt)


def get_best_model_for_task(task_description: str) -> Optional[str]:
    """Get the best model for a given task description.

    Args:
        task_description: Description of the task.

    Returns:
        The recommended model identifier, or None.
    """
    with ModelEvolver() as evolver:
        recommendation = evolver.get_model_recommendation(task_description)
        return recommendation.get("model")


def record_outcome(
    session_id: str,
    success_metrics: Dict[str, Any],
) -> None:
    """Record the outcome of a session.

    Args:
        session_id: The session identifier.
        success_metrics: Dict with keys like success_score, model, task_type,
                        latency, tokens, success (bool).
    """
    with SelfLearningEngine() as engine:
        conn = engine._conn
        session = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if session:
            score = success_metrics.get("success_score", 0.0)
            conn.execute(
                "UPDATE sessions SET success_score = ?, user_feedback = ? WHERE id = ?",
                (
                    score,
                    success_metrics.get("user_feedback", 0),
                    session_id,
                ),
            )
            conn.commit()

        model = success_metrics.get("model", "")
        task_type = success_metrics.get(
            "task_type",
            _classify_task_type(session["prompt"] if session else ""),
        )
        if model:
            with ModelEvolver(engine) as evolver:
                evolver.record_performance(
                    model=model,
                    task_type=task_type,
                    success=success_metrics.get("success", False),
                    latency=success_metrics.get("latency", 0.0),
                    tokens=success_metrics.get("tokens", 0),
                )


def auto_tune_parameters() -> Dict[str, Any]:
    """Run automatic parameter tuning based on learning history.

    Analyzes past performance and adjusts internal parameters for
    optimal model selection, prompt improvement, and routing.

    Returns:
        Dict with tuning results and applied changes.
    """
    results: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "changes": [],
        "analysis": {},
    }

    with SelfLearningEngine() as engine:
        with AutoImprover(engine) as improver:
            analysis = improver.analyze_sessions(days=30)
            results["analysis"] = analysis

            if analysis.get("best_model"):
                results["changes"].append(
                    {
                        "type": "model_preference",
                        "value": analysis["best_model"],
                        "reason": "Highest success rate across all tasks",
                    }
                )

        with ModelEvolver(engine) as evolver:
            all_metrics = evolver.get_all_metrics()
            for task_type, models in all_metrics.items():
                if models:
                    best = models[0]
                    if best.get("success_rate", 0) > 0.8:
                        results["changes"].append(
                            {
                                "type": "task_model_mapping",
                                "task_type": task_type,
                                "model": best["model"],
                                "success_rate": best["success_rate"],
                            }
                        )

        top_patterns = engine.get_top_patterns(limit=10)
        results["top_patterns"] = top_patterns

    return results
