#!/bin/bash
set -e
set -x

LAB=encode
for STUDY in encode-enhancers encode-hic-domains; do

    # create a new template directory
    hubward new $LAB $STUDY

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
hubward process $LAB

hubward liftover $LAB dm3 dm6

# upload to track hub.
#
# This requires a ~/.hubward.yaml config file, e.g.,
#
#   hub_url_pattern: 'http://example.com/webapps/%s/compiled/compiled.hub.txt'
#   hub_remote_pattern: '/home/me/apps/%s/compiled/compiled.hub.txt'
#   host: example.com
#   user: me
#   email: me@example.com
#
hubward build-trackhub $LAB dm3 --config /tmp/test-hubward.yaml
