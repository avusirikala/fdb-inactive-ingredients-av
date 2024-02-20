import logging
import os
import sys


def print_time(duration):
    """Print elapsed time in a user-friendly format HH:MM:SS

    Parameters
    ----------
    duration : float
        Duration to which convert

    Returns
    -------
    string : str
        String of duration converted into format HH:MM:SS
    """
    h = int(duration // (60 * 60))
    duration -= h * (60 * 60)
    m = int(duration // 60)
    duration -= m * 60
    s = int(duration)
    duration -= s
    ms = f"{duration:.2f}".split('.')[-1]

    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2):}.{ms}"


def init_loggers(name='simple_example'):
    """ Function to create logger

    Parameters
    ----------
    name : str
        Name to identify the logger

    Returns
    -------
    logger : logging
        logger of logging file format
    """
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # add formatter to stdout_handler
    stdout_handler.setFormatter(formatter)

    # add stdout_handler to logger
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    logger.info(f'Started logger named: {name}')

    return logger


def log_session(log_filename, msg):
    """ Logs a message to the logfile. Helper Function to ease logging

    Parameters
    ----------
    log_filename : str
        Path to the logfile to log
    msg : str
        Message to be logged into the logfile

    Returns
    -------
    None
    """
    if log_filename is None:
        return

    if msg[-1] != '\n':
        msg += '\n'

    with open(log_filename, "a+") as f:
        f.write(msg)


def log_init_session(log_filename):
    """Logs the initial configuration of the run to the log file (so one can compare afterwards)

    Parameters
    ----------
    log_filename : str
        Path to the logfile to log

    Returns
    -------
    None
    """

    if log_filename is None:
        return

    log_session(log_filename, f'Using MODELS:\n')
    log_session(log_filename, f'\tMODEL Group 1: {os.environ["MODEL_GROUP1"]}\n')
    log_session(log_filename, f'\tMODEL Group 2-3: {os.environ["MODEL_GROUP2-3"]}\n')
    log_session(log_filename, f'\tMODEL Group 4-5: {os.environ["MODEL_GROUP4-5"]}\n')
    log_session(log_filename, f'Extract XML Method: {os.environ["XML_EXTRACTION"]}')
    log_session(log_filename, f'Output Type: {os.environ["TYPE_OF_OUTPUT"]}')
    log_session(log_filename, f'Indexing Mode: {os.environ["INDEXING_METHOD"]}')
    log_session(log_filename, f'Prompt Set: {os.environ["PROMPT_SET"]}')
    log_session(log_filename, f'\tQA Prompt: {os.environ["qa_prompt"]}')
    log_session(log_filename, f'\tSchema Main List: {os.environ["schema_main_list"]}')
    log_session(log_filename, f'\tSchema Printing List: {os.environ["schema_printing_list"]}')
    log_session(log_filename, f'\tSchema Both Printing and Other Parts: {os.environ["schema_both_print_list"]}')
    log_session(log_filename, f'\tProduct Route: {os.environ["schema_product_route"]}')
    log_session(log_filename, f'\tProduct Dosage Form: {os.environ["schema_product_df"]}')
    log_session(log_filename, f'\tMint: {os.environ["schema_mint_found"]}')
    log_session(log_filename, f'\tMenthol: {os.environ["schema_menthol_found"]}')
    log_session(log_filename, f'\tGroup 2-3 Query: {os.environ["schema_group2_3_query"]}')
    log_session(log_filename, f'\tGroup 4-5 Query: {os.environ["schema_group4_5_query"]}')
    log_session(log_filename, f'\n\n')


def compare_results(ids1, name1, ids2, name2, id2inactive, _logger=None, toprint=True):
    """ Method to compare results between different methods

    Parameters
    ----------
    ids1 : list
        Inactive Ingredients ID List of Method 1
    name1 : str
        Name of Method 1
    ids2 : list
        Inactive Ingredients ID List of Method 2
    name2 : str
        Name of Method 2
    id2inactive : dict
        Dictionary with (inactive ingredient ID): (inactive ingredient name)
    _logger : logging
        logger object (or None, in case no logging)
    toprint : bool
        To Print or not the outcome

    Returns
    -------
    msg : str
        output of comparison
    """

    ids2 = sorted(ids2)
    ids1 = sorted(ids1)
    found_in_1_not_2 = [id2inactive[c] for c in ids1 if c not in ids2]
    found_in_2_not_1 = [id2inactive[c] for c in ids2 if c not in ids1]

    msg = ""

    if _logger is not None:
        msg += f"'{name1}' vs '{name2}'\n"

        if len(found_in_1_not_2) > 0:
            msg += f"In '{name1}' not in '{name2}': {', '.join(found_in_1_not_2)}\n"
        else:
            msg += f"All in '{name1}' in '{name2}'\n"

        if len(found_in_2_not_1) > 0:
            msg += f"In '{name2}' not in '{name1}': {', '.join(found_in_2_not_1)}\n"
        else:
            msg += f"All in '{name2}' in '{name1}'\n"

        _logger.info(msg)

    else:
        if len(found_in_1_not_2) == len(found_in_2_not_1) == 0:
            msg += 'all ok.\n'
        elif len(found_in_1_not_2) > 0 and len(found_in_2_not_1) == 0:
            msg += f'missing: {", ".join(found_in_1_not_2)} ; expected: {ids1} ; got: {ids2} \n'
        elif len(found_in_1_not_2) == 0 and len(found_in_2_not_1) > 0:
            msg += f'too much: {", ".join(found_in_2_not_1)} ; expected: {ids1} ; got: {ids2} \n'
        else:
            msg += f'missing: {", ".join(found_in_1_not_2)} ; too much: {", ".join(found_in_2_not_1)} ; expected: {sorted(ids1)} ; got: {sorted(ids2)} \n'

        if toprint:
            print(msg, end='')

    return msg


def statistics(errors, config="data/LLM03_RI.txt"):
    """ Statistics function used on local validation excel to check which Group has errors, what is missing...

    Parameters
    ----------
    errors : str
        error string of all the error messages in each NDC  / SetID
    config : str
        path to the configuration file of Reported Inactive Ingredients information to extract <inactive ID> -> <Group> (dictionary)

    Returns
    -------
    llm : list
        list of returned inactive ingredients IDs from LLM
    llm_missing : list
        list of inactive ingredients IDs that should have been in LLM but aren't (according to Todd's ingredients)
    group_missing : list
        list of groups from inactive ingredients that should have been in LLM but aren't (according to Todd's ingredients)
    llm_toomuch : list
        list of inactive ingredients IDs that were in LLM but shouldn't (according to Todd's ingredients)
    group_toomuch : list
        list of groups from ingredients that were in LLM but shouldn't (according to Todd's ingredients)
    """
    import pandas as pd

    id2group = pd.read_csv(config).set_index('ReportedInactiveID').to_dict()["GroupNumber"]

    if not isinstance(errors, list):
        errors = errors.split('\n')

    todd = list(map(eval, [e[e.find("["):e.find(']')+1] for e in errors]))
    llm = list(map(eval, [e[e.rfind("["):e.rfind(']') + 1] for e in errors]))

    llm_missing = [[_t for _t in t if _t not in m] for t, m in zip(todd, llm)]
    group_missing = [[id2group[_l] for _l in m] for m in llm_missing]
    llm_toomuch = [[_l for _l in m if _l not in t] for t, m in zip(todd, llm)]
    group_toomuch = [[id2group[_l] for _l in m] for m in llm_toomuch]

    return llm, llm_missing, group_missing, llm_toomuch, group_toomuch
