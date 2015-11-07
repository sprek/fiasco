import unittest
import tempfile
import os
import create_db
import sqlite3
import player
import playset
import dice
import game_control
import status

# id, name, p_left_name, p_right_name,
# rel_l_id, rel_l_role, rel_l_option
# rel_r_id, rel_r_role, rel_r_option

GAME_ID1='0'
TEST_PLAYER_VALUES1= [1, 'daniel', '', '',
                      '', '', '',
                      '', '', '', GAME_ID1]
TEST_PLAYER_VALUES2= [2, 'mary', '', '',
                      '', '', '',
                      '', '', '', GAME_ID1]

TEST_PLAYER_VALUES3= [2, 'fred', '', '',
                      '', '', '',
                      '', '', '', GAME_ID1]

TEST_PLAYSET='/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt'

def clear_tables(db):
    cur = db.cursor()
    cur.execute('DELETE FROM player')
    cur.execute('DELETE FROM dice')
    db.commit()

def print_player_info(player_obj):
    print ("id_num        : " + str(player_obj.id_num))
    print ("name          : " + str(player_obj.name))
    print ("p_left_name   : " + str(player_obj.p_left_name))
    print ("p_right_name  : " + str(player_obj.p_right_name))
    print ("rel_l_id      : " + str(player_obj.rel_l_id))
    print ("rel_l_role    : " + str(player_obj.rel_l_role))
    print ("rel_l_option  : " + str(player_obj.rel_l_option))
    print ("rel_r_id      : " + str(player_obj.rel_r_id))
    print ("rel_r_role    : " + str(player_obj.rel_r_role))
    print ("rel_r_option  : " + str(player_obj.rel_r_option))
    print ("game_id       : " + str(player_obj.game_id))

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

        # try setting relationships

        # first prepare the dice, so that there's enough for all the tests
        dice.insert_dice_into_db(dice.Dice({0:100,1:100,2:100,3:100,4:100,5:100,6:100},p1.game_id), self.db)
        
        test_playset = playset.parse_playset(TEST_PLAYSET)
        # p1 and p2: mayor / health commissioner
        # p1 and p3: drug dealer / drug manufacturer
        # p2 and p3: plumber / client
        p1_p2_rel_opt = ('elected official', 'mayor')
        p2_p1_rel_opt = ('elected official', 'health commissioner')
        p1_p3_rel_opt = ('drug person', 'dealer')
        p3_p1_rel_opt = ('drug person', 'manufacturer')
        p2_p3_rel_opt = ('tradesman', 'plumber')
        p3_p2_rel_opt = ('client', '')
        game_control.set_relationship(p1_p2_rel_opt[0], p1_p2_rel_opt[1], p1.name,
                                      p2_p1_rel_opt[0], p2_p1_rel_opt[1], p2.name,
                                      p1.name, test_playset, p1.game_id, self.db)
        game_control.set_relationship(p1_p3_rel_opt[0], p1_p3_rel_opt[1], p1.name,
                                      p3_p1_rel_opt[0], p3_p1_rel_opt[1], p3.name,
                                      p3.name, test_playset, p1.game_id, self.db)
        game_control.set_relationship(p2_p3_rel_opt[0], p2_p3_rel_opt[1], p2.name,
                                      p3_p2_rel_opt[0], p3_p2_rel_opt[1], p3.name,
                                      p3.name, test_playset, p1.game_id, self.db)
        # get the updated player information
        p1 = player.get_player_from_db_by_name(p1.name, p1.game_id, self.db)
        p2 = player.get_player_from_db_by_name(p2.name, p2.game_id, self.db)
        p3 = player.get_player_from_db_by_name(p3.name, p3.game_id, self.db)

        #print_player_info(p1)
        #print_player_info(p2)
        #print_player_info(p3)
        
        # In a 3 person game, everyone should be neighbors with eachother
        if p1.p_left_name == p2.name:
            # for player 1: left is p2, right is p3
            assert p1_p2_rel_opt == (p1.rel_l_role, p1.rel_l_option)
            assert p1_p3_rel_opt == (p1.rel_r_role, p1.rel_r_option)
            # for player 3: left is p1, right is p2
            assert p3_p1_rel_opt == (p3.rel_l_role, p3.rel_l_option)
            assert p3_p2_rel_opt == (p3.rel_r_role, p3.rel_r_option)
            # for palyer 2: left is p3, right is p1
            assert p2_p3_rel_opt == (p2.rel_l_role, p2.rel_l_option)
            assert p2_p1_rel_opt == (p2.rel_r_role, p2.rel_r_option)
        elif p1.p_left_name == p3.name:
            # for player 1: left is p3, right is p2
            assert p1_p3_rel_opt == (p1.rel_l_role, p1.rel_l_option)
            assert p1_p2_rel_opt == (p1.rel_r_role, p1.rel_r_option)
            # for player 3: left is p2, right is p1
            assert p3_p2_rel_opt == (p3.rel_l_role, p3.rel_l_option)
            assert p3_p1_rel_opt == (p3.rel_r_role, p3.rel_r_option)
            # for palyer 2: left is p1, right is p3
            assert p2_p1_rel_opt == (p2.rel_l_role, p2.rel_l_option)
            assert p2_p3_rel_opt == (p2.rel_r_role, p2.rel_r_option)
        else:
            # this should not happen
            assert False

    def test_status(self):
        """ Testing status functions
        status.get_round_from_db
        """
        clear_tables(self.db)
        assert(status.get_round_from_db(GAME_ID1, self.db) == -1)
        status.initialize_status(GAME_ID1, self.db, 3)
        assert(status.get_round_from_db(GAME_ID1, self.db) == 0)
        status.set_round_in_db(5, GAME_ID1, self.db)
        assert(status.get_round_from_db(GAME_ID1, self.db) == 5)
        status.initialize_status(GAME_ID1, self.db, 3)
        assert(status.get_round_from_db(GAME_ID1, self.db) == 0)
        table_str = status.create_player_rel_table(5)
        assert (len(table_str) == 74)
        table = status.get_table_from_rel_table(table_str)
        assert (len(table) == 5)
        assert (len(table[0]) == 5)
        tmp_table_str = status.get_rel_table_from_table(table)
        assert (tmp_table_str == table_str)
        tmp_table = status.get_table_from_rel_table(table_str)
        assert (tmp_table == table)
        new_table = status.update_player_rel_table(table_str, 1,2,5)
        status.set_player_rel_table_in_db(GAME_ID1, new_table, self.db)
        new_status = status.get_status_from_db(GAME_ID1, self.db)
        assert(status.get_table_from_rel_table(new_status.player_rel_table)[1][2] == '5')
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
