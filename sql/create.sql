CREATE TABLE IF NOT EXISTS "Folders" (
	"id"	INTEGER UNIQUE,
	"org_path"	TEXT NOT NULL UNIQUE,
	"sym_path"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "People" (
    "id"	INTEGER UNIQUE,
    "name"	TEXT NOT NULL UNIQUE,
    "encoding" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "Files" (
	"id"	INTEGER UNIQUE,
	"path"	TEXT NOT NULL UNIQUE,
	"hash"  TEXT,
	"caption" TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE INDEX IF NOT EXISTS "idx_hash" on "Files" (hash asc);

CREATE TABLE IF NOT EXISTS "Tags" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "FileTags" (
	"file_id"	INTEGER,
	"tag_id"	INTEGER,
	FOREIGN KEY("file_id") REFERENCES "Files"("id"),
	FOREIGN KEY("tag_id") REFERENCES "Tags"("id")
);

CREATE TABLE IF NOT EXISTS Collections (
	"id" 	INTEGER UNIQUE,
	"name"  TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "FileCollections" (
	"collection_id"	INTEGER,
	"file_id"	INTEGER,
	FOREIGN KEY("collection_id") REFERENCES "Collections"("id"),
	FOREIGN KEY("file_id") REFERENCES "Files"("id")
);

CREATE TABLE IF NOT EXISTS "Scenes" (
	"id" 	INTEGER UNIQUE,
	"file_id"	INTEGER,
	"start" TEXT NOT NULL,
	"end" 	TEXT NOT NULL,
	FOREIGN KEY("file_id") REFERENCES "Files"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "SceneTags" (
	"scene_id"	INTEGER,
	"tag_id"	INTEGER,
	FOREIGN KEY("scene_id") REFERENCES "Scenes"("id"),
	FOREIGN KEY("tag_id") REFERENCES "Tags"("id")
);