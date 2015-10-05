""" This module contains functions that are used for generating html
"""

import player

def get_dice_color(num):
    greensp = "<span style='color:#00cc00'>"
    redsp = "<span style='color:#dd0000'>"
    esp = "</span>"
    if num < 3:
        return redsp + str(num) + esp
    return greensp + str(num) + esp

def get_dice_html(dice):
    rstring = "<pre><strong>Dice available:</strong>" + \
              "1:<strong>" + get_dice_color(dice[1]) + "</strong>  " +\
              "2:<strong>" + get_dice_color(dice[2]) + "</strong>  " +\
              "3:<strong>" + get_dice_color(dice[3]) + "</strong>  " +\
              "4:<strong>" + get_dice_color(dice[4]) + "</strong>  " +\
              "5:<strong>" + get_dice_color(dice[5]) + "</strong>  " +\
              "6:<strong>" + get_dice_color(dice[6]) + "</strong></pre>"
    return rstring


def get_playset_html(pset, db, cur_player_name, game_id):
    playset_html = '<h2>Relationships</h2>\n'
    cur_player = player.get_player_from_db_by_name(cur_player_name, game_id, db)
    for i,entry_group in enumerate(pset.relationships):
        entry_id = "rel_" + str(i+1)
        # 1. family      enable for: player1 player2
        playset_html += "\n<div class=\"row\"><div class=\"col-md-4\"><h3>" + str(i+1) + ". " + entry_group.title + "</h3></div>\n" + \
                        "<div class=\"col-md-4 well-lg\">" + \
                        "<form class=\"form-inline\">Enable for:&nbsp;&nbsp;&nbsp;" + \
                        "<label class=\"checkbox\"><input type=\"checkbox\" entry_id=\"" + entry_id + "\"value = \"" + cur_player.p_left_name + "\" class=\"player_check player_check1\"> " + cur_player.p_left_name + "</input></label>&nbsp;&nbsp;&nbsp;" + \
                        "<label class=\"checkbox\"><input type=\"checkbox\" entry_id=\"" + entry_id + "\" value = \"" + cur_player.p_right_name + "\" class=\"player_check player_check2\"> " + cur_player.p_right_name + "</input></label>" + \
                        "</form></div></div>\n" + \
                        '\n<ul class="list-group" id="' + entry_id + '">'
        
        for j,entry in enumerate(entry_group.entries):
            entry_id_e = entry_id + "e" + str(j)
            select_html1 = ''
            select_html2 = ''
            for k, option in enumerate(entry.rel_a_options):
                if k == 0:
                    select_html1 = '&nbsp;&nbsp;(\n<select class="btn btn-mini rel_select1">'
                select_html1 += '<option val="'+ entry_id_e + '_g1_o' + str(k) +'">' + option + '</option>'
                if k == len(entry.rel_a_options)-1:
                    select_html1 += '</select>)'
            for k, option in enumerate(entry.rel_b_options):
                if k == 0:
                    select_html2 = '&nbsp;&nbsp;(\n<select class="btn btn-mini rel_select2">'
                select_html2 += '<option val="'+ entry_id_e + '_g2_o' + str(j) +'">' + option + '</option>'
                if k == len(entry.rel_a_options)-1:
                    select_html2 += '</select>)'
            playset_html += '<li class="p_rel_item list-group-item disabled">' + \
                        '<input type="radio" disabled="true" id="radio_' + entry_id_e + '" class="radio_rel">' + \
                        '&nbsp;&nbsp;&nbsp;' + str(j+1) + '. ' + \
                        '<span class="g1_text">' + entry.rel_a + '</span>' + select_html1 + \
                        '&nbsp;&nbsp; / &nbsp;&nbsp;<span class="g2_text">' + \
                        entry.rel_b + '</span>' + select_html2 + '</li>'
        playset_html += '</ul>\n'
    return playset_html

def get_player_list_html(player_names):
    result_str = '<ul class="list-group">'
    for name in player_names:
        result_str += '<li class="list-group-item">' + name \
                      + '<div class="pull-right"><a href="' + name + '" class="remove_player">Remove</a></div></li>'
    result_str += '</ul>'
    return result_str
