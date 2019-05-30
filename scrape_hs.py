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

        if not i%10:
            print('Pages scraped: {0}/{1}'.format(i-min_page, pages), datetime.utcnow())
            conn.commit()


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
            failures.append(soup)
            continue

    return failures

#### scrape all player names

def get_all_players():
    import requests, pyspark
    import sqlite3 as sql
    import pandas as pd
    import pickle as pckl
    from bs4 import BeautifulSoup
    from pyspark.sql.types import DateType
    from pyspark.sql import SparkSession
    from datetime import datetime

    conn = sql.connect('./data/osrs.db')

    spark = SparkSession.builder.appName("osrs").getOrCreate()

    sqlContext = pyspark.sql.SQLContext(spark)

    now = datetime.utcnow()

    players_results = conn.execute('SELECT name, date FROM players_name LIMIT 50').fetchall()
    players_df = pd.DataFrame({'name': [x[0] for x in players_results], 'date': [x[1] for x in players_results]})
    players = sqlContext.createDataFrame(players_df).select('name').repartition(16)

    players_hs = players.rdd.mapPartitions(get_single_player_part)
    players_hs.is_checkpointed = True

    print('Checkpoint enabled: ', players_hs.is_checkpointed,'\nNum partitions: ', players_hs.getNumPartitions())
    print(now)

    results = players_hs.collect()

    # insert dataframe function
    try:
        xp_df, rank_df = data_to_df(results)
    except:
        return results

    print(datetime.utcnow())

    return xp_df, rank_df


# player scraping results into dataframe

def data_to_df(data):

    columns = ['name', 'date', 'overall', 'attack', 'defence', 'strength', 'hitpoints', 'ranged', 'prayer', 'magic',
               'cooking', 'woodcutting', 'fletching', 'fishing', 'firemaking', 'crafting', 'smithing', 'mining',
               'herblore', 'agility', 'thieving', 'slayer', 'farming', 'runecraft', 'hunter', 'construction']

    xp_list, rank_list = [], []

    for row in data:
        xp = [row[0]] + [row[1]] + [int(x) for x in row[2]]
        rank = [row[0]] + [row[1]] + [int(x) for x in row[3]]

        xp_zip = zip(columns, xp)
        rank_zip = zip(columns, rank)

        xp_dict, rank_dict = {}, {}

        for key, value in xp_zip:
            xp_dict[key] = value

        for key, value in rank_zip:
            rank_dict[key] = value

        xp_list.append(xp_dict)
        rank_list.append(rank_dict)

    xp_df = xp_df.append(xp_list)
    rank_df = rank_df.append(rank_list)

    return xp_df, rank_df




def get_single_player_part(players):
    from datetime import datetime
    # base url for api request
    player_url_base = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player='

    i = 0
    now = datetime.utcnow()

    my_list = []

    for player in players:
        name = player['name']
        url = player_url_base + name

        if not i%20:
            now = datetime.utcnow()
        else:
            pass
        i += 1

        try:
            page = requests.get(url).text.replace(u'\n', u' ')
            skills = [i.split(',') for i in page.split()]
            xp = [i[2] for i in skills[0:24]]
            rank = [i[0] for i in skills[0:24]]
            my_list.append(tuple((name, now, xp, rank)))# players_data
        except:
            pass
    return my_list



##### if wanting to scrape for particular skill

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
