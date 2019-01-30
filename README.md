# flickr-recovery
Simple python tool to reorder photos into albums &amp; rename them to previous names after pooling flick dump

If for some reason you had to pull dump from flickr, you may find it pretty much useless
(several thousands of photos, just put with incorrect names into zip files +-4 Gb each)
So, this tool is intended to help you resorting albums structure according to
metadata from flickr itself


First of all, you can just find a guy who know python, and ask him to read this manual and perform required steps on your Mac / PC / etc.

If this one is not good enough, or something, you need to do two things: extract data, and reorder it. Both can be done with the flickr-recovery;
installation requires python3.5+ and pip (I'll recommend creating new virtualenv for it)
In this virtualenv (or just in base environment) run:
```shell
python -m pip install flickr-recovery
python -m flickr-recovery extract-to-albums /path/to/your/archives/all/in/one/dir
```

Make sure you have enough space on the partition with archives;
Or, if you want to extract images to different location, add images_dir to command call

```shell
python -m flickr-recovery extract-to-albums /path/to/your/archives/all/in/one/dir /path/to/images/
```

The directory should exists, if specified. Otherwise, it would be /path/to/your/archives/all/in/one/dir/images for images
and /path/to/your/archives/all/in/one/dir/data for account data
