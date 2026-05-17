#!/usr/bin/env bash
set -euo pipefail

sed -i "s/^local\s\+all\s\+all\s\+peer/local   all             all                                     scram-sha-256/" /etc/postgresql/16/main/pg_hba.conf
grep "^local" /etc/postgresql/16/main/pg_hba.conf
pg_ctlcluster 16 main reload
