# Copyright 2022 GlobalFoundries PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Convert the lyrdb klayout database file to GDSII file 

Usage:
    convert_lyrdb_to_gds.py (--help| -h)
    convert_lyrdb_to_gds.py --db=<lyrdb_file_path>

Options:
    --help -h                           Print this help message.
    --db=<lyrdb_file_path>              Path to the results database.
"""

from docopt import docopt
from tqdm import tqdm
import time
import gdstk
import xml.etree.ElementTree as ET

import pandas as pd
import re
import json


def darw_polygons(polygon_data, cell, lay_num, dt, path_width):
    """
    darw_polygons _summary_

    Parameters
    ----------
    polygon_data : _type_
        _description_
    """

    # polygon: (985.739,294.774;985.739,295.776;986.741,295.776;986.741,294.774)

    polygon_data = re.sub(r"\s+", "", polygon_data)
    polygon_data = re.sub(r"[()]", "", polygon_data)

    print("## POLYGON DATA : ", polygon_data)
    tag_split = polygon_data.split(":")
    tag = tag_split[0]
    poly_txt = tag_split[1]
    polygons = re.split(r"[/|]", poly_txt)

    print("    Type   ", tag)
    print("    All polygons   ", polygons)

    if tag == "polygon":
        for poly in polygons:
            points = [
                (float(p.split(",")[0]), float(p.split(",")[1]))
                for p in poly.split(";")
            ]
            print("           All points : ", points)
            cell.add(gdstk.Polygon(points, lay_num, dt))

    elif tag == "edge-pair":
        for poly in polygons:
            points = [
                (float(p.split(",")[0]), float(p.split(",")[1]))
                for p in poly.split(";")
            ]
            print("           All points : ", points)
            cell.add(gdstk.FlexPath(points, path_width, layer=lay_num, datatype=dt))

    elif tag == "edge":
        for poly in polygons:
            points = [
                (float(p.split(",")[0]), float(p.split(",")[1]))
                for p in poly.split(";")
            ]
            print("           All points : ", points)
            cell.add(gdstk.FlexPath(points, path_width, layer=lay_num, datatype=dt))
    else:
        print(f"## Error unknown type: {tag} ignored")

    # polygon_points = list()
    # if "polygon" in polygon_data:
    #     polygon_points = re.search(r'\((.*?)\)',polygon_data).group(1).split(";")

    # point = float()
    # points = []
    # for point in polygon_points:
    #     points.append(f"({point})")

    # print (polygon_data)


def parse_results_db(results_database: str):
    """
    This function will parse Klayout database for analysis.

    Parameters
    ----------
    results_database : string or Path object
        Path string to the results file

    Returns
    -------
    set
        A set that contains all rules in the database with violations
    """

    rule_info = []
    rule_lay_num = 10000
    path_width = 0.01

    t0 = time.time()
    cell_name = ""
    lib = None
    cell = None
    in_item = False
    rule_data_type_map = list()

    for ev, elem in tqdm(ET.iterparse(results_database, events=("start", "end"))):

        if elem.tag != "item" and not in_item:
            elem.clear()
            continue

        if elem.tag != "item" and in_item:
            continue

        if elem.tag == "item" and ev == "start":
            in_item = True
            continue

        rules = elem.findall("category")
        values = elem.findall("values")

        if len(values) > 0:
            polygons = values[0].findall("value")
        else:
            polygons = []

        if cell_name == "":
            all_cells = elem.findall("cell")

            if len(all_cells) > 0:
                cell_name = all_cells[0].text

                if cell_name is None:
                    elem.clear()
                    continue

                # print(cell_name)

                lib = gdstk.Library(cell_name)
                cell = lib.new_cell(cell_name)

        if len(rules) > 0:
            rule_name = rules[0].text.replace("'", "")
            if rule_name is None:
                elem.clear()
                continue

            # print(rule_name)
        else:
            elem.clear()
            continue

        if not rule_name in rule_data_type_map:
            rule_data_type_map.append(rule_name)

        ## draw polygons here.
        if not cell is None:
            for p in polygons:
                polygons = darw_polygons(
                    p.text,
                    cell,
                    rule_lay_num,
                    rule_data_type_map.index(rule_name) + 1,
                    path_width,
                )
                print(type(p))
                # cell.add(gdstk.)
                break

        ## Clear memeory
        in_item = False
        elem.clear()

        lib.write_gds(f"{cell_name}.gds")

    print("Total read time: {}".format(time.time() - t0))
    print(rule_data_type_map)


if __name__ == "__main__":

    args = docopt(__doc__, version="lyrdb to gds converter: 0.1")

    parse_results_db(args["--db"])
