# Author: Tyler Blair
# Website: https://www.github.com/tblair7

# create table of players within database if it doesn't already exist
def create_players_table(conn):
    import sqlite3 as sql
    conn.execute('''CREATE TABLE IF NOT EXISTS players_name(
                    "name" TEXT,
                    "date" DATETIME NOT NULL,
                    "skill" TEXT,
                    "rank" INTEGER)''')
    conn.commit()
    return

def create_hs_tables(conn):

    conn.execute('''CREATE TABLE IF NOT EXISTS players_xp (
                    name TEXT NOT NULL,
                    date DATETIME NOT NULL,
                    overall INTEGER,
                    attack INTEGER,
                    defence INTEGER,
                    strength INTEGER,
                    hitpoints INTEGER,
                    ranged INTEGER,
                    prayer INTEGER,
                    magic INTEGER,
                    cooking INTEGER,
                    woodcutting INTEGER,
                    fletching INTEGER,
                    fishing INTEGER,
                    firemaking INTEGER,
                    crafting INTEGER,
                    smithing INTEGER,
                    mining INTEGER,
                    herblore INTEGER,
                    agility INTEGER,
                    thieving INTEGER,
                    slayer INTEGER,
                    farming INTEGER,
                    runecraft INTEGER,
                    hunter INTEGER,
                    construction INTEGER)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS players_rank (
                    name TEXT NOT NULL,
                    date DATETIME NOT NULL,
                    overall INTEGER,
                    attack INTEGER,
                    defence INTEGER,
                    strength INTEGER,
                    hitpoints INTEGER,
                    ranged INTEGER,
                    prayer INTEGER,
                    magic INTEGER,
                    cooking INTEGER,
                    woodcutting INTEGER,
                    fletching INTEGER,
                    fishing INTEGER,
                    firemaking INTEGER,
                    crafting INTEGER,
                    smithing INTEGER,
                    mining INTEGER,
                    herblore INTEGER,
                    agility INTEGER,
                    thieving INTEGER,
                    slayer INTEGER,
                    farming INTEGER,
                    runecraft INTEGER,
                    hunter INTEGER,
                    construction INTEGER)''')

    conn.commit()


def insert_players_xp(conn, name, skills_list):

    # skills list is a nested list in the form of: [['rank, level, xp'], ['rank, level, xp'], ...]
    conn.execute('''INSERT INTO players_xp (name, date, overall, attack, defence, strength, hitpoints, ranged, prayer,
    magic, cooking, woodcutting, fletching, fishing, firemaking, crafting, smithing, mining, herblore, agility, thieving,
    slayer, farming, runecraft, hunter, construction)
    VALUES ()

    )''')

if __name__ == "__main__":
    # execute only if run as a script
    main()
