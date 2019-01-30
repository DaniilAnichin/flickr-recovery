#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import subprocess
from json import load
from os import path, listdir, sched_getaffinity, wait

import click
import shutil

from .utils import (
    ensure_not_exists, get_flickr_id, get_real_name, get_valid_albums, make_dir
)


def images_to_albums(images_dir: str, data_dir: str, default_album: str):
    full_default = path.join(images_dir, default_album)
    with open(path.join(data_dir, 'albums.json')) as out:
        albums = load(out)['albums']
    files_to_parse = listdir(images_dir)
    for filename in files_to_parse:
        full_name = path.join(images_dir, filename)
        if not path.isfile(full_name):
            click.echo('Skipping a dir: {full_name};'.format(**locals()))
            continue

        flickr_id = get_flickr_id(filename)
        if not flickr_id:
            continue
        extension = filename.split('.')[-1]
        if extension == filename:
            click.echo('No extension found in {filename} name; using as is'.format(**locals()))
            extension = ''

        data_path = path.join(data_dir, 'photo_{flickr_id}.json'.format(**locals()))
        if not path.isfile(data_path):
            click.echo('{data_path} is not right, extracted from {filename};'.format(**locals()))
            continue

        with open(data_path) as out:
            data = load(out)

        real_name = get_real_name(data, extension) or filename

        valid_albums = get_valid_albums(albums, data, images_dir)
        if not valid_albums:
            click.echo('No valid albums for {filename}, moving to "{default_album}"'.format(**locals()))
            if not make_dir(full_default):
                continue
            valid_albums.append(full_default)

        last_album = valid_albums.pop()

        for album in valid_albums:
            destination = ensure_not_exists(path.join(album, real_name))
            shutil.copyfile(full_name, destination)

        destination = ensure_not_exists(path.join(last_album, real_name))
        shutil.move(full_name, destination)


def extract_archives(archives_dir, images_dir, data_dir):
    archives = [
        file
        for file
        in listdir(archives_dir)
        if file.endswith('.zip')
    ]
    destinations = {file: images_dir if file.startswith('data-') else data_dir for file in archives}

    processes = set()
    max_processes = len(sched_getaffinity(0))
    for file, destination in destinations.items():
        # NOTICE Both next commands may work only under unix distributions
        processes.add(subprocess.Popen(('unzip', path.join(archives_dir, file), '-d', destination,)))
        if len(processes) >= max_processes:
            wait()
            processes.difference_update([p for p in processes if p.poll() is not None])

    # Check if all the child processes were closed
    for p in processes:
        if p.poll() is None:
            p.wait()
