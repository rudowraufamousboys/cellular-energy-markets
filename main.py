#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Cell import cell
from datetime import datetime, timedelta
from dateutil.parser import parse

# Init cells
cell1 = cell('cell1', 1)
cell2 = cell('cell2', 2)
cell3 = cell('cell3', 2)
cell4 = cell('cell4', 3)

# Iteration by time
def compareCells(cell1, cell2):
    startdate = parse(cell1.getStartDate())
    enddate = parse(cell1.getEndDate())
    while (startdate < enddate):
        print(startdate)
        # do the magic here
        startdate = startdate + timedelta(minutes=15)


compareCells(cell1, cell2)
