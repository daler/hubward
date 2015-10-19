#!/bin/bash
set -e
set -x

GROUP=encode
ASSEMBLY=dm3
for STUDY in encode-enhancers; do #encode-hic-domains; do

    rm -rf $GROUP/$ASSEMBLY/$STUDY

    # create a new template directory
    hubward new $GROUP $ASSEMBLY $STUDY

    # Create a git repo to illustrate the changes.
    (cd $GROUP && git init)
    (cd $GROUP/$ASSEMBLY/$STUDY && git add . && git commit -m "initial template for $STUDY")

    # copy over the edited example data.
    rsync -arv example/$GROUP/$ASSEMBLY/$STUDY/ $GROUP/$ASSEMBLY/$STUDY/

    rm -f $GROUP/$ASSEMBLY/$STUDY/raw-data/*

    # then make a commit that shows these changes
    (cd $GROUP/$ASSEMBLY && git commit -a -m "changes made by the $GROUP/$ASSEMBLY/$STUDY example")

    (cd $GROUP/$ASSEMBLY/$STUDY && python metadata-builder.py)

done

# this reads the metadata.yaml files and processes files as needed
hubward process $GROUP $ASSEMBLY

#hubward liftover $GROUP dm3 dm6

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
hubward build-trackhub $GROUP dm3 --config /tmp/test-hubward.yaml
