import time
from helpers.config import *
from helpers.get_spl_data import get_doc_dailymed, extract_doc_content
from helpers.inactive_ingredients_data import get_todd_ingredients, possible_inactive_ingredients, get_set_id_from_ndc
from helpers.prompt import *
from helpers.extraction import extract_ingredients
from helpers.util import init_loggers, compare_results, log_session, log_init_session, print_time
# from helpers.data_sets import *

list_searches = """0591-0860-01
0591-0860-05
0591-0861-01
0591-0861-05
0591-0862-01
0591-0862-05""".split('\n')

if __name__ == '__main__':
    start = time.time()

    # if type(list_searches) != list:
    if isinstance(list_searches, list):
        pass
    else:
        list_searches = [list_searches]

    if os.environ['LOG_DIR'] == '':
        log_filename = None
    else:
        log_filename = f"{os.environ['LOG_DIR']}/run_{time.strftime('%Y_%m_%d.%H_%M_%S')}.log"

    log_init_session(log_filename)
        
    if TYPE_OF_OUTPUT == 'normal':
        logger = init_loggers('fsb-inactive')
        logger.info(f'Using Model:  MODEL {os.environ["MODEL_GROUP1"]}\n')
    else:
        logger = None

    # iterated through a list of setids
    for i, search in enumerate(list_searches):

        if NDC_SETID == 'ndc':
            setid, ndcs, ndc11 = get_set_id_from_ndc(search)
        else:
            setid = search
            ndcs, ndc11 = [], ""

        if TYPE_OF_OUTPUT == 'simple':
            if NDC_SETID == 'ndc':
                print(f'[{i}] {setid}/{search}: ', end='')
            else:
                print(f'[{i}] {setid}: ', end='')
            logger = None

        # Extract from Daily Med the content of the SPL of setID
        filename = get_doc_dailymed(setid, method=os.environ["EXTRACT_METHOD"], _logger=logger)
        if filename is None:
            continue

        document = extract_doc_content(filename, _logger=logger)
        if document is None:
            continue

        inactive_ingredients, inactive2group, inactive2ids, id2inactive = possible_inactive_ingredients(filter_alias=SELECTED_ALIAS_TYPE, filter_group=SELECTED_GROUPS, logger=logger)
        
        if inactive_ingredients is None:
            continue

        todd_ing_ids = get_todd_ingredients(search, NDC_SETID, ndc11, filter_group=SELECTED_GROUPS)
        if logger is not None:
            logger.info(f"Found Todd Ingredients: {todd_ing_ids}\n")

        found_ingredients_ids, product = extract_ingredients(setid, search, ndcs, NDC_SETID, inactive_ingredients, inactive2group, inactive2ids, document, _filter_groups=SELECTED_GROUPS, _logger=logger, _true_ing=todd_ing_ids)
        if found_ingredients_ids is None:
            found_ingredients = ['error']
            continue

        compare_msg = compare_results(todd_ing_ids, "ToddIngredients", found_ingredients_ids, "LLMFound", id2inactive, logger, toprint=False)
        print(f"{compare_msg}", end="")

        log_session(log_filename, f"{setid}/{search}: {compare_msg}")

    if logger is not None:
        logger.info(f"Took overall: {print_time(time.time() - start)}\n")
    else:
        print(f"Took overall: {print_time(time.time() - start)}\n")

    log_session(log_filename, f"Took overall: {print_time(time.time() - start)}\n")
