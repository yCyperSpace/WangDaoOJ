#!/usr/bin/env bash
set -euo pipefail

sed -i "s/^#\?listen_addresses.*/listen_addresses = ''/" /etc/postgresql/16/main/postgresql.conf
grep "^listen_addresses" /etc/postgresql/16/main/postgresql.conf
pg_ctlcluster 16 main start
pg_lsclusters
pg_isready
