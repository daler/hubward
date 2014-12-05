#!/bin/bash
set -e
set -x

LAB=encode
for STUDY in encode-enhancers encode-hic-domains; do

    # create a new template directory
    hubmasonry new $LAB $STUDY

    # Create a git repo to illustrate the changes.
    (cd $LAB && git init)
    (cd $LAB/$STUDY && git add . && git commit -m "initial template for $STUDY")

    # copy over the edited example data.
    rsync -arv example/$LAB/$STUDY/ $LAB/$STUDY/

    # then make a commit that shows these changes
    (cd $LAB && git commit -a -m "changes made by the $LAB/$STUDY example")

    # call the script to get data
    bash $LAB/$STUDY/src/get-data.bash

done

# this reads the metadata.yaml files and processes files as needed
hubmasonry process $LAB

# upload to track hub.
#
# This requires a ~/.hubmasonry.yaml config file, e.g.,
#
#   hub_url_pattern: 'http://example.com/webapps/%s/compiled/compiled.hub.txt'
#   hub_remote_pattern: '/home/me/apps/%s/compiled/compiled.hub.txt'
#   host: example.com
#   user: me
#   email: me@example.com
#
hubmasonry build-trackhub $LAB dm3
