#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from re import sub
from json import load
from os import path, listdir, mkdir
from collections import defaultdict

import click
import shutil


name_counters = defaultdict(lambda: 0)


def get_name(image: dict) -> str:
    if image['name'] == ' ':
        return image['original'].split('/')[-1]
    image_name = '-'.join(sub(r'[\u0400-\u04FF.]', '', image['name'].lower()).split(' '))
    image_id = image['id']
    return f'{image_name}_{image_id}_o.jpg'


def get_flickr_id(filename: str) -> str:
    for name_part in reversed(filename.replace('.', '_').split('_')):
        if name_part.isdigit():
            return name_part
    click.echo(f'Cannot extract flickr id from "{filename}"; may be invalid')
    return ''


def make_album(full_album: str) -> bool:
    if path.isfile(full_album):
        click.echo(f'Destination album already exists as file - "{full_album}"')
        return False

    if not path.isdir(full_album):
        mkdir(full_album)
    return True


def get_valid_albums(flickr_data: dict, images_dir: str) -> list:
    albums = [path.join(images_dir, album['title']) for album in flickr_data['albums']]
    valid_albums = []
    for album in albums:
        if make_album(album):
            valid_albums.append(album)
    return valid_albums


def get_real_name(flickr_data: dict, extension: str) -> str:
    name = flickr_data['name']
    if name == ' ':
        return ''
    return f'{name}.{extension}'


def append_counter(real_name: str, count: str) -> str:
    name_parts = real_name.split('.')
    extension = name_parts.pop()
    name_parts.append(str(count).zfill(4))
    name_parts.append(extension)
    return '.'.join(name_parts)


@click.command()
@click.argument('images_dir', envvar='FLICKR_IMAGES_DIR',type=click.Path(file_okay=False))
@click.argument('data_dir', envvar='FLICKR_DATA_DIR', type=click.Path(file_okay=False))
@click.argument('default_album', default='common')
def images_to_albums(images_dir, data_dir, default_album):
    full_default = path.join(images_dir, default_album)
    files_to_parse = listdir(images_dir)
    for filename in files_to_parse:
        full_name = path.join(images_dir, filename)
        if not path.isfile(full_name):
            click.echo(f'Skipping a dir: {full_name};')
            continue

        flickr_id = get_flickr_id(filename)
        if not flickr_id:
            continue
        extension = filename.split('.')[-1]
        if extension == filename:
            click.echo(f'No extension found in {filename} name; using as is')
            extension = ''

        data_path = path.join(data_dir, f'photo_{flickr_id}.json')
        if not path.isfile(data_path):
            click.echo(f'{data_path} is not right, extracted from {filename};')
            continue

        with open(data_path) as out:
            data = load(out)

        real_name = get_real_name(data, extension) or filename
        name_counters[real_name] += 1
        if name_counters[real_name] > 1:
            real_name = append_counter(real_name, name_counters[real_name])

        valid_albums = get_valid_albums(data, images_dir)
        if not valid_albums:
            click.echo(f'No valid albums for {filename}, moving to "{default_album}"')
            if not make_album(full_default):
                continue
            valid_albums.append(full_default)

        last_album = valid_albums.pop()

        for album in valid_albums:
            destination = path.join(album, real_name)
            if path.exists(destination):
                click.echo(f'"{destination}" already exists')
                continue
            shutil.copyfile(full_name, destination)
        destination = path.join(last_album, real_name)
        if path.exists(destination):
            click.echo(f'"{destination}" already exists')
            continue
        shutil.move(full_name, destination)


if __name__ == '__main__':
    images_to_albums()
