import sqlite3 as lite

def create_db():
    con = lite.connect('players.db')
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS players")
        cur.execute("DROP TABLE IF EXISTS dice")
        cur.execute("DROP TABLE IF EXISTS status")
        cur.execute("DROP TABLE IF EXISTS player")
        cur.execute("CREATE TABLE players (name TEXT, game_id TEXT)")
        cur.execute("CREATE TABLE dice (d1 INT, d2 INT, d3 INT, d4 INT, d5 INT, d6 INT, game_id TEXT)")
        cur.execute("CREATE TABLE status (round INT, game_id TEXT)")
        cur.execute("CREATE TABLE player (id INT, p_left_id INT, p_right_id INT, rel_l TEXT, rel_r TEXT, game_id TEXT)")
    con.close()

create_db()
