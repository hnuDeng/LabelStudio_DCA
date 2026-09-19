"""
Data version control system.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataVersion:
    """Represents a version of data."""

    def __init__(
        self,
        version_id: str,
        data_hash: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ):
        """
        Initialize data version.

        Args:
            version_id: Unique version identifier
            data_hash: Hash of the data
            description: Version description
            metadata: Additional metadata
            parent_id: Parent version ID
        """
        self.version_id = version_id
        self.data_hash = data_hash
        self.description = description
        self.metadata = metadata or {}
        self.parent_id = parent_id
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "data_hash": self.data_hash,
            "description": self.description,
            "metadata": self.metadata,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
        }


class DataVersionControl:
    """Data version control system."""

    def __init__(self, project_id: int):
        """Initialize version control and load from DB."""
        self.project_id = project_id
        self.versions: Dict[str, DataVersion] = {}
        self.current_version: Optional[str] = None
        self._next_version_num = 1

        # Load from DB
        from backend.database import SessionLocal, DBVersionCommit
        with SessionLocal() as db:
            db_commits = db.query(DBVersionCommit).filter(DBVersionCommit.project_id == project_id).all()
            for dbc in db_commits:
                version = DataVersion(
                    version_id=dbc.version_id,
                    data_hash=dbc.data_hash,
                    description=dbc.description,
                    parent_id=dbc.parent_id
                )
                self.versions[version.version_id] = version
                # Extract number from v1, v2...
                try:
                    num = int(version.version_id[1:])
                    self._next_version_num = max(self._next_version_num, num + 1)
                except ValueError:
                    pass

            # Try to guess current version
            if self.versions:
                self.current_version = max(self.versions.values(), key=lambda v: v.created_at).version_id

    def compute_data_hash(self, data: Any) -> str:
        """Compute hash of data."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def create_version(
        self,
        data: Any,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DataVersion:
        """Create a new version."""
        data_hash = self.compute_data_hash(data)
        version_id = f"v{self._next_version_num}"

        version = DataVersion(
            version_id=version_id,
            data_hash=data_hash,
            description=description,
            metadata=metadata,
            parent_id=self.current_version,
        )

        self.versions[version_id] = version
        self.current_version = version_id
        self._next_version_num += 1

        # Persist to DB
        from backend.database import SessionLocal, DBVersionCommit
        with SessionLocal() as db:
            db_commit = DBVersionCommit(
                project_id=self.project_id,
                version_id=version.version_id,
                data_hash=version.data_hash,
                description=version.description,
                parent_id=version.parent_id
            )
            db.add(db_commit)
            db.commit()

        logger.info(f"Created version {version_id} for project {self.project_id}")

        return version

    def get_version(self, version_id: str) -> Optional[DataVersion]:
        """
        Get version by ID.

        Args:
            version_id: Version ID

        Returns:
            DataVersion or None
        """
        return self.versions.get(version_id)

    def list_versions(self) -> List[DataVersion]:
        """
        List all versions.

        Returns:
            List of DataVersion
        """
        return sorted(
            self.versions.values(),
            key=lambda v: v.created_at,
            reverse=True,
        )

    def get_history(self, version_id: Optional[str] = None) -> List[DataVersion]:
        """
        Get version history.

        Args:
            version_id: Starting version ID (None for current)

        Returns:
            List of DataVersion in order
        """
        if version_id is None:
            version_id = self.current_version

        history = []
        current = self.get_version(version_id)

        while current:
            history.append(current)
            current = self.get_version(current.parent_id) if current.parent_id else None

        return list(reversed(history))
