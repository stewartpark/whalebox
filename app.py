#!/usr/bin/env python

from flask import Flask, request
import docker
import tarfile
import json
import time
import sys
import io
import os

app = Flask(__name__)
client = docker.from_env()

with open(os.getenv('RUNTIMES_JSON', 'runtimes.json')) as f:
    RUNTIME_CONFIG = json.load(f)

if os.fork() == 0:
    for _, config in RUNTIME_CONFIG.items():
        print(f' * Pulling {config["image"]}...')
        client.images.pull(config['image'])
    print(' * Needed docker images are ready.')
    sys.exit(0)


def get_tar_bytes(filename, text):
    buf = io.BytesIO()
    text_bytes = text.encode('utf-8')
    tar = tarfile.TarFile(mode='w', fileobj=buf)
    f = tarfile.TarInfo(filename)
    f.uid = 1000
    f.gid = 1000
    f.size = len(text_bytes)
    tar.addfile(f, io.BytesIO(text_bytes))
    tar.close()
    return buf.getvalue()


@app.route('/')
def list_containers():
    labels = [
        'whalebox.created=true'
    ]

    if request.args.get('user'):
        labels.append(f'whalebox.user={request.args.get("user")}')

    containers = client.containers.list(all=True, filters={'label': labels})
    return {
        'containers': [
            {
                'id': c.short_id,
                'status': c.status,
                'labels': c.labels
            } for c in containers
        ]
    }


@app.route('/', methods=['POST'])
def create_container():
    runtime = request.json['runtime']
    code = request.json['code']
    extra = request.json.get('extra', {})
    labels = {
        'whalebox.created': 'true',
        'whalebox.runtime': runtime
    }

    if request.args.get('user'):
        labels['whalebox.user'] = request.args.get('user')

    config = RUNTIME_CONFIG[runtime]

    try:
        client.images.get(config['image'])
    except docker.errors.ImageNotFound:
        client.images.pull(config['image'])

    container = client.containers.create(
        image=config['image'],
        entrypoint=config['entrypoint'],
        command=config['command'],
        cpu_shares=1000,
        network_disabled=True,
        oom_kill_disable=False,
        pids_limit=10,
        shm_size='1M',
        mem_limit='16M',
        stdin_open=True,
        tty=True,
        user=1000,
        environment={
            'TERM': 'dumb'
        },
        labels=labels
    )

    container.put_archive('/', get_tar_bytes(config['file'], code))

    for k, v in extra.items():
        container.put_archive('/', get_tar_bytes(k, v))

    while container.status == 'created':
        container.start()
        time.sleep(0.5)
        container.reload()

    return {
        'id': container.short_id,
        'status': container.status,
        'labels': container.labels
    }


@app.route('/<container_id>', methods=['DELETE'])
def delete_container(container_id):
    container = client.containers.get(containerid)
    container.remove(force=True)
    return ''


@app.route('/<container_id>', methods=['POST'])
def write_to_container(container_id):
    s = client.api.attach_socket(
        container_id, params={'stdin': 1, 'stream': 1})
    data = request.get_data()
    s._sock.send(data)
    if request.args.get('nl'):
        s._sock.send(b"\n")
    s.close()
    return ''


@app.route('/<container_id>', methods=['GET'])
def read_from_container(container_id):
    kwargs = {
        'stdout': True,
        'stderr': False,
        'tail': 128
    }

    if request.args.get('stderr'):
        kwargs['stderr'] = True
    if request.args.get('tail'):
        kwargs['tail'] = int(request.args.get('tail'))

    container = client.containers.get(container_id)
    return container.logs(**kwargs)
