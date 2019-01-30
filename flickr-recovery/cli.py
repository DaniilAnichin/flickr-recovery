#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from os import path

import click

from .file_processing import extract_archives, images_to_albums
from .utils import make_dir


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
