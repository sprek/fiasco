import unittest
import tempfile
import os
import create_db
import sqlite3
import player
import playset
import dice
import game_control

# id, name, p_left_name, p_right_name,
# rel_l_id, rel_l_role, rel_l_sub1, rel_l_sub2
# rel_r_id, rel_r_role, rel_r_sub1, rel_r_sub2

GAME_ID1='0'
TEST_PLAYER_VALUES1= [1, 'daniel', '', '',
                      11, 1, 3, 2,
                      23, 2, 0, 0, GAME_ID1]
TEST_PLAYER_VALUES2= [2, 'mary', '', '',
                      3, 1, 0, 0,
                      14, 2, 0, 0, GAME_ID1]

TEST_PLAYER_VALUES3= [2, 'fred', '', '',
                      3, 1, 0, 0,
                      14, 2, 0, 0, GAME_ID1]

TEST_PLAYSET='/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt'

def clear_tables(db):
    cur = db.cursor()
    cur.execute('DELETE FROM player')
    cur.execute('DELETE FROM dice')
    db.commit()

class FiascoTestCase(unittest.TestCase):
    """ Unit tests for fiasco game
    """
    def setUp(self):
        self.db_fd = tempfile.mkstemp()
        create_db.create_db(self.db_fd[1])
        self.db = sqlite3.connect(self.db_fd[1])

    def tearDown(self):
        os.close(self.db_fd[0])
        os.remove(self.db_fd[1])

    def test_players_db(self):
        """ Testing player functions
        player.insert_player_into_db
        player.get_players_from_db
        player.get_player_from_db_by_name
        player.update_player_by_name
        """
        clear_tables(self.db)

        # test empty players
        test_players = player.get_players_from_db(GAME_ID1, self.db)
        assert (test_players == [])
        test_names = player.get_player_names_from_db(GAME_ID1, self.db)
        assert (test_names == [])
        
        # insert player
        test_player = player.Player (*TEST_PLAYER_VALUES1)
        player.insert_player_into_db(test_player, self.db)
        db_player = player.get_players_from_db(test_player.game_id, self.db)[0]
        assert db_player == test_player
        # get player
        db_player2 = player.get_player_from_db_by_name(db_player.name, db_player.game_id, self.db)
        assert(db_player2 == db_player)
        # update player
        cur_id = db_player.id_num
        db_player.id_num = cur_id + 1
        player.update_player_by_name(db_player, self.db)
        # get player
        new_db_player = player.get_player_from_db_by_name(
            db_player.name, db_player.game_id, self.db)
        assert(new_db_player.id_num == db_player.id_num)

    def test_parse_playset(self):
        """ Testing playset functions
        playset.parse_playset
        """
        test_playset = playset.parse_playset(TEST_PLAYSET)
        assert(test_playset.name == 'Main Street')
        assert(len(test_playset.relationships) == 6)
        assert(len(test_playset.needs) == 6)
        assert(len(test_playset.locations) == 6)
        assert(len(test_playset.objects) == 6)
        
        for entry in test_playset.relationships:
            assert(len(entry.entries) == 6)
        for entry in test_playset.needs:
            assert(len(entry.entries) == 6)
        for entry in test_playset.locations:
            assert(len(entry.entries) == 6)
        for entry in test_playset.objects:
            assert(len(entry.entries) == 6)

    def test_dice(self):
        """ Testsing dice functions
        dice.get_dice_from_db
        dice.insert_dice_into_db
        dice.get_dice_from_db
        """
        clear_tables(self.db)
        num_players = 4
        test_dice = dice.initialize_dice(num_players,'0')
        total = 0
        for key in test_dice.dice:
            total += test_dice.dice[key]
        assert (total == 4 * num_players)
        # insert dice
        dice.insert_dice_into_db(test_dice, self.db)
        # get dice
        db_dice = dice.get_dice_from_db(test_dice.game_id, self.db)
        assert(db_dice == test_dice)

    def test_clear(self):
        test_dice = dice.initialize_dice(3,'0')
        dice.insert_dice_into_db(test_dice, self.db)
        test_player = player.Player (*TEST_PLAYER_VALUES1)
        player.insert_player_into_db(test_player, self.db)
        assert len(player.get_players_from_db(test_player.game_id, self.db)) > 0
        assert len(dice.get_dice_from_db(test_dice.game_id, self.db).dice) > 0
        clear_tables(self.db)
        assert len(player.get_players_from_db(test_player.game_id, self.db)) == 0
        assert dice.get_dice_from_db(test_dice.game_id, self.db) == None

    def test_game_control(self):
        """ Testing game_control functions
        game_control.initialize_game
        """
        clear_tables(self.db)
        p1 = player.Player(*TEST_PLAYER_VALUES1)
        p2 = player.Player(*TEST_PLAYER_VALUES2)
        p3 = player.Player(*TEST_PLAYER_VALUES3)
        # insert players into db
        player.insert_player_into_db(p1, self.db)
        player.insert_player_into_db(p2, self.db)
        player.insert_player_into_db(p3, self.db)
        # initialize game
        game_control.initialize_game(p1.game_id, self.db)
        # get the updated player information
        p1 = player.get_player_from_db_by_name(p1.name, p1.game_id, self.db)
        p2 = player.get_player_from_db_by_name(p2.name, p2.game_id, self.db)
        p3 = player.get_player_from_db_by_name(p3.name, p3.game_id, self.db)
        # In a 3 person game, everyone should be neighbors with eachother
        assert(p1.p_left_name in [p2.name, p3.name])
        assert(p1.p_right_name in [p2.name, p3.name])
        assert(not p1.p_left_name == p1.p_right_name)
        assert(p2.p_left_name in [p1.name, p3.name])
        assert(p2.p_right_name in [p1.name, p3.name])
        assert(not p2.p_left_name == p2.p_right_name)
        assert(p3.p_left_name in [p1.name, p2.name])
        assert(p3.p_right_name in [p1.name, p2.name])
        assert(not p3.p_left_name == p3.p_right_name)
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    
