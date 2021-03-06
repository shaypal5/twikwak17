"""Running the entire data generation pipeline."""

import re
import time
import shutil

from .phases import (
    phase1,
    phase2,
    phase3,
    phase4,
    phase5,
    phase6,
    phase7,
)
from .shared import (
    CfgKey,
    error_raising_cfg_val_get,
    phase_output_dpath,
    qprint,
    seconds_to_duration_str,
    Session,
    # phase products meant for final output
    uid_to_gender_map_fpath_by_dpath,
    uid_list_fpath_by_dpath,
    social_graph_fpath_by_dpath,
    graphml_fpath_by_dpath,
    # output file paths
    output_social_graph_fpath,
    output_uid2gender_fpath,
    output_uid_list_fpath,
    output_graphml_fpath,
)


def safe_move(source_fpath, target_fpath, description):
    try:
        shutil.move(source_fpath, target_fpath)
        qprint(f"{description} moved to {target_fpath}")
    except FileNotFoundError:
        qprint((f"{description} file not found in {source_fpath}."
                " Either is was not generated or was already moved."
                " File moving cancelled."))


def safe_copy(source_fpath, target_fpath, description):
    try:
        shutil.copy(source_fpath, target_fpath)
        qprint(f"{description} copied to {target_fpath}")
    except FileNotFoundError:
        qprint((f"{description} file not found in {source_fpath}."
                " Copying cancelled."))


def run_pipeline(
        tpath=None, kpath=None, output_dpath=None, session_fpath=None):
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
    session_fpath : str, optional
        The path to the save file of a previous session to continue. If not
        given, a new session is created.
    """
    phases = ['1', '2', '3', '4', '5']
    run_phases(
        phases=phases, tpath=tpath, kpath=kpath, output_dpath=output_dpath,
        session_fpath=session_fpath)


def run_phases(
        phases, tpath=None, kpath=None, output_dpath=None,
        session_fpath=None):
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
    session_fpath : str, optional
        The path to the save file of a previous session to continue. If not
        given, a new session is created.
    """
    if session_fpath is None:
        print("\n\nStarting a new twikwak17 session.")
        start = time.time()
        kwargs = {'tpath': tpath, 'kpath': kpath, 'output_dpath': output_dpath}
        session = Session(
            start_time=start,
            kwargs=kwargs,
            phases=None,
            last_completed_subphase=None,
        )
        last_completed_phase = '0'
        # last_completed_subphase = None
    else:
        qprint(
            "\n\nRestoring twikwak17 session from {}...".format(session_fpath))
        session = Session.load(session_fpath)
        start = session.start_time
        phases = session.kwargs['phases']
        tpath = session.kwargs['tpath']
        kpath = session.kwargs['kpath']
        output_dpath = session.kwargs['output_dpath']

    tpath = error_raising_cfg_val_get(tpath, CfgKey.TWITTER7_DPATH)
    kpath = error_raising_cfg_val_get(kpath, CfgKey.KWAK10_DPATH)
    output_dpath = error_raising_cfg_val_get(
        output_dpath, CfgKey.OUTPUT_DPATH)
    qprint((
        "\n\n######## twikwak17 ######## \n\n"
        "Starting to run the twikwak17 dataset generation pipeline."
        "\nPhases to run: {}\n"
        "\nPath to twitter7 dataset folder: {}\n"
        "Path to kwak10www dataset folder: {}\n"
        "Path to output folder: {}"
    ).format(phases, tpath, kpath, output_dpath))

    # big_phases = set([x[0] for x in phases])

    phase1_out_dpath = phase_output_dpath(1, output_dpath)
    if '1' in phases and last_completed_phase < '1':
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

    phase3_out_dpath = phase_output_dpath(3, output_dpath)
    if '3' in phases:
        phase3(
            phase1_output_dpath=phase1_out_dpath,
            phase2_output_dpath=phase2_out_dpath,
            phase3_output_dpath=phase3_out_dpath,
        )

    phase4_out_dpath = phase_output_dpath(4, output_dpath)
    if '4' in phases:
        phase4(
            phase1_output_dpath=phase1_out_dpath,
            phase3_output_dpath=phase3_out_dpath,
            phase4_output_dpath=phase4_out_dpath,
        )

    phase5_out_dpath = phase_output_dpath(5, output_dpath)
    if '5' in phases:
        phase5(
            phase2_output_dpath=phase2_out_dpath,
            phase4_output_dpath=phase4_out_dpath,
            phase5_output_dpath=phase5_out_dpath,
        )

    phase6_out_dpath = phase_output_dpath(6, output_dpath)
    if '6' in phases:
        phase6(
            phase5_output_dpath=phase5_out_dpath,
            phase6_output_dpath=phase6_out_dpath,
        )

    phase7_out_dpath = phase_output_dpath(7, output_dpath)
    if '7' in phases:
        phase7(
            phase5_output_dpath=phase5_out_dpath,
            phase6_output_dpath=phase6_out_dpath,
            phase7_output_dpath=phase7_out_dpath,
        )

    qprint("Copying output files to final output folder...")

    uid2gender_fpath = uid_to_gender_map_fpath_by_dpath(phase5_out_dpath)
    target_uid2gender = output_uid2gender_fpath(output_dpath)
    safe_copy(uid2gender_fpath, target_uid2gender, "UID-to-gender map")

    uid_list_fpath = uid_list_fpath_by_dpath(phase5_out_dpath)
    target_uid_list_fpath = output_uid_list_fpath(output_dpath)
    safe_copy(uid_list_fpath, target_uid_list_fpath, "User ID list")

    social_graph_fpath = social_graph_fpath_by_dpath(phase6_out_dpath)
    target_socgraph_fpath = output_social_graph_fpath(output_dpath)
    safe_move(social_graph_fpath, target_socgraph_fpath, "Social graph")

    graphml_fpath = graphml_fpath_by_dpath(phase7_out_dpath)
    target_graphml_fpath = output_graphml_fpath(output_dpath)
    safe_move(graphml_fpath, target_graphml_fpath, "Graphml graph")

    graphml_s_fpath = graphml_fpath_by_dpath(phase7_out_dpath, sample=True)
    target_graphml_s_fpath = output_graphml_fpath(output_dpath, sample=True)
    safe_copy(graphml_s_fpath, target_graphml_s_fpath, "Graphml sample graph")

    end = time.time()
    print((
        "\n\nFinished running the twikwak17 pipeline.\n"
        "Run duration: {}".format(seconds_to_duration_str(end - start))
    ))
