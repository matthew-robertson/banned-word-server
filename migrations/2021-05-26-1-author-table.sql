CREATE TABLE 'author' (
    user_id int NOT NULL PRIMARY KEY,
    infraction_count int DEFAULT 0,
    created_at Varchar NOT NULL,
    updated_at Varchar DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE 'author_infraction' (
    user_id int NOT NULL,
    ban_id int NOT NULL,
    infraction_count int DEFAULT 0,
    created_at Varchar NOT NULL,
    updated_at Varchar DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, ban_id),
    FOREIGN KEY(ban_id) REFERENCES server_banned_word(rowid),
    FOREIGN KEY(user_id) REFERENCES server_banned_word(user_id)

);
