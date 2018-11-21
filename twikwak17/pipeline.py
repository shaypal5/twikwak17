"""Running the entire data generation pipeline."""

import re
import time

from .phases import (
    phase1,
    phase2,
)
from .shared import (
    CfgKey,
    error_raising_cfg_val_get,
    phase_output_dpath,
    qprint,
    seconds_to_duration_str,
)


def run_pipeline(tpath=None, kpath=None, output_dpath=None):
    """Runs the entire data generation pipeline.

    Parameters
    ----------
    tpath : str, optional
        The path to the twitter7 dataset folder. If not given, the value keyed
        to 'twitter7_dpath' is looked up in the twikwak17 configuration file.
    kpath : str, optional
        The path to the kwak10www dataset folder. If not given, the value keyed
        to 'kwak10_dpath' is looked up in the twikwak17 configuration file.
    output_dpath : str, optional
        The path to the designated output folder. If not given, the value keyed
        to 'output_dpath' is looked up in the twikwak17 configuration file.
    """
    start = time.time()
    tpath = error_raising_cfg_val_get(tpath, CfgKey.TWITTER7_DPATH)
    kpath = error_raising_cfg_val_get(kpath, CfgKey.KWAK10_DPATH)
    output_dpath = error_raising_cfg_val_get(output_dpath, CfgKey.OUTPUT_DPATH)
    qprint((
        "\n\n######## twikwak17 ######## \n\n"
        "Starting to run the entire twikwak17 dataset generation pipeline."
        "\nPath to twitter7 dataset folder: {}\n"
        "Path to kwak10www dataset folder: {}\n"
        "Path to output folder: {}"
    ).format(tpath, kpath, output_dpath))

    phase1_out_dpath = phase_output_dpath(1, output_dpath)
    phase1(output_dpath=phase1_out_dpath, tpath=tpath)

    phase2_out_dpath = phase_output_dpath(2, output_dpath)
    phase2(output_dpath=phase2_out_dpath, kpath=kpath)

    end = time.time()
    print((
        "\n\nFinished running the twikwak17 pipeline.\n"
        "Run duration: {}".format(seconds_to_duration_str(end - start))
    ))


def run_phases(phases, tpath=None, kpath=None, output_dpath=None):
    """Runs the entire data generation pipeline.

    Parameters
    ----------
    phases : list of str
        The list of phases and subphases to run. E.g. ['2', '3.1', '4.2']
    tpath : str, optional
        The path to the twitter7 dataset folder. If not given, the value keyed
        to 'twitter7_dpath' is looked up in the twikwak17 configuration file.
    kpath : str, optional
        The path to the kwak10www dataset folder. If not given, the value keyed
        to 'kwak10_dpath' is looked up in the twikwak17 configuration file.
    output_dpath : str, optional
        The path to the designated output folder. If not given, the value keyed
        to 'output_dpath' is looked up in the twikwak17 configuration file.
    """
    start = time.time()
    tpath = error_raising_cfg_val_get(tpath, CfgKey.TWITTER7_DPATH)
    kpath = error_raising_cfg_val_get(kpath, CfgKey.KWAK10_DPATH)
    output_dpath = error_raising_cfg_val_get(output_dpath, CfgKey.OUTPUT_DPATH)
    qprint((
        "\n\n######## twikwak17 ######## \n\n"
        "Starting to run the following phases in the twikwak17 pipeline."
        "\n {}"
        "\nPath to twitter7 dataset folder: {}\n"
        "Path to kwak10www dataset folder: {}\n"
        "Path to output folder: {}"
    ).format(phases, tpath, kpath, output_dpath))

    phase1_out_dpath = phase_output_dpath(1, output_dpath)
    if '1' in phases:
        phase1(output_dpath=phase1_out_dpath, tpath=tpath)
    else:
        one_subphases = [p for p in phases if re.match("1\.\d", p)]
        if len(one_subphases) > 0:
            phase1(output_dpath=phase1_out_dpath, tpath=tpath,
                   subphases=one_subphases)

    phase2_out_dpath = phase_output_dpath(2, output_dpath)
    if '2' in phases:
        phase2(output_dpath=phase2_out_dpath, kpath=kpath)
    else:
        two_subphases = [p for p in phases if re.match("2\.\d", p)]
        if len(two_subphases) > 0:
            phase2(output_dpath=phase2_out_dpath, kpath=kpath,
                   subphases=two_subphases)

    end = time.time()
    print((
        "\n\nFinished running the twikwak17 pipeline.\n"
        "Run duration: {}".format(seconds_to_duration_str(end - start))
    ))