#! /usr/bin/env python3

"""Senzing mapper template for transforming source data to Senzing JSON format."""

import argparse
import glob
import hashlib
import json
import sys
import time
from collections import defaultdict

# import csv or pandas here


class SenzingJson:
    """senzing json class"""

    def __init__(self):
        """initialization method"""
        self._json = {"DATA_SOURCE": "", "RECORD_ID": "", "RECORD_TYPE": ""}
        self.features = []
        self.building_features = {}
        self.payload = defaultdict(list)

    def set_data_source(self, _value):
        """set the data source"""
        if _value:
            self._json["DATA_SOURCE"] = _value

    def set_record_id(self, _value):
        """set the record_id"""
        self._json["RECORD_ID"] = _value

    def set_record_type(self, _value):
        """set the record_type"""
        if _value:
            self._json["RECORD_TYPE"] = _value

    def _clean_dict(self, _dict):
        """clean dict values - strip strings and filter empty values"""
        for k, v in _dict.items():
            if isinstance(v, str):
                v = v.strip()
            if v:
                yield k, v

    def add_feature(self, name_or_dict, _dict=None):
        """Add a feature - standalone or grouped.

        Examples:
            json_data.add_feature({"SSN_NUMBER": raw_data["ssn"]})
            json_data.add_feature({"DATE_OF_BIRTH": raw_data["dob"]})

            json_data.add_feature("name1", {"NAME_FIRST": raw_data["first_name"]})
            json_data.add_feature("name1", {"NAME_LAST": raw_data["last_name"]})

            json_data.add_feature("addr1", {"ADDR_LINE1": raw_data["addr1"]})
            json_data.add_feature("addr1", {"ADDR_CITY": raw_data["city"]})
        """
        if _dict is None:
            # Standalone feature: add_feature({"KEY": value})
            feature = dict(self._clean_dict(name_or_dict))
            if feature:
                self.features.append(feature)
        else:
            # Grouped feature: add_feature("group_name", {"KEY": value})
            name = name_or_dict
            if name not in self.building_features:
                self.building_features[name] = {}
                self.features.append(self.building_features[name])
            for k, v in self._clean_dict(_dict):
                if k in self.building_features[name]:
                    raise ValueError(f"Attribute '{k}' already set for feature '{name}'")
                self.building_features[name][k] = v

    def add_payload(self, _dict):
        """add payload attributes

        Example:
            json_data.add_payload({"job_category": raw_data["job_category"]})
            json_data.add_payload({"job_title": raw_data["job_title"]})
        """
        for k, v in self._clean_dict(_dict):
            self.payload[k].append(str(v))

    def render(self):
        """render the final JSON object with all features and payload"""
        self._json["FEATURES"] = [f for f in self.features if f]
        for k, v in self.payload.items():
            self._json[k] = " | ".join(v) if len(v) > 1 else v[0]
        return self._json


def compute_record_hash(target_dict, attr_list=None):
    """compute a hash to use for record_id if needed"""
    if attr_list:
        string_to_hash = ""
        for attr_name in sorted(attr_list):
            string_to_hash += (
                " ".join(str(target_dict[attr_name]).split()).upper()
                if attr_name in target_dict and target_dict[attr_name]
                else ""
            ) + "|"
    else:
        string_to_hash = json.dumps(target_dict, sort_keys=True)
    return hashlib.md5(bytes(string_to_hash, "utf-8")).hexdigest()


def map_record(raw_data):
    """primary mapping function"""
    json_list = []

    # place any filters needed here

    # place any calculations needed here

    # initialize
    json_data = SenzingJson()
    json_data.set_data_source("")  # supply a value for this data source
    json_data.set_record_id(raw_data[""])  # supply a 100% unique attribute
    json_data.set_record_type("")  # should be PERSON or ORGANIZATION

    # place column mappings here
    # json_data.add_feature({"ATTRIBUTE_NAME": raw_data.get("column_name")})
    # json_data.add_feature("group1", {"ATTRIBUTE_NAME": raw_data.get("column_name")})

    mapped_data = json_data.render()
    json_list.append(mapped_data)

    return json_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="the name of the input file")
    parser.add_argument("-o", "--output_file", dest="output_file", help="the name of the output file")
    parser.add_argument(
        "-s", "--start-line", dest="start_line", type=int, default=1, help="line number to start at (default: 1)"
    )
    args = parser.parse_args()

    file_list = glob.glob(args.input_file)
    if not file_list:
        print("\nNo files found matching the input file specification\n")
        sys.exit(1)

    if args.output_file:
        output_file = open(args.output_file, "w", encoding="utf-8")
    else:
        output_file = None

    proc_start_time = time.time()
    shut_down = False
    input_row_count = 0
    output_row_count = 0

    try:
        file_num = 0
        for file_name in file_list:
            file_num += 1
            print(f"reading file {file_num} of {len(file_list)}: {file_name}")

            # open reader here

            for row in reader:  # pylint: disable=undefined-variable
                input_row_count += 1
                if input_row_count < args.start_line:
                    continue

                for json_data in map_record(row):
                    if output_file:
                        output_file.write(json.dumps(json_data) + "\n")
                    else:
                        print(f"--- Record {input_row_count} ---")
                        print(json.dumps(json_data, indent=4))
                        response = input("Press Enter for next, 'r' to show raw source (Ctrl+C to abort): ")
                        if response.lower() == "r":
                            print("\nSource:")
                            print(json.dumps(row, indent=4, default=str))
                            input("\nPress Enter for next record (Ctrl+C to abort) ...")
                    output_row_count += 1

                if input_row_count % 10000 == 0:
                    print(f"{input_row_count} rows processed, {output_row_count} rows written")

            # close reader here

    except KeyboardInterrupt:
        print("\nUSER INTERRUPT! Shutting down ... (please wait)\n")
        shut_down = True

    elapsed_mins = round((time.time() - proc_start_time) / 60, 1)
    run_status = ("completed in" if not shut_down else "aborted after") + f" {elapsed_mins} minutes"
    print(f"{input_row_count} rows processed, {output_row_count} rows written, {run_status}\n")

    if output_file:
        output_file.close()

    sys.exit(0)
