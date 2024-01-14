# To-do List

## Server

- Implement settings menus
  - Server settings
  - Client settings
  - Listener settings
  - User settings
- Add validators to all fields
- Better authentication for user creation
  - Email verification
  - Invite codes
  - Add time limits to sessions
- "Forgot Password" form
- "Remove Manager" form
- "Add Admin" form
- "Clear Tasks" form
- Add cleanup job for payloads folder
- Alternate dropper options
- Make templates flexbox-based to improve mobile support
- Add scrolling to logs in project screen
- Add warnings to permission/deletion related actions
- Add feature to save and edit user commands
- Improve crypter.py to more thoroughly obfuscate UPX traces

## Listener

- Load settings variables from database
- Create route that accepts configuration changes from server
- Stress test request buffer

## Client

- Add configuration function
- Improve persistence method
  - No local copy of binary
  - No use of Flock
  - Change cronjob each time on launch
- Gradually remove all hard-coded strings or change to different encoding
- Incorporate AV-detection methods that are less terminal-based
- Create a "Lite" version of Ziti that only accepts and executes commands
- Port Ziti to Windows, with minimal API usage
  - Create respective PS-based dropper script
- Create a MitM payload that logs passwords via .bash_rc
- Add rootkit to future clients

## Project

- Create Docker images for server and listener
  - MySQL by default
  - Gunicorn for WSGI
  - Nginx proxy server with self-signed cert
  - Listener launches with script that takes in server address/port as arguments
- SOCKS Support
- Split listener/server/clients into separate repositories?
