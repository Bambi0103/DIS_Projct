CREATE TABLE teams (
    team_name TEXT PRIMARY KEY
);

INSERT INTO teams (team_name)
SELECT DISTINCT national_team
FROM players;

ALTER TABLE players
ADD CONSTRAINT fk_national_team
FOREIGN KEY (national_team) REFERENCES teams(team_name);