#!/bin/bash
set -e
set -x

GROUP=encode
for STUDY in encode-enhancers encode-hic-domains; do

    # create a new template directory
    hubward new $GROUP $STUDY

    # Create a git repo to illustrate the changes.
    (cd $GROUP && git init)
    (cd $GROUP/$STUDY && git add . && git commit -m "initial template for $STUDY")

    # copy over the edited example data.
    rsync -arv example/$GROUP/$STUDY/ $GROUP/$STUDY/

    # then make a commit that shows these changes
    (cd $GROUP && git commit -a -m "changes made by the $GROUP/$STUDY example")

    # call the script to get data
    bash $GROUP/$STUDY/src/get-data.bash

done

# this reads the metadata.yaml files and processes files as needed
hubward process $GROUP

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
