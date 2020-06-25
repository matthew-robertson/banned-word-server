CREATE TABLE 'plan' (
	plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
	name Varchar NOT NULL,
	created_at Varchar NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at Varchar NOT NULL DEFAULT CURRENT_TIMESTAMP,
  bannings_allowed INTEGER NOT NULL
);

INSERT INTO plan (name, bannings_allowed) select "Base", 3;
INSERT INTO plan (name, bannings_allowed) select "Premium", 10;

CREATE TABLE 'server_plan' (
	plan_id INTEGER NOT NULL,
	server_id Varchar NOT NULL,
	created_at Varchar NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at Varchar NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(server_id) REFERENCES server(server_id),
	FOREIGN KEY(plan_id) REFERENCES plan(plan_id)
);

INSERT INTO server_plan (server_id, plan_id)
SELECT server_id, 1 from server;