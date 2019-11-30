#!/usr/bin/env python

from datetime import datetime

import docker
import time
import os

client = docker.from_env()

TIMEOUT = int(os.getenv('TIMEOUT', 3600))

while True:
    containers = client.containers.list(
        all=True,
        filters=dict(
            label='whalebox.created=true'
        )
    )

    now = datetime.utcnow()
    for container in containers:
        created = datetime.strptime(
            container.attrs['Created'][:-4], '%Y-%m-%dT%H:%M:%S.%f')
        seconds = (now - created).seconds
        if seconds > TIMEOUT:
            print(
                f"Deleted {container.short_id} since it's too old. ({seconds}s, {container.status})")
            container.remove(force=True)

    time.sleep(5)
