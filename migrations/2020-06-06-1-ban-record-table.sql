CREATE TABLE 'ban_record' (
	ban_id int NOT NULL,
	record_seconds int NOT NULL,
	created_at Varchar NOT NULL,
  updated_at Varchar DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(ban_id) REFERENCES server_banned_word(rowid)
);

INSERT INTO ban_record (ban_id, record_seconds, created_at, updated_at)
SELECT rowid as ban_id, 0 as record_seconds, datetime('now')	as created_at, datetime('now')	as updated_at from server_banned_word;