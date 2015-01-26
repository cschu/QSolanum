#!/bin/bash

mysql -D trost_prod -h cosmos -u schudoma -p < cleanup.sql
