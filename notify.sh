#!/bin/bash

mkfifo /tmp/waldo
sleep 10
systemd-notify --ready --status="Waiting for data…"

while : ; do
	read a < /tmp/waldo
	systemd-notify --status="Processing $a"

	# Do something with $a …
	sleep 10

	systemd-notify --status="Waiting for data…"
done
