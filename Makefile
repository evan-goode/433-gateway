default: all

all:
	./setup.py build

install:
	./setup.py install
	install -m 644 433-gateway.service /etc/systemd/system/
	[ -f /etc/433-gateway.toml ] || install -m 644 433-gateway.toml /etc/433-gateway.toml
	systemctl daemon-reload
