set -e
set -x
python setup.py install
git config --global user.email "none@example.com"
git config --global user.name "hubward-example"
cat >> .hubward.yaml <<EOF
hub_url_pattern: "http://localhost/{genome}/compiled/compiled.hub.txt"
hub_remote_pattern: "/root/{genome}/compiled/compiled.hub.txt"
host: localhost
user: root
email: root@localhost
EOF

service ssh start
mkdir -p /root/.ssh
ssh-keygen -f /root/.ssh/id_rsa -N ""
ssh-keyscan -H localhost >> /root/.ssh/known_hosts
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
#ssh-copy-id localhost
./run-example.bash
