# codex_indexer.py

from __future__ import annotations

import ast
import hashlib
import sqlite3
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".swift": "swift",
}


class CodexIndexer:

    def __init__(
        self,
        root: str = ".",
        database: str = ".codex/index.db",
    ):
        self.root = Path(root).resolve()
        self.database = Path(database)

        self.database.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.db = sqlite3.connect(
            self.database
        )

        self.db.row_factory = sqlite3.Row

        self._initialize_database()

    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    def _initialize_database(self):

        self.db.executescript(
            """
            PRAGMA journal_mode=WAL;
            PRAGMA foreign_keys=ON;

            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE NOT NULL,
                hash TEXT NOT NULL,
                language TEXT,
                size INTEGER,
                modified REAL,
                indexed_at REAL
            );

            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY,
                file_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                kind TEXT,
                line INTEGER,

                FOREIGN KEY(file_id)
                    REFERENCES files(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS
                idx_files_path
            ON files(path);

            CREATE INDEX IF NOT EXISTS
                idx_symbols_name
            ON symbols(name);

            CREATE INDEX IF NOT EXISTS
                idx_symbols_file
            ON symbols(file_id);
            """
        )

        self.db.commit()

    # --------------------------------------------------
    # HASHING
    # --------------------------------------------------

    def file_hash(
        self,
        path: Path,
    ) -> str:

        sha256 = hashlib.sha256()

        with path.open(
            "rb"
        ) as file:

            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                sha256.update(chunk)

        return sha256.hexdigest()

    # --------------------------------------------------
    # FILE DISCOVERY
    # --------------------------------------------------

    def discover_files(self):

        for path in self.root.rglob("*"):

            if not path.is_file():
                continue

            if ".codex" in path.parts:
                continue

            if ".git" in path.parts:
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            yield path

    # --------------------------------------------------
    # PYTHON SYMBOL EXTRACTION
    # --------------------------------------------------

    def extract_python_symbols(
        self,
        path: Path,
    ):

        try:

            source = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(source)

        except Exception:
            return []

        symbols = []

        for node in ast.walk(tree):

            if isinstance(
                node,
                ast.FunctionDef,
            ):
                symbols.append(
                    (
                        node.name,
                        "function",
                        node.lineno,
                    )
                )

            elif isinstance(
                node,
                ast.AsyncFunctionDef,
            ):
                symbols.append(
                    (
                        node.name,
                        "async_function",
                        node.lineno,
                    )
                )

            elif isinstance(
                node,
                ast.ClassDef,
            ):
                symbols.append(
                    (
                        node.name,
                        "class",
                        node.lineno,
                    )
                )

        return symbols

    # --------------------------------------------------
    # GENERIC SYMBOL EXTRACTION
    # --------------------------------------------------

    def extract_symbols(
        self,
        path: Path,
        language: str,
    ):

        if language == "python":
            return self.extract_python_symbols(
                path
            )

        return []

    # --------------------------------------------------
    # INDEX FILE
    # --------------------------------------------------

    def index_file(
        self,
        path: Path,
    ):

        relative_path = str(
            path.relative_to(self.root)
        )

        language = SUPPORTED_EXTENSIONS[
            path.suffix.lower()
        ]

        file_hash = self.file_hash(
            path
        )

        stat = path.stat()

        existing = self.db.execute(
            """
            SELECT id, hash
            FROM files
            WHERE path = ?
            """,
            (relative_path,),
        ).fetchone()

        # Skip unchanged files
        if (
            existing
            and existing["hash"] == file_hash
        ):
            return "unchanged"

        # Remove old index
        if existing:

            self.db.execute(
                """
                DELETE FROM files
                WHERE id = ?
                """,
                (existing["id"],),
            )

        # Insert file
        cursor = self.db.execute(
            """
            INSERT INTO files (
                path,
                hash,
                language,
                size,
                modified,
                indexed_at
            )
            VALUES (?, ?, ?, ?, ?, strftime('%s','now'))
            """,
            (
                relative_path,
                file_hash,
                language,
                stat.st_size,
                stat.st_mtime,
            ),
        )

        file_id = cursor.lastrowid

        # Extract symbols
        symbols = self.extract_symbols(
            path,
            language,
        )

        for name, kind, line in symbols:

            self.db.execute(
                """
                INSERT INTO symbols (
                    file_id,
                    name,
                    kind,
                    line
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_id,
                    name,
                    kind,
                    line,
                ),
            )

        self.db.commit()

        return "indexed"

    # --------------------------------------------------
    # FULL INDEX
    # --------------------------------------------------

    def index_project(self):

        indexed = 0
        unchanged = 0

        for path in self.discover_files():

            result = self.index_file(
                path
            )

            if result == "indexed":
                indexed += 1

            else:
                unchanged += 1

        return {
            "indexed": indexed,
            "unchanged": unchanged,
        }

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(
        self,
        query: str,
    ):

        return self.db.execute(
            """
            SELECT
                symbols.name,
                symbols.kind,
                symbols.line,
                files.path
            FROM symbols
            JOIN files
                ON symbols.file_id =
                   files.id
            WHERE symbols.name LIKE ?
            ORDER BY
                files.path,
                symbols.line
            """,
            (
                f"%{query}%",
            ),
        ).fetchall()

    # --------------------------------------------------
    # STATS
    # --------------------------------------------------

    def stats(self):

        files = self.db.execute(
            "SELECT COUNT(*) FROM files"
        ).fetchone()[0]

        symbols = self.db.execute(
            "SELECT COUNT(*) FROM symbols"
        ).fetchone()[0]

        return {
            "root": str(self.root),
            "database": str(
                self.database
            ),
            "files": files,
            "symbols": symbols,
        }

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------

    def close(self):

        self.db.close()


# ======================================================
# CLI
# ======================================================

if __name__ == "__main__":

    indexer = CodexIndexer()

    print(
        "Indexing:",
        indexer.root,
    )

    result = (
        indexer.index_project()
    )

    print(
        "Index complete:",
        result,
    )

    print(
        "Statistics:",
        indexer.stats(),
    )

    indexer.close()
