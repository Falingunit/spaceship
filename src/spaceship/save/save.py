from __future__ import annotations

import json
from typing import Any, Iterable, Mapping

import mysql.connector


class Manager:
    """MySQL-backed save system.

    Tables:
      - events:   optional labels/metadata for why a state was saved
      - profiles: a save slot
      - states:   JSON payload per save, with one marked as latest via `isLatest`
    """

    def __init__(self, host: str, user: str, password: str, database: str):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        # Dict cursor makes column access clearer.
        self.cursor = self.connection.cursor(dictionary=True)

    # --- Schema -----------------------------------------------------------------
    def initialize_database(self, events: Iterable[Mapping[str, Any]] | None = None):
        """Create tables and optionally seed event metadata."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                metadata JSON NOT NULL
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                metadata JSON NOT NULL
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS states (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data JSON NOT NULL,
                isLatest BOOLEAN NOT NULL DEFAULT TRUE,
                profileId INT NOT NULL,
                eventId INT,
                timeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                      ON UPDATE CURRENT_TIMESTAMP,
                mainBranch BOOLEAN NOT NULL DEFAULT TRUE,

                CONSTRAINT fk_states_profile
                  FOREIGN KEY (profileId) REFERENCES profiles(id)
                  ON DELETE CASCADE
                  ON UPDATE CASCADE,

                CONSTRAINT fk_states_event
                  FOREIGN KEY (eventId) REFERENCES events(id),

                UNIQUE KEY uniq_latest_per_profile (profileId, isLatest)
            )
            """
        )

        if events:
            for event in events:
                name = event.get("name") or "event"
                metadata = json.dumps(event)
                self.cursor.execute(
                    """
                    INSERT IGNORE INTO events (name, metadata)
                    VALUES (%s, %s)
                    """,
                    (name, metadata),
                )

        self.connection.commit()

    # Backwards compatibility with previous typo.
    intialize_database = initialize_database

    # --- Profiles ---------------------------------------------------------------
    def add_profile(self, name: str, profile_metadata: Mapping[str, Any] | None = None) -> int:
        """Create a profile if it does not exist. Returns profile id."""
        metadata = json.dumps(profile_metadata or {})
        self.cursor.execute(
            """
            INSERT IGNORE INTO profiles (name, metadata)
            VALUES (%s, %s)
            """,
            (name, metadata),
        )
        self.connection.commit()

        # Fetch id (INSERT IGNORE may have skipped insert)
        self.cursor.execute(
            "SELECT id FROM profiles WHERE name = %s",
            (name,),
        )
        row = self.cursor.fetchone()
        if not row:
            raise ValueError(f"Failed to create or fetch profile '{name}'.")
        return int(row["id"])

    def get_profile_id(self, name: str) -> int | None:
        """Return the profile id for the given name, or None if missing."""
        self.cursor.execute(
            "SELECT id FROM profiles WHERE name = %s",
            (name,),
        )
        row = self.cursor.fetchone()
        return int(row["id"]) if row else None

    def get_or_create_profile(self, name: str, profile_metadata: Mapping[str, Any] | None = None) -> int:
        """Fetch a profile id by name, creating it if it does not exist."""
        existing = self.get_profile_id(name)
        if existing is not None:
            return existing
        return self.add_profile(name, profile_metadata)

    # --- Saving -----------------------------------------------------------------
    def _resolve_event(self, event_name: str | None, metadata: Mapping[str, Any] | None) -> int | None:
        if not event_name:
            return None

        meta_json = json.dumps(metadata or {})
        self.cursor.execute(
            """
            INSERT IGNORE INTO events (name, metadata)
            VALUES (%s, %s)
            """,
            (event_name, meta_json),
        )
        self.connection.commit()

        self.cursor.execute("SELECT id FROM events WHERE name = %s", (event_name,))
        row = self.cursor.fetchone()
        return int(row["id"]) if row else None

    def save_state(
        self,
        profile_id: int,
        state_data: Mapping[str, Any] | Any,
        *,
        event: str | None = None,
        event_metadata: Mapping[str, Any] | None = None,
    ) -> int:
        """Persist a new state and mark it as the latest for the profile."""
        payload = json.dumps(state_data)
        event_id = self._resolve_event(event, event_metadata)

        # Move previous latest off the main branch and insert new latest row.
        self.cursor.execute(
            "UPDATE states SET isLatest = FALSE WHERE profileId = %s AND isLatest = TRUE",
            (profile_id,),
        )
        self.cursor.execute(
            """
            INSERT INTO states (data, isLatest, profileId, eventId)
            VALUES (%s, TRUE, %s, %s)
            """,
            (payload, profile_id, event_id),
        )
        self.connection.commit()
        return int(self.cursor.lastrowid)

    # --- Loading ----------------------------------------------------------------
    def get_state(self, profile_id: int) -> dict[str, Any] | None:
        self.cursor.execute(
            """
            SELECT id, data, timeStamp, eventId
            FROM states
            WHERE profileId = %s AND isLatest = TRUE
            """,
            (profile_id,),
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(row["id"]),
            "data": json.loads(row["data"]),
            "timeStamp": row["timeStamp"],
            "eventId": row["eventId"],
        }

    def get_state_history(self, profile_id: int):
        self.cursor.execute(
            """
            SELECT id, data, timeStamp, eventId, isLatest
            FROM states
            WHERE profileId = %s
            ORDER BY timeStamp DESC
            """,
            (profile_id,),
        )
        rows = self.cursor.fetchall()
        return [
            {
                "id": int(row["id"]),
                "data": json.loads(row["data"]),
                "timeStamp": row["timeStamp"],
                "eventId": row["eventId"],
                "isLatest": bool(row["isLatest"]),
            }
            for row in rows
        ]

    # Compatibility alias.
    get_latest_state = get_state

    def get_previous_state(self, state_id: int, profile_id: int):
        self.cursor.execute(
            """
            SELECT data FROM states
            WHERE id = %s AND profileId = %s
            """,
            (state_id, profile_id),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        return json.loads(row["data"])

    # --- Rollback ---------------------------------------------------------------
    def rollback_to_state(self, state_id: int, profile_id: int):
        """Mark the given state as the latest for this profile."""
        self.cursor.execute(
            """
            SELECT id FROM states WHERE id = %s AND profileId = %s
            """,
            (state_id, profile_id),
        )
        if not self.cursor.fetchone():
            raise ValueError("State does not exist for this profile.")

        self.cursor.execute(
            "UPDATE states SET isLatest = FALSE WHERE profileId = %s",
            (profile_id,),
        )
        self.cursor.execute(
            "UPDATE states SET isLatest = TRUE WHERE id = %s AND profileId = %s",
            (state_id, profile_id),
        )
        self.connection.commit()

    # --- Maintenance ------------------------------------------------------------
    def clear_profile_states(self, profile_id: int):
        self.cursor.execute(
            "DELETE FROM states WHERE profileId = %s",
            (profile_id,),
        )
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
