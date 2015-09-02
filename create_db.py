import sqlite3 as lite

def create_db(filename='fiasco.db'):
    con = lite.connect(filename)
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS dice")
        cur.execute("DROP TABLE IF EXISTS status")
        cur.execute("DROP TABLE IF EXISTS player")
        #cur.execute("DROP TABLE IF EXISTS sub_relationship")
        #cur.execute("CREATE TABLE relationship (id_num INT, p1_role TEXT, p2_role TEXT)")
        #cur.execute("CREATE TABLE sub_relationship (relationship_id INT, p1 BOOLEAN, p2 BOOLEAN)")
        cur.execute("CREATE TABLE player (id_num INT, name TEXT, p_left_name TEXT, p_right_name TEXT, "
                    "rel_l_id INT, rel_l_role INT, rel_l_sub1 INT, rel_l_sub2 INT, "
                    "rel_r_id INT, rel_r_role INT, rel_r_sub1 INT, rel_r_sub2 INT, "
                    "game_id TEXT)")
        cur.execute("CREATE TABLE dice (d1 INT, d2 INT, d3 INT, d4 INT, d5 INT, d6 INT, game_id TEXT)")
        cur.execute("CREATE TABLE status (round INT, game_id TEXT)")
        
        
        #cur.execute("CREATE TABLE player (id INT, p_left_id INT, p_right_id INT, rel_l TEXT, rel_r TEXT, game_id TEXT)")
    con.close()

if __name__ == '__main__':
    create_db()
