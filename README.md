# whalebox

whalebox lets you run untrusted code easily via simple HTTP APIs.

Note: this is pre-alpha quality software. Use at your own peril.


## How to run locally

```bash
$ docker-compose up
```


## Usage

```bash
# Run code
$ curl -XPOST -H'Content-Type: application/json' http://localhost:5000/ -d'{"runtime": "ruby", "code": "print(\"Hello, world\")"}'
{"id":"5b99000314","labels":{"whalebox.created":"true","whalebox.runtime":"ruby"},"status":"exited"}

# Get stdout
$ curl http://localhost:5000/5b99000314
Hello, world

# If your application expects stdin, you can write to stdin as well
$ curl -XPOST 'http://localhost:5000/5b99000314?nl=1' -d'hello'

# List containers
$ curl http://localhost:5000/
{"containers":[{"id":"5b99000314","labels":{"whalebox.created":"true","whalebox.runtime":"ruby"},"status":"exited"},{"id":"5b79c7f4d8","labe
ls":{"whalebox.created":"true","whalebox.runtime":"ruby"},"status":"exited"}]}

# Run code with a user name tagged.
$ curl -XPOST -H'Content-Type: application/json' 'http://localhost:5000/?user=john123' -d'{"runtime": "ruby", "code": "print(\"Hello, world\")"}'
{"id":"dce65099f6","labels":{"whalebox.created":"true","whalebox.runtime":"ruby","whalebox.user":"john123"},"status":"exited"}

# List containers for a user
$ curl 'http://localhost:5000/?user=john123'
{"containers":[{"id":"dce65099f6","labels":{"whalebox.created":"true","whalebox.runtime":"ruby","whalebox.user":"john123"},"status":"exited"
}]}
```
