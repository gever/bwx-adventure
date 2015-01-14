# a simple http server for an adventure game
# vim: et sw=2 ts=2 sts=2

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from advent import Game
import time
import urlparse

# add games here.  As long as they follow the example, they will appear in the drop down menu.
import http_game

# globals
games = {}
state = {}

class State(object):
  def __init__(self, game, game_function, session, params):
    self.in_apply = 0
    self.session = session
    self.name = game
    self.game = game_function(game)
    self.game.http_output = True
    self.game.run_init()

class RequestHandler(BaseHTTPRequestHandler):
  def __init__(self, *args):
    BaseHTTPRequestHandler.__init__(self, *args)
    global games
    global state

  def do_GET(self):
    parsed_path = urlparse.urlparse(self.path)
    if parsed_path.path == '/favicon.ico':
      self.send_response(404)
      return
    params = urlparse.parse_qs(parsed_path.query, True)
    if not 'game' in params or not 'session' in params:
      self.intro()
      return
    game = params['game'][0]
    if not game in games:
      self.intro()
      return
    session = params['session'][0]
    if not session in state:
      state[session] = State(game, games[game], session, params)
    cmd = ""
    if 'cmd' in params:
      cmd = params['cmd'][0]
    self.play(cmd, state[session])

  def header(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write("<html><head><title>Adventure</title>")
    self.wfile.write("""
    <style>
    input.prompt { background-color: #000000; color: #ffffff; border: 0px;
                   font-size: 16pt;
                   text-decoration: none;
                   font-family: courier, monospace; }
    p.adventure { background-color: #000000; color: #cccccc; border: 0px;
                  font-size: 16pt;
                  text-decoration: none;
                  font-family: courier, monospace; }
    </style>
    """);
    self.wfile.write("</head><body OnLoad=document.f.p.focus()>");
    self.wfile.write('<p class="adventure">')

  def intro(self):
    self.header()
    self.wfile.write('<h1>Adventure Game Server</h1><br>')
    self.wfile.write('Welcome to the game server.  Please select a game from the drop down menu.  If you have a saved game or want to save this game enter a one word session name (e.g. joe1234) which will act as your username/password/save slot. Have Fun!<br>')
    self.wfile.write('<br><form name="prompt" action="play.html" method="GET">')
    self.wfile.write('<input type="hidden" name="cmd" value="">')
    session = 'session' + str(time.time())
    self.wfile.write('Session: <input type="text" name="session" value="%s"><br>' % session)
    self.wfile.write('Game: <select type="text" name="game">')
    for (k, v) in games.iteritems():
      self.wfile.write('<option>%s</option>' % k)
    self.wfile.write('</select><br>')
    self.wfile.write('<input type="submit" name="Submit">')
    self.wfile.write('</form>')
    self.footer()

  def footer(self):
    self.wfile.write("</body>")
    self.wfile.write("""
    <script languages="javascript">
    <!--
    document.f.p.focus()
    -->
    </script>""")
    self.wfile.write("</html>")

  def play(self, cmd, state):
    state.game.run_step(cmd)
    state.game.run_room()
    self.header()
    self.wfile.write('<p class="adventure">')
    t = '<br />'.join(state.game.http_text.split('\n'))
    self.wfile.write(t)
    self.wfile.write('</p>')
    self.wfile.write('<form name="f" action="play.html" method="GET">')
    self.wfile.write('<input type="hidden" name="game" value="%s">' % state.name)
    self.wfile.write('<input type="hidden" name="session" value="%s">' % state.session)
    self.wfile.write('<input id="p" class="prompt" type=text name="cmd" size="72">')
    self.wfile.write("</form>")
    self.footer()


class Server:
  def __init__(self, port):
    def handler(*args):
      RequestHandler(*args)
    global games
    games = Game.get_registered_games()
    HTTPServer.protocol_version = "HTTP/1.0"
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()

  @staticmethod
  def serve_http(port):
    Server(port)

if __name__ == "__main__":
  Server.serve_http(8080)
