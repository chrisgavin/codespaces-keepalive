#!/usr/bin/env python3
import datetime
import json
import os
import pathlib
import sys
import time

_LOG_FILE = pathlib.Path.home() / ".local" / "log" / "keepalive.log"
_ACTIVE_CLIENTS_MONITOR_PATH = pathlib.Path("/workspaces/.codespaces/shared/active-clients-monitor.json")
_ACTIVE_CLIENTS_MONITOR_TEMP_PATH = _ACTIVE_CLIENTS_MONITOR_PATH.parent / (_ACTIVE_CLIENTS_MONITOR_PATH.name + ".tmp")

def _update():
	timestamp = datetime.datetime.utcnow().isoformat() + "Z"
	print(f"Updating keepalive timestamp to {timestamp}.", file=sys.stderr)
	content = json.loads(_ACTIVE_CLIENTS_MONITOR_PATH.read_text())
	content["timestamp"] = timestamp
	_ACTIVE_CLIENTS_MONITOR_TEMP_PATH.write_text(json.dumps(content))
	_ACTIVE_CLIENTS_MONITOR_TEMP_PATH.rename(_ACTIVE_CLIENTS_MONITOR_PATH)

def _loop():
	while True:
		_update()
		time.sleep(60)

def main():
	_LOG_FILE.parent.mkdir(exist_ok=True, parents=True)

	while not _ACTIVE_CLIENTS_MONITOR_PATH.exists():
		print("Waiting for active client monitor file to exist before forking...", file=sys.stderr)
		time.sleep(5)

	_update()

	print(f"Forking into the background now. Further log output will go to {_LOG_FILE}.", file=sys.stderr)

	pid = os.fork()
	if pid > 0:
		return

	os.setsid()
	os.umask(0)

	pid = os.fork()
	if pid > 0:
		return

	sys.stdout.flush()
	sys.stderr.flush()
	output_stream = _LOG_FILE.open("a")
	sys.stdout = output_stream
	sys.stderr = output_stream

	_loop()

if __name__ == "__main__":
	main()
