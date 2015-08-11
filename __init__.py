from fiasco import parse_playset
from flask import Flask, render_template, request, session, redirect, url_for
from flask import g, jsonify
from flask_bootstrap import Bootstrap, StaticCDN
from cgi import escape
import sqlite3
import json
from random import randint

DATABASE = '/Users/danielsprechman/development/projects/fiasco/database/players.db'
GAMEID = "0"

def get_players():
    cur = get_db().cursor()
    db_result = cur.execute("SELECT name from players")
    results = db_result.fetchall()
    players = []
    for name in results:
        if len(name) > 0:
            players.append(name[0])
    return players

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def get_num_players():
    return len(get_players())

def get_dice(num_players):
    dice = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    for i in range(0,num_players*4):
        r = randint(1,6)
        dice[r] = dice[r] + 1
    return dice

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

def get_dice_from_db(game_id):
    dice = {}
    db = get_db()
    cur = db.cursor()
    db_result = cur.execute("SELECT * from dice where game_id=?", GAMEID)
    if len(db_result.fetchall()) > 0:
        db_result = cur.execute ("SELECT d1,d2,d3,d4,d5,d6 from dice where game_id=?", GAMEID)
        results = db_result.fetchall()
        if len(results) > 0:
            print "RESULTS: " + str(results[0])
            for i in range (0, len(results[0])):
                dice[i+1] = results[0][i]
        else:
            print "ERROR NO RESULTS"
    else:
        print "SETTING DICE"
        dice = get_dice(get_num_players())
        cur.execute("INSERT INTO dice (d1,d2,d3,d4,d5,d6,game_id) VALUES (?,?,?,?,?,?,?)", \
                    (dice[1],  dice[2], dice[3], dice[4], dice[5], dice[6], GAMEID,))
        db.commit()
    return dice

def get_playset_html():
    playset_html = '<h2>Relationships</h2>\n'
                       
    pd = parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
    last_group = ''
    group_num = 0
    for entry in pd['relationships']:
        entry_id = str(group_num) + "_" + str(entry.num)
        if last_group == '':
            last_group = entry.group
            group_num += 1
            playset_html += "<h3>" + str(group_num) + ". " + entry.group + "</h3>\n" + \
                            '<ul class="list-group">'
        if not last_group == entry.group:
            last_group = entry.group
            group_num += 1
            playset_html += "</ul>" + \
                            "<h3>"  + str(group_num) + ". " + entry.group + "</h3>\n" + \
                            '<ul class="list-group">'
        select_html1 = ''
        select_html2 = ''

        if len(entry.name_options) > 0:
            select_html1 = '&nbsp;&nbsp;(<select class="btn btn-mini">'
            for opt in entry.name_options:
                select_html1 += '<option>' + opt + '</option>'
            select_html1 += '</select>)'
        if len(entry.pair_options) > 0:
            select_html2 = '&nbsp;&nbsp;(<select class="btn btn-mini">'
            for opt in entry.pair_options:
                select_html2 += '<option>' + opt + '</option>'
            select_html2 += '</select>)'
        playset_html += '<li class="p_rel_item list-group-item">' + \
                        '<input type="radio" id="radio_' + entry_id + '">' + \
                        '&nbsp;&nbsp;&nbsp;' + str(entry.num) + ". " + entry.name + select_html1 + '&nbsp;&nbsp; / &nbsp;&nbsp;' + entry.pair + select_html2 + '</li>'
    playset_html += '</ul>'
    return playset_html

#def get_playset_meta_html():
#
#    
#    return json.dumps({'data' : 'asdf'})

def create_app(configfile=None):
    app = Flask(__name__)
    Bootstrap(app)
    app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN()
    app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()
    app.secret_key = 'K\x9a\xa1\xa1\x84\x1a\x9b\xdc\xb3m\x0c\xdf[\x1c;\xc1S\xbd\xd6\x90\xec#\xdaX'

    #@app.route('/test', methods=('POST', 'GET'))
    #def test():
    #    data = {"data" : "asdf"}
    #    print "RETURNING: " + json.dumps(data)
    #    return render_template('test.html', td=json.dumps(data))
    #    #return jsonify({'data' : 'asdf'})

    @app.route('/get_setup_status', methods=('POST', 'GET'))
    def get_setup_status():
        dice_html = get_dice_html(get_dice_from_db(GAMEID))
        data = {'dice_html' : dice_html}
        #data = {'test1' : 'a', 'test2' : 'b'}
        #print "RETURNING: " + str(jsonify(data))
        return jsonify(data)

    @app.route('/play', methods=('POST', 'GET'))
    def play():
        player = request.args.get('player', '')
        if player:
            players = get_players()
            if player in players:
                session['player'] = player
                
        if not 'player' in session or len(session['player']) == 0:
            players = get_players()
            return render_template('select_player.html', players=players)
        else:
            #pd = parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
            #dice = get_dice_from_db(GAMEID)
            return render_template('play.html',
                                   player=session['player'],
                                   playset_name='Main St.',
                                   dice_html=get_dice_html(get_dice_from_db(GAMEID)),
                                   playset_html = get_playset_html())

    @app.route('/endgame', methods=('POST', 'GET'))
    def endgame():
        db = get_db()
        cur = db.cursor()
        cur.execute("delete from dice where game_id=?",GAMEID)
        db.commit()
        return redirect('/')

    @app.route('/changeplayer', methods=('POST', 'GET'))
    def changeplayer():
        session['player'] = ''
        return redirect('/play')
        
    @app.route('/clearplayers', methods=('POST', 'GET'))
    def clearplayers():
        cur = get_db().cursor()
        cur.execute("delete from players")
        db.commit()
        return ''
    
    @app.route('/removeplayer', methods=('POST', 'GET'))
    def removeplayer():
        db = get_db()
        cur = db.cursor()
        name = request.form['data']
        print "REMOVING " + name
        #uname = HTMLParser.HTMLParser().unescape(name)
        cur.execute("delete from players where name=?", (name,))
        db.commit()
        return ''

    @app.route('/playerlist', methods=('POST', 'GET'))
    def playerlist():
        players = get_players()
        result_str = '<ul class="list-group">'
        found_current_player = False
        for name in players:
            if 'player' in session and name == session['player']:
                found_current_player = True
            result_str += '<li class="list-group-item">' + name \
                          + '<div class="pull-right"><a href="' + name + '" class="remove_player">Remove</a></div></li>'
        result_str += '</ul>'
        if not found_current_player:
            session['player'] = ''
        return result_str

    @app.route('/playerjoin', methods=('POST', 'GET'))
    def playerjoin():
        name = request.form['data']
        if not name in get_players():
            print "INSERTING PLAYER: " + name
            db = get_db()
            cur = db.cursor()
            #sql = "INSERT INTO players (name, game_id) VALUES ('%s', '%s')"
            cur.execute("INSERT INTO players (name, game_id) VALUES (?, ?)", (name, GAMEID,))
            db.commit()
        session['player'] = name
        return ''

    @app.route('/', methods=('GET', 'POST'))
    def index():
        #player = request.args.get('player', '')
        player = ''
        if 'player' in session:
            player = session['player']
        else:
            session['player'] = player
        return render_template('index.html', player=player)

    #@app.route('/test', methods=('GET', 'POST'))
    #def test():
    #    return render_template('test2.html')
    
    return app
