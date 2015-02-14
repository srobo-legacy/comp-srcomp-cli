import webbrowser
import threading
import time
import socket

def find_unused_port():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.bind(('::1', 0))
    print(sock.getsockname())
    addr, port, flowinfo, scopeid = sock.getsockname()
    sock.close()
    return port

def command(settings):
    try:
        import sr.comp.scorer
    except ImportError:
        print("sr.comp.scorer not installed.")
        exit(1)
    port = find_unused_port()
    app = sr.comp.scorer.app
    app.config['COMPSTATE'] = settings.compstate
    app.config['COMPSTATE_LOCAL'] = not settings.push_changes
    def browse():
        time.sleep(1.5)
        webbrowser.open("http://localhost:{}/".format(port))
    thread = threading.Thread(target=browse)
    thread.start()
    try:
        app.run(host='::1',
                port=port,
                debug=False,
                passthrough_errors=True)
    except KeyboardInterrupt:
        pass

def add_subparser(subparsers):
    parser = subparsers.add_parser('score')
    parser.add_argument('compstate', help='competition state repository')
    parser.add_argument('-p', '--push-changes', action='store_true',
                        help='send commits upstream to origin/master')
    parser.set_defaults(func=command)

