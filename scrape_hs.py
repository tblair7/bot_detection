# Author: Tyler Blair
# Website: https://www.github.com/tblair7

def scrape_names_df(min_rank, max_rank, skill):
    import requests
    import sqlite3 as sql
    from datetime import datetime
    from bs4 import BeautifulSoup
    import hs_tables
    import pandas as pd

    conn = sql.connect('data/osrs.db')

    # create players table if it doesn't already exist
    # attributes: name, date, skill
    hs_tables.create_players_table(conn)

    # get skill name for inserting attribute in datebase table
    skills = ["Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged", "Prayer", "Magic", "Cooking",
              "Woodcutting", "Fletching", "Fishing", "Firemaking", "Crafting", "Smithing", "Mining", "Herblore",
              "Agility", "Thieving", "Slayer", "Farming", "Runecraft", "Hunter", "Construction"]
    skill_name = skills[skill]

    # time in utc for later time series analysis
    now = datetime.utcnow()
    time = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(now.year, now.month, now.day,
                                                                now.hour, now.minute, now.second)

    total_base = 'https://secure.runescape.com/m=hiscore_oldschool/overall.ws?table={0}&page='.format(skill)
    #player_url_base = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player='

    # range of pages to scrape results
    min_page = min_rank//25
    max_page = max_rank//25
    pages = max_page - min_page
    #url_no_page = ranking_url_base + 'table={22}&page='.format(table_num)

    df = pd.DataFrame({'name': [],
                       'date': [],
                       'skill': [],
                       'rank': []})

    for i in range(min_page, max_page):

        url = total_base + str(i)
        soup = BeautifulSoup(requests.get(url).text)
        try:
            table = soup.find("tbody")
            for row in table.findAll("tr"):
                player = row.findAll("td")
                # cols = [rank, name, level, xp]
                cols = [element.text.strip() for element in player]
                #name = cols[1].replace(u'\xa0', u' ')

                if cols[1]:
                    name = cols[1].replace(u'\xa0', u' ')
                    #print(name)
                    rank = int(cols[0].replace(u',', u''))
                    try:
                        df = df.append({'name': name,
                                        'date': time,
                                        'skill': skill_name,
                                        'rank': rank},
                                        ignore_index = True)
                    except:
                        print('Failed entry:', cols)
                        continue

                else:
                    continue
        # create catch here
        except:
            print(soup[0:50])
            failures.append(soup)
            continue




        if not i%20:
            print('Pages scraped: {0}/{1}'.format(i-min_page, pages), datetime.utcnow())
        else:
            continue

    return df

def scrape_names(min_rank, max_rank, skill):
    import requests
    import sqlite3 as sql
    from datetime import datetime
    from bs4 import BeautifulSoup
    import hs_tables

    conn = sql.connect('data/osrs.db')

    # create players table if it doesn't already exist
    # attributes: name, date, skill
    hs_tables.create_players_table(conn)

    #hs_tables.create_players_table(conn)

    # get skill name for inserting attribute in datebase table
    skills = ["Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged", "Prayer", "Magic", "Cooking",
              "Woodcutting", "Fletching", "Fishing", "Firemaking", "Crafting", "Smithing", "Mining", "Herblore",
              "Agility", "Thieving", "Slayer", "Farming", "Runecraft", "Hunter", "Construction"]
    skill_name = skills[skill]

    # time in utc for later time series analysis
    now = datetime.utcnow()
    time = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(now.year, now.month, now.day,
                                                                now.hour, now.minute, now.second)

    total_base = 'https://secure.runescape.com/m=hiscore_oldschool/overall.ws?table={0}&page='.format(skill)
    #player_url_base = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player='

    # range of pages to scrape results
    min_page = min_rank//25
    max_page = max_rank//25
    pages = max_page - min_page
    #url_no_page = ranking_url_base + 'table={22}&page='.format(table_num)

    failures = []

    for i in range(min_page, max_page):

        url = total_base + str(i)
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        try:
            table = soup.find("tbody")
        # create catch here
        except:
            return soup

        if table:
            for row in table.findAll("tr"):
                player = row.findAll("td")
                # cols = [rank, name, level, xp]
                cols = [element.text.strip() for element in player]
                #name = cols[1].replace(u'\xa0', u' ')

                if cols[1]:
                    name = cols[1].replace(u'\xa0', u' ')
                    #print(name)
                    rank = int(cols[0].replace(u',', u''))
                    try:
                        conn.execute('''INSERT OR IGNORE INTO players_name(name, date, skill, rank) VALUES (?,?,?,?)''',(name, time, skill_name, int(rank)))
                    except:
                        print('Failed:', cols)
                        continue

                else:
                    continue
        else:
            failures.append(soup)
            continue

        if not i%10:
            print('Pages scraped: {0}/{1}'.format(i-min_page, pages), datetime.utcnow())
            conn.commit()
        else:
            continue

    return failures


def get_player(conn, skill):

    import hs_tables
    from datetime import datetime
    import sqlite3 as sql
    import requests

    # base url for api request
    player_url_base = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player='

    skills = ["Overall", "Attack", "Defence", "Strength", "Hitpoints", "Ranged", "Prayer", "Magic", "Cooking",
              "Woodcutting", "Fletching", "Fishing", "Firemaking", "Crafting", "Smithing", "Mining", "Herblore",
              "Agility", "Thieving", "Slayer", "Farming", "Runecraft", "Hunter", "Construction"]
    skill_name = skills[skill]
    #print(skill_name)

    hs_tables.create_hs_tables(conn)

    players = conn.execute('''SELECT name from players_name WHERE skill = (?)''', (skill_name,)).fetchall()
    num_players = len(players)

    now = datetime.utcnow()
    time = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(now.year, now.month, now.day,
                                                                now.hour, now.minute, now.second)
    failed = []
    num = 0

    for player in players:
        # sql returns list of tuples, this isolates the name
        name = player[0]
        url = player_url_base + name

        num += 1
        if not num%20:
            print('Players scraped: {0}/{1}'.format(num, num_players), datetime.utcnow() - now)
        else:
            pass

        try:
            page = requests.get(url).text.replace(u'\n', u' ')
            skills = [i.split(',') for i in page.split()]
            xp = [i[2] for i in skills[0:24]]
            rank = [i[0] for i in skills[0:24]]
        except:
            print(name)
            failed.append(name)
            continue

        conn.execute('''INSERT INTO players_xp VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', [name, time] + xp)
        conn.execute('''INSERT INTO players_rank VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', [name, time] + rank)

    return failed


if __name__ == "__main__":
    # execute only if run as a script
    main()
