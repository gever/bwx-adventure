# a simple http server for an adventure game
# vim: et sw=2 ts=2 sts=2

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time
import urlparse

class State(object):
  def __init__(self):
    self.in_apply = 0
    self.username = 'user' + str(time.clock())
    self.password = 'password' + str(time.clock())
    self.session = 'session' + str(time.clock())

class RequestHandler(BaseHTTPRequestHandler):
  def __init__(self, state, *args):
    self.state = state
    BaseHTTPRequestHandler.__init__(self, *args)

  def do_GET(self):
    parsed_path = urlparse.urlparse(self.path)
    if parsed_path.path == '/favicon.ico':
      self.send_response(404)
      return
    params = urlparse.parse_qs(parsed_path.query, True)
    print params
    cmd = ""
    if 'cmd' in params:
      cmd = params['cmd']
    self.play(cmd)

  def play(self, cmd):
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
    self.wfile.write("</head><body>");
    self.wfile.write("""
    <p class="adventure">
    <form name="prompt" action=play.html" method="GET">
    """);
    if self.state.in_apply:
      self.wfile.write('<input type="hidden" name="apply" value="1">')
      self.wfile.write('<input type="hidden" name="username" value="%s">' % self.state.username)
      self.wfile.write('<input type="hidden" name="password" value="%s">' % self.state.password)
      self.wfile.write('<input type="hidden" name="session" value="%s">' % self.state.session)
    self.wfile.write('> <input class="prompt" type=text name="cmd" size="72">')
    self.wfile.write("</form>")
    self.wfile.write("</body>")
    self.wfile.write("""
    <script languages="javascript">
    <!--
    document.prompt.inputPrompt.focus()
    -->
    </script>""")
    self.wfile.write("</html>")


class Server:
  def __init__(self, state, port):
    def handler(*args):
      RequestHandler(state, *args)
    HTTPServer.protocol_version = "HTTP/1.0"
    server = HTTPServer(('0.0.0.0', port), handler)
    server.serve_forever()

def output(s, t):
  pass

def serve_http(port):
  Server(State(), port)

serve_http(9999)
