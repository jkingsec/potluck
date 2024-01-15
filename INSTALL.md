# Potluck Installation

## Note

Potluck is still early in development, many features have yet to be fully implemented. The current release is only intended for testing and not deployment.

## Server Setup

1. Download the repo using `git clone https://github.com/jkingsec/potluck.git`
2. Move server to `/opt` with `sudo mv ~/potluck/src/server /opt/potluck`
3. Create Potluck group with `sudo groupadd potluck`
4. Optionally, create a potluck user with `sudo useradd -g potluck potluck` or add the current user with `sudo usermod -aG potluck $USER`
5. Assign ownership of the server with `sudo chown -R :potluck /opt/potluck` (or `sudo chown -R potluck:potluck /opt/potluck`)
6. Change the secret key in `app.py`
7. Set up a virtual environment with
  - `sudo apt-get install python3.10-venv`
  - `cd /opt/potluck`
  - `python3 -m venv potluck-env`
  - `source /opt/potluck/potluck-env/bin/activate`
8. Install Python dependencies with `pip3 install -r /opt/potluck/requirements.txt`
  - If you need to install pip3, use `sudo apt-get install python3-pip` 
9. Install system-wide requirements (tested on Ubuntu 23.04 and 22.04)
  - `sudo apt-get install gcc g++-multilib libboost-all-dev nlohmann-json3-dev upx-ucl && sudo apt-get update`
10. If the server instance is going to be exposed on a public network (highly not recommended), then it should be configured with a WSGI and proxy server. For more detailed instructions, please consult the [Gunicorn documentation](https://docs.gunicorn.org/en/stable/deploy.html). Otherwise, a simple test can be done by simply launching the runfile `run`
  - `cd /opt/potluck && ./run`
  - If you wish to test the server on a private network, append `--host=0.0.0.0` to the end of `run`. BE INCREDIBLY CAREFUL WHEN DOING THIS.
11. Login into the server as "admin" with the password "potluck123"
12. Go to the User Settings page and change the password with the Change Password form

## Listener Setup

1. Download the repo using `git clone https://github.com/jkingsec/potluck.git`
2. Move server to `/opt` with `sudo mv ~/potluck/src/listener /opt/potluck`
3. Create Potluck group with `sudo groupadd potluck`
4. Optionally, create a potluck user with `sudo useradd -g potluck potluck` or add the current user with `sudo usermod -aG potluck $USER`
5. Assign ownership of the server with `sudo chown -R :potluck /opt/potluck` (or `sudo chown -R potluck:potluck /opt/potluck`)
6. Set up a virtual environment with
  - `sudo apt-get install python3.10-venv`
  - `cd /opt/potluck`
  - `python3 -m venv potluck-env`
  - `source /opt/potluck/potluck-env/bin/activate`
7. Install Python dependencies with `pip3 install -r /opt/potluck/requirements.txt`
  - If you need to install pip3, use `sudo apt-get install python3-pip` 
8. Edit `listener.py` so that `server_domain` and `server_port` both point to your server instance
9. As with the server, if the listener instance is going to be exposed on a public network, then it should be configured with a WSGI and proxy server. Otherwise, a simple test can be done with `python3 listener.py`
  - If you want to expose the listener to a private network for testing purposes, add the parameter `host="0.0.0.0"` to the `app.run()` command at the very bottom of `listener.py`
10. On launch, the listener will assign itself a UUID and contact the server
11. Repeat with each desired listener instance
