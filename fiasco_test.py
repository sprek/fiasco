import unittest
import tempfile
import os
import create_db
import sqlite3
import player
import playset

# id, name, p_left_id, p_right_id,
# rel_l_id, rel_l_role, rel_l_sub1, rel_l_sub2
# rel_r_id, rel_r_role, rel_r_sub1, rel_r_sub2

TEST_PLAYER_VALUES1= [1, 'daniel', 0, 2,
                      11, 1, 3, 2,
                      23, 2, 0, 0, '0']
TEST_PLAYER_VALUES2= [2, 'mary', 1, 3,
                      3, 1, 0, 0,
                      14, 2, 0, 0, '0']

TEST_PLAYSET='/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt'

#def create_2players_test_data(db):
#    cur = db.cursor()
#    cur.execute("INSERT INTO player (id, name, p_left_id, p_right_id, "
#                 "rel_l_id, rel_l_role, rel_l_sub1, rel_l_sub2, "
#                 "rel_r_id, rel_r_role, rel_r_sub1, rel_r_sub2, "
#                 "game_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                 TEST_PLAYER_VALUES1)
#    cur.execute("INSERT INTO player (id, name, p_left_id, p_right_id, "
#                 "rel_l_id, rel_l_role, rel_l_sub1, rel_l_sub2, "
#                 "rel_r_id, rel_r_role, rel_r_sub1, rel_r_sub2, "
#                 "game_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                 TEST_PLAYER_VALUES2)
#    db.commit()

class FiascoTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd = tempfile.mkstemp()
        print ("CREATED DB: " + self.db_fd[1])
        create_db.create_db(self.db_fd[1])
        self.db = sqlite3.connect(self.db_fd[1])

    def tearDown(self):
        os.close(self.db_fd[0])
        os.remove(self.db_fd[1])

    def test_set_get_players(self):
        """ Tests the following functions:
        player.insert_player_into_db
        player.get_players_from_db
        """
        test_player = player.Player (*TEST_PLAYER_VALUES1)
        player.insert_player_into_db(test_player, self.db)
        db_player = player.get_players_from_db(test_player.game_id, self.db)[0]
        assert db_player == test_player

    def test_parse_playset(self):
        """ Tests:
        playset.parse_playset
        """
        test_playset = playset.parse_playset(TEST_PLAYSET)
        assert(test_playset.name == 'Main Street')
        assert(len(test_playset.relationships) == 6)
        assert(len(test_playset.needs) == 6)
        assert(len(test_playset.locations) == 6)
        assert(len(test_playset.objects) == 6)

        
        for entry in test_playset.relationships:
            print ("RELATIONSHIP: " + entry.title + " LEN: " + str(len(entry.entries)))
            
            assert(len(entry.entries) == 6)
        for entry in test_playset.needs:
            assert(len(entry.entries) == 6)
        for entry in test_playset.locations:
            assert(len(entry.entries) == 6)
        for entry in test_playset.objects:
            assert(len(entry.entries) == 6)

if __name__ == '__main__':
    unittest.main()
    
