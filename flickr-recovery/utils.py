#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from os import path, mkdir

import click


def get_flickr_id(filename: str) -> str:
    for name_part in reversed(filename.replace('.', '_').split('_')):
        if name_part.isdigit():
            return name_part
    click.echo('Cannot extract flickr id from "{filename}"; may be invalid'.format(**locals()))
    return ''


def make_dir(full_path: str) -> bool:
    if path.isfile(full_path):
        click.echo('Destination directory already exists as file - "{full_path}"'.format(**locals()))
        return False

    if not path.isdir(full_path):
        mkdir(full_path)
    return True


def get_valid_albums(full_albums: dict, flickr_data: dict, images_dir: str) -> list:
    albums_data = [data for data in full_albums if flickr_data['id'] in data['photos']]
    albums_data.extend(flickr_data['albums'])
    albums = {path.join(images_dir, album['title'].replace('/', '.')) for album in albums_data}
    valid_albums = []
    for album in albums:
        if make_dir(album):
            valid_albums.append(album)
    return valid_albums


def get_real_name(flickr_data: dict, extension: str) -> str:
    name = flickr_data['name']
    if name == ' ':
        return ''
    return '{name}.{extension}'.format(**locals())


def ensure_not_exists(destination: str) -> str:
    if not path.exists(destination):
        return destination
    count = 1
    name_parts = destination.split('.')
    while True:
        if count > 10000:
            raise Exception('Something went really wrong')
        current = name_parts[:]
        current[-2] += '-' + str(count).zfill(4)
        destination = '.'.join(current)
        if not path.exists(destination):
            return destination
        count += 1
