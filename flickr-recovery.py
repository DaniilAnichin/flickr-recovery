#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import subprocess
from re import sub
from json import load
from os import path, listdir, mkdir, sched_getaffinity, wait

import click
import shutil


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


def make_dir(full_path: str) -> bool:
    if path.isfile(full_path):
        click.echo(f'Destination directory already exists as file - "{full_path}"')
        return False

    if not path.isdir(full_path):
        mkdir(full_path)
    return True


def get_valid_albums(flickr_data: dict, images_dir: str) -> list:
    albums = [path.join(images_dir, album['title'].replace('/', '.')) for album in flickr_data['albums']]
    valid_albums = []
    for album in albums:
        if make_dir(album):
            valid_albums.append(album)
    return valid_albums


def get_real_name(flickr_data: dict, extension: str) -> str:
    name = flickr_data['name']
    if name == ' ':
        return ''
    return f'{name}.{extension}'


def ensure_not_exists(destination: str) -> str:
    if not path.exists(destination):
        return destination
    count = 1
    name_parts = destination.split('.')
    while True:
        if count > 10000:
            raise Exception('Something went really wrong')
        current = name_parts[:]
        current[-2] += f'-{str(count).zfill(4)}'
        destination = '.'.join(current)
        if not path.exists(destination):
            return destination
        count += 1


def images_to_albums(images_dir: str, data_dir: str, default_album: str):
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

        valid_albums = get_valid_albums(data, images_dir)
        if not valid_albums:
            click.echo(f'No valid albums for {filename}, moving to "{default_album}"')
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
        processes.add(subprocess.Popen(('unzip', path.join(archives_dir, file), '-d', destination,)))
        if len(processes) >= max_processes:
            wait()
            processes.difference_update([p for p in processes if p.poll() is not None])

    # Check if all the child processes were closed
    for p in processes:
        if p.poll() is None:
            p.wait()


@click.group()
def cli():
    """Script for working with flickr data dump, which is kinda messy and unordered"""
    pass


@cli.command()
@click.argument('archives_dir', envvar='FLICKR_ARCHIVES_DIR', type=click.Path(file_okay=False))
@click.argument('images_dir', envvar='FLICKR_IMAGES_DIR', default='-',
                type=click.Path(file_okay=False, allow_dash=True))
@click.argument('data_dir', envvar='FLICKR_DATA_DIR', default='-',
                type=click.Path(file_okay=False, allow_dash=True))
def extract(archives_dir, images_dir, data_dir):
    """
    Simply extracts all the data from archives to two different dirs,
    :param archives_dir: directory where archives are stored
    :param images_dir: path to directory with flickr images
    :param data_dir: path to directory with account data
    """
    if data_dir == '-':
        data_dir = path.join(archives_dir, 'data')
        if not make_dir(data_dir):
            return
    if images_dir == '-':
        images_dir = path.join(archives_dir, 'images')
        if not make_dir(images_dir):
            return

    extract_archives(archives_dir, images_dir, data_dir)


@cli.command()
@click.argument('images_dir', envvar='FLICKR_IMAGES_DIR', type=click.Path(file_okay=False))
@click.argument('data_dir', envvar='FLICKR_DATA_DIR', type=click.Path(file_okay=False))
@click.argument('default_album', default='unsorted')
def to_albums(images_dir, data_dir, default_album):
    """
    Reorders images from images_dir to albums according to information in data_dir
    :param images_dir: path to directory with flickr images
    :param data_dir: path to directory with account data
    :param default_album: name of the dir for photos with no album
    """
    images_to_albums(images_dir, data_dir, default_album)


@cli.command()
@click.argument('archives_dir', envvar='FLICKR_ARCHIVES_DIR', type=click.Path(file_okay=False))
@click.argument('images_dir', envvar='FLICKR_IMAGES_DIR', default='-',
                type=click.Path(file_okay=False, allow_dash=True))
@click.argument('data_dir', envvar='FLICKR_DATA_DIR', default='-',
                type=click.Path(file_okay=False, allow_dash=True))
@click.argument('default_album', default='unsorted')
def extract_to_albums(archives_dir, images_dir, data_dir, default_album):
    """
    Both extracting and reordering images to albums
    :param archives_dir: directory where archives are stored
    :param images_dir: path to directory with flickr images
    :param data_dir: path to directory with account data
    :param default_album: name of the dir for photos with no album
    """
    if data_dir == '-':
        data_dir = path.join(archives_dir, 'data')
        if not make_dir(data_dir):
            return
    if images_dir == '-':
        images_dir = path.join(archives_dir, 'images')
        if not make_dir(images_dir):
            return

    extract_archives(archives_dir, images_dir, data_dir)
    images_to_albums(images_dir, data_dir, default_album)


if __name__ == '__main__':
    cli()
