# flickr-recovery
Simple python tool to reorder photos into albums &amp; rename them to previous names after pooling flick dump


1) Data preparation

    1) Manually

        To extract data from multiple zip archives, try
        ```shell
        cd /dir/with/your/archives
        for i in data*.zip; do unzip "$i" -d "/dir/with/your/photos"; done
        ```
        but make sure that `/dir/with/your/photos` (replace with one you choose) actually exists.
        Also, you can just extract them one by one (but it's too long, of course)
        After that, extract the one left archive (which name does not start from `data-`) to another dir (not the same for the previous step)

    2) With script

        Run `flickr_unpack.sh "/dir/with/your/archives"` in this tool