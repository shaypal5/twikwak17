"""Phase 6 of the twikwak17 dataset generation process."""

import re
import gc
import time
import gzip
import zipfile
from contextlib import ExitStack


from twikwak17.shared import (
    qprint,
    seconds_to_duration_str,
    phase_output_report_fpath,
    set_output_report_file_handle,
    create_timestamped_report_file_copy,
    kwak10_twitter_rv_fpath,
    uid_to_gender_map_fpath_by_dpath,
    social_graph_fpath_by_dpath,
)


UID_TO_GENDER_REGEX = '(\d+) ([01])'


def get_uid_set(uid2gender_fpath):
    qprint("\nLoading uid-to-gender map from file...")
    lines_read = 0
    matching_lines = 0
    nonmatching_lines = 0
    bad_uid_lines = 0
    uid_set = set()
    with gzip.open(uid2gender_fpath, 'rt') as uid2gender_f:
        for line in uid2gender_f:
            lines_read += 1
            try:
                uid, gender = re.findall(UID_TO_GENDER_REGEX, line)[0]
            except IndexError:
                nonmatching_lines += 1
            try:
                uid_set.add(int(uid))
                matching_lines += 1
            except ValueError:
                bad_uid_lines += 1
                print(uid)
            if lines_read % 100000 == 0:
                qprint((
                    f"{lines_read:,} lines read; {matching_lines:,}"
                    f" lines matched. {bad_uid_lines} bad UIDs."), end='\r')

    qprint("User ID set loaded from file successfully.\n")
    return uid_set


UID_TO_UID_REGEX = '(\d+)[\t\s]+(\d+)'


def uids_from_edge_line(line):
    if len(line) < 1:
        return None, None
    uid, uid = re.findall(UID_TO_UID_REGEX, line)[0]
    return int(uid), int(uid)


def project_edge_list_to_user_intersection(
        twitter_rv_fpath, uid2gender_fpath, output_fpath):
    """Projects a user-to-user edge list to a given user intersection list.

    All edges between one (or two) users who cannot be found in the given user
    intersection list are removed in the new version of the user-to-user edge
    list file created.  d.

    Parameters
    ----------
    twitter_rv_fpath : str
        The full qualified path to the kwak10www's social graph file.
    uid2gender_fpath : str
        The full qualified path to the user-id-to-gender file.
    output_fpath : str
        The path to the designated output file.
    """
    qprint("Starting to run through social graph file...")
    uid_set = get_uid_set(uid2gender_fpath)
    with ExitStack() as stack:
        twitter_rv_z = stack.enter_context(
            zipfile.ZipFile(twitter_rv_fpath, 'r'))
        twitter_rv_f = stack.enter_context(
            twitter_rv_z.open('twitter_rv.net', 'r'))
        out_f = stack.enter_context(gzip.open(output_fpath, 'wt+'))
        uid1, uid2 = None, None
        lines_read = 0
        lines_dumped = 0
        edges_thrown = 0
        lines_to_dump = []

        edge_line = twitter_rv_f.readline()
        lines_read += 1

        while edge_line:
            edge_str = edge_line.decode("utf-8")
            uid1, uid2 = uids_from_edge_line(edge_str)
            if (uid1 in uid_set) and (uid2 in uid_set):
                lines_to_dump.append(f"{uid1} {uid2}")
            else:
                edges_thrown += 1
            if len(lines_to_dump) >= 100000:
                lines = "\n".join(lines_to_dump) + "\n"
                out_f.write(lines)
                lines_dumped += 100000
                lines_to_dump = None
                del lines_to_dump
                gc.collect()
                lines_to_dump = []
            edge_line = twitter_rv_f.readline()
            lines_read += 1
            if lines_read % 10000 == 0:
                qprint((
                    f"{lines_read:,} lines read|"
                    f"{lines_dumped:,} lines dumped|"
                    f"{edges_thrown:,} edges thrown. {uid1} ~ {uid2}"),
                    end='\r')
        if len(lines_to_dump) > 0:
            lines = "\n".join(lines_to_dump) + "\n"
            out_f.write(lines)
            lines_dumped += len(lines_to_dump)
        return int(edges_thrown), int(lines_dumped)


def phase6(phase5_output_dpath, phase6_output_dpath):
    """Removes non-intersection edges from kwak10's social graph.

    Parameters
    ----------
    phase5_output_dpath : str
        The path to the output directory of phase 5.
    phase6_output_dpath : str
        The path to the output directory of this phase, phase 6.
    """
    start = time.time()
    twitter_rv_fpath = kwak10_twitter_rv_fpath()
    uid2gender_fpath = uid_to_gender_map_fpath_by_dpath(phase5_output_dpath)
    output_fpath = social_graph_fpath_by_dpath(phase6_output_dpath)
    output_report_fpath = phase_output_report_fpath(6, phase6_output_dpath)

    with open(output_report_fpath, 'wt+') as output_report_f:
        set_output_report_file_handle(output_report_f)
        qprint("\n\n====== PHASE 6 =====")
        qprint((
            f"Starting phase 6 from \n{twitter_rv_fpath} and "
            f"\n{uid2gender_fpath} \ninput files to {output_fpath} "
            "output file."))

        edges_removed, edges_left = project_edge_list_to_user_intersection(
            twitter_rv_fpath=twitter_rv_fpath,
            uid2gender_fpath=uid2gender_fpath,
            output_fpath=output_fpath,
        )

        qprint((
            f"Removed {edges_removed:,} edges from the social graph; "
            f"{edges_left:,} remain. Graph dumped to {output_fpath}."))

        end = time.time()
        qprint((
            "Finished running phase 6 of the twikwak17 pipeline.\n"
            "Run duration: {}".format(seconds_to_duration_str(end - start))
        ))
    set_output_report_file_handle(None)
    create_timestamped_report_file_copy(output_report_fpath)
    return output_fpath
