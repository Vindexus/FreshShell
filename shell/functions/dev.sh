# General development helper functions.

# Kill whatever process is listening on the given port.
#   Usage: killport <port>
killport() {
  lsof -ti :$1 | xargs kill -9
}
