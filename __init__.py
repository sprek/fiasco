from fiasco import parse_playset
from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap, StaticCDN
from flask import g
from cgi import escape
import sqlite3
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
    rstring = "1:<strong>" + get_dice_color(dice[1]) + "</strong>  " +\
              "2:<strong>" + get_dice_color(dice[2]) + "</strong>  " +\
              "3:<strong>" + get_dice_color(dice[3]) + "</strong>  " +\
              "4:<strong>" + get_dice_color(dice[4]) + "</strong>  " +\
              "5:<strong>" + get_dice_color(dice[5]) + "</strong>  " +\
              "6:<strong>" + get_dice_color(dice[6]) + "</strong>"
    return rstring

def create_app(configfile=None):
    app = Flask(__name__)
    Bootstrap(app)
    app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN()
    app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()
    app.secret_key = 'K\x9a\xa1\xa1\x84\x1a\x9b\xdc\xb3m\x0c\xdf[\x1c;\xc1S\xbd\xd6\x90\xec#\xdaX'

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
            pd = parse_playset('/Users/danielsprechman/development/projects/fiasco/playset_main_st.txt')
            dice = {}
            db = get_db()
            cur = db.cursor()
            db_result = cur.execute("SELECT * from dice where game_id=?", GAMEID)
            if len(db_result.fetchall()) > 0:
                print "ALREADY STARTED"
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
            return render_template('play.html',
                                   player=session['player'],
                                   playset=pd,
                                   playset_name='Main St.',
                                   dice_html=get_dice_html(dice))

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

    @app.route('/test', methods=('GET', 'POST'))
    def test():
        return render_template('test2.html')
    
    return app
