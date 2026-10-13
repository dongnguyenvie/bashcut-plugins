"""`bashcut` for the fetch scripts while the plugin runs them (bin/bridge/bashcut).

The scripts shell out to `bashcut <group> <command> …` exactly as they do in an agent's terminal. Inside the plugin
there is no automation socket, so this stand-in hands the words to the plugin's session over a Unix socket; the
session runs them as the host call `cli` (the same command, checked by BashCut like any plugin call) and the answer
is printed the way the bashcut CLI prints it: the result as JSON on stdout, or {"error": {code, message}} on stderr
with exit status 1. Standard library only.
"""
import json
import os
import socket
import sys


def main(argv):
    path = os.environ.get("BASHCUT_RESOURCES_BRIDGE")
    if not path:
        sys.stderr.write(json.dumps({"error": {"code": -32603, "message": "bashcut is reachable only while "
                                               "bashcut.resources runs a request"}}) + "\n")
        return 1
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.connect(path)
            connection.sendall((json.dumps({"argv": argv}, ensure_ascii=False) + "\n").encode())
            connection.shutdown(socket.SHUT_WR)
            data = b""
            while True:
                chunk = connection.recv(1 << 16)
                if not chunk:
                    break
                data += chunk
        reply = json.loads(data or b"{}")
    except (OSError, ValueError) as error:
        reply = {"error": {"code": -32603, "message": f"bashcut.resources bridge: {error}"}}
    if "error" in reply:
        sys.stderr.write(json.dumps({"error": reply["error"]}, ensure_ascii=False) + "\n")
        return 1
    sys.stdout.write(json.dumps(reply.get("result"), ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
