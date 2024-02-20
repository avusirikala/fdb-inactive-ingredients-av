import os
import time
import pandas as pd
from langchain.output_parsers import StructuredOutputParser
from helpers.schemas import prepare_schema_index_query_g1_setid, prepare_schema_query_g2_3, prepare_schema_query_g4, \
    prepare_schema_index_query_g1_ndc_pre, prepare_schema_index_query_g1_ndc_pos, prepare_schema_query_g5
from helpers.util import print_time
from langchain.embeddings import OpenAIEmbeddings
from llama_index import ServiceContext, GPTListIndex, GPTKeywordTableIndex, \
    GPTKnowledgeGraphIndex, PromptHelper, OpenAIEmbedding, LangchainEmbedding, GPTVectorStoreIndex
from llama_index.callbacks import LlamaDebugHandler, CallbackManager
from llama_index.llms import OpenAI, AzureOpenAI
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import TokenTextSplitter


RULES_CONFIG_FILE = 'data/LLM05_GROUP_2-5_RULES.csv'


def decompose(txt, remove_parentheses=False):
    """ Helper function to decompose aliases and ingredients names, to make it easier to match

    Parameters
    ----------
    txt : str
        text to decompose in tokens
    remove_parentheses : bool
        whether to remove everything which is inside parentheses or not

    Returns
    -------
    list
        tokens decomposed for easier matching
    """

    import re

    if remove_parentheses:
        if '(' in txt and ')' in txt:
            txt = re.sub(r'\([^)]*\)', '', txt)
        else:
            return []

    # words to ignore for matching
    ignore_parts = ['no.', 'carmine', 'indigo', 'nf']

    res = re.findall("\w+[&]*\w*\.*", txt)

    return [r for r in res if r not in ignore_parts]


def filter_valid_ingredients(inactive, inprint, both_inprint_outside, valid_invalid, already_decomposed=False):
    """Method to filter only the ingredients which are in valid list and follow the rules (ex: ink)

    Parameters
    ----------
    inactive : list
        inactive ingredients found by the LLM
    inprint : list
        inactive ingredients which are also present in the ink found by the LLM
    both_inprint_outside : list
        inactive ingredients which are also present in the ink and also outside found by the LLM
    valid_invalid : dict
        valid inactive ingredients list and their aliases
    already_decomposed : bool
        whether the list of valid inactive ingredients is already decomposed or not (this speeds processing)

    Returns
    -------
    : list
        Valid list of inactive ingredients filtered out
    """
    decomposed_inactive = [sorted(decompose(i)) for i in inactive] + [sorted(decompose(i, remove_parentheses=True)) for i in inactive]

    decompose_inprint = [sorted(decompose(i)) for i in inprint]
    decompose_inprint_outside = [sorted(decompose(i)) for i in both_inprint_outside]
    decompose_inprint = [i for i in decompose_inprint if i not in decompose_inprint_outside and i != []]

    decomposed_inactive = [i for i in decomposed_inactive if i not in decompose_inprint and i != []]
    if already_decomposed:
        decomposed_valid_invalid = valid_invalid
    else:
        decomposed_valid_invalid = {i: [sorted(decompose(a)) for a in al] for i, al in valid_invalid.items()}
    answer = []

    for i, al in decomposed_valid_invalid.items():
        if len(decomposed_inactive) == 0:
            break
        for a in al:
            if a in decomposed_inactive:
                answer.append(i)
                decomposed_inactive.remove(a)
                break

    return list(set(answer))


def index_data(doc_to_index,
               deployment_env_key=None,
               model_env_key="MODEL_GROUP1",
               indexing_structure=os.environ['INDEXING_METHOD']):
    """ Method to get Service Context

    Parameters
    ----------
    doc_to_index : Document
        Document to index
    deployment_env_key : str
        Environment variable containing Azure OpenAI deployment name (Azure only)
    model_env_key : str
        Environment variable name containing OpenAI Model name
    indexing_structure : str
        Indexing structure name: list-index | vector-store | keyword-table | knowledge-graph

    Returns
    -------
    service_context : llama_index.indices.service_context.ServiceContext
        Service context containing Model definition, context window, ....
    """

    model = os.environ[model_env_key]
    if os.environ['AZURE_API'] != '':
        deployment = os.environ.get(deployment_env_key, model)
        llm_predictor = AzureOpenAI(engine=deployment,
                                    model=model,
                                    temperature=0)
        
        if os.environ["OPENAI_USE_EMBEDDINGS"] == "True":
            embed_model_name = os.environ["OPENAI_EMBEDDINGS_MODEL"]
            embed_deployment_name = os.environ.get("OPENAI_EMBEDDINGS_DEPLOYMENT", embed_model_name)
            
            try:
                embed_model = LangchainEmbedding(OpenAIEmbeddings(
                    deployment=embed_deployment_name,
                    model=embed_model_name,
                    openai_api_base=os.environ["OPENAI_API_BASE"],
                    openai_api_type="azure",
                ))

            except Exception as e:
                print("Error LangChainEmbedding:", e)
        else:
            embed_model = None
    else:
        llm_predictor = OpenAI(temperature=0, model=model)

        if os.environ["OPENAI_USE_EMBEDDINGS"] == "True":
            embed_model = OpenAIEmbedding()
        else:
            embed_model = None

    if os.environ['DEBUG'] == 'True':
        llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        callback_manager = CallbackManager([llama_debug])
    else:
        callback_manager = None

    node_parser = SimpleNodeParser(text_splitter=TokenTextSplitter(chunk_size=2024, chunk_overlap=20))
    prompt_helper = PromptHelper(num_output=512,
                                 chunk_overlap_ratio=0.2,
                                 chunk_size_limit=None,
                                 # context_window=4000,
                                 )
    prompt_helper = prompt_helper.from_llm_metadata(llm_predictor.metadata)

    service_context = ServiceContext.from_defaults(llm=llm_predictor, callback_manager=callback_manager,
                                                   # node_parser=node_parser,
                                                   embed_model=embed_model,
                                                   prompt_helper=prompt_helper
                                                   )

    if indexing_structure == 'vector-store':
        index = GPTVectorStoreIndex.from_documents(doc_to_index, service_context=service_context)
    elif indexing_structure == 'list-index':
        index = GPTListIndex.from_documents(doc_to_index, service_context=service_context)
    elif indexing_structure == 'keyword-table':
        index = GPTKeywordTableIndex.from_documents(doc_to_index, service_context=service_context)
    elif indexing_structure == 'knowledge-graph':
        index = GPTKnowledgeGraphIndex.from_documents(doc_to_index, service_context=service_context)
    else:
        index = None

    return index


def process_output_group1(txt, output_parser, possible_inactive, _logger=None):
    """ Method to extract the outcome of LLM for group 1 extraction

    Parameters
    ----------
    txt : str
        raw text coming from LLM
    output_parser : StructuredOutputParser
        Langchain Structured output parser that helps to extract the text
    possible_inactive : dict
        Dictionary containing all the possible inactive ingredients and its aliases
    _logger : logging
        logger object (or None, in case no logging)

    Returns
    -------
    result : list
        All the inactive ingredients found in the text already filtering out printing inking
    product_route : str
        The Distribution Route found in the product
    product_df : str
        The Dosage Form found in the product
    found_ndc_info : str
        The NDC information, meaning the product distinguish features of the NDC (ex: 10mg, 20mg, 30mg)
    """

    txt = txt.replace('json', '').replace('```', '')
    try:
        response_treated = output_parser.parse(txt)
    except Exception as e:
        print(f"error with structured extraction:\n\toriginal output: {txt}\n\terror:'{e.__str__()}'")
        response_treated = {}

    _list_inactive = response_treated['FoundInactiveIngredients'] if 'FoundInactiveIngredients' in response_treated else []
    list_inactive = []
    for c in _list_inactive:
        if c.count(",") > 1:
            list_inactive += c.split(',')
        else:
            list_inactive.append(c)

    list_inactive = [c.lower() for c in list_inactive]

    list_inactive_printing_ink = response_treated['IngredientsPrintingInk'] if 'IngredientsPrintingInk' in response_treated else []
    list_inactive_printing_ink = [c.lower() for c in list_inactive_printing_ink]

    list_inactive_printing_outside = response_treated['IngredientsPrintingInkOutside'] if 'IngredientsPrintingInkOutside' in response_treated else []
    list_inactive_printing_outside = [c.lower() for c in list_inactive_printing_outside]

    product_route = response_treated['Product_route'] if 'Product_route' in response_treated else ''
    product_route = product_route.lower()

    product_df = response_treated['Product_dosage_form'] if 'Product_dosage_form' in response_treated else ''
    product_df = product_df.lower()

    found_mint = response_treated['Product_found_mint'] if 'Product_found_mint' in response_treated else ''
    found_mint = True if found_mint in ['1', 1, True] else False

    found_menthol = response_treated['Product_found_menthol'] if 'Product_found_menthol' in response_treated else ''
    found_menthol = True if found_menthol in ['1', 1, True] else False

    found_ndc_info = response_treated['Found NDC Specific Information'] if 'Found NDC Specific Information' in response_treated else ''
    found_ndc_info = True if found_ndc_info in ['1', 1, True] else False

    if found_mint:
        list_inactive += ['mint']

    if found_menthol:
        list_inactive += ['menthol']

    inactive_decomposed = {i: [sorted(decompose(a)) for a in al] for i, al in possible_inactive.items()}
    result = filter_valid_ingredients(list_inactive, list_inactive_printing_ink, list_inactive_printing_outside,
                                      inactive_decomposed, already_decomposed=True)

    if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'True':
        msg = f"DEBUG:\n\tfound_inactive: '" + "', '".join(list_inactive) + \
              "\n\tfound_print: '" + "', '".join(list_inactive_printing_ink) + \
              "\n\tfound_print_outside: '" + "', '".join(list_inactive_printing_outside) + "'" + \
              f"\n\tfound_mint: '{found_mint}'" + \
              f"\n\tfound_menthol: '{found_menthol}'"

        if _logger is not None:
            _logger.info(msg)
        else:
            print(msg)

    if _logger is not None:
        _logger.info(f'Before Filtering: ' + ", ".join(list_inactive))
        _logger.info(f'After Filtering: ' + ", ".join(result))

    return result, product_route, product_df, found_ndc_info


def process_output_group2_3(answer, name2id):
    """ Helper function to process output from LLM regarding Group 2 and 3

    Parameters
    ----------
    answer : dict
        Dictionary structure fed to the LLM containing For group 2: (name_ingredient): Include/Exclude
         For Group 3: (name_ingredient): (choice of ingredient)
    name2id : dict
        Dictionary with (name of ingredient) : (id of ingredient) structure

    Returns
    -------
    result_ids: list
        list of ingredient IDs found from Group 2 and Group 3
    """

    result_ids = []

    for name, value in answer.items():
        name = name.replace('_', ' ')
        if value == 'Include':
            if name.lower() in name2id:
                result_ids.append(name2id[name.lower()])
            continue
        elif value == 'Exclude':
            continue
        else:
            if value.lower() in name2id:
                result_ids.append(name2id[value.lower()])

    return result_ids


def process_output_group4_5(response, output_parser, name2id):
    """ Helper function to process output from LLM regarding Group 4 and 5

    Parameters
    ----------
    response : llama_index.indices.query
        Response object containing answer from LLM regarding Group 4 and 5
    output_parser : llama_index.output_parsers.LangchainOutputParser
        Output parser helper to extract structured information from response
    name2id : dict
        Dictionary with (name of ingredient) : (id of ingredient) structure

    Returns
    -------
    result_ids: list
        list of ingredient IDs found from Group 2 and Group 3
    """
    txt = response.response
    txt = txt.replace('json', '').replace('```', '')
    response_treated = output_parser.parse(txt)

    result_ids = [name2id[r.replace('Found ', '').lower()] for r, v in response_treated.items()
                  if v in [1, '1'] and r.replace('Found ', '').lower() in name2id.keys()]

    return result_ids


def extract_ingredients(_setid, _ndc, _ndcs, _ndc_setid, _inactive_ing, _inactive_groups, _inactive_ids, _doc_to_index,
                        _filter_groups, _logger=None, _true_ing=None):
    """ Main extract ingredients method to extract all the inactive ingredients from an SPL

    Parameters
    ----------
    _setid : str
        Hash key that represents an SPL
    _ndc : str
        NDC RAW text
    _ndcs : str
        list of all RAW _NDCs present in FDB for the specific SetID
    _ndc_setid : str
        Whether the extraction is occuring at SETID level or NDC (value: 'ndc' or 'setid')
    _inactive_ing : dict
        Dictionary containing all the available inactive ingredients and its aliases
    _inactive_groups : dict
        Dictionary containing all the available inactive ingredients and its corresponding group
    _inactive_ids : dict
        Dictionary containing all the available inactive ingredients and its corresponding ID
    _doc_to_index : Document with content
        Llama Document with content
    _filter_groups : list
        The groups that will be looked at
    _logger : logging
        logger object (or None, in case no logging)
    _true_ing : list
        IDs found in Todd's rules which correspond at the moment to the "true" labels

    Returns
    -------
    result_ids : list
        IDs of found ingredients through the LLM
    product_size_ndc : str
        The NDC information, meaning the product distinguish features of the NDC (ex: 10mg, 20mg, 30mg)
    """

    start = time.time()

    if _logger is not None:
        _logger.info(f'Extract ingredients: first doing Vector search then tagging with alias')

    try:
        # Group 1 query
        product_size_ndc = ""
        if _ndc_setid == 'setid':
            _index_g1 = index_data(_doc_to_index,
                                   deployment_env_key="DEPLOYMENT_GROUP1",
                                   model_env_key="MODEL_GROUP1")
            query_engine, output_parser = prepare_schema_index_query_g1_setid(_index_g1)
            query = os.environ["qa_prompt"]
        # if NDC then perform extra steps
        else:
            _index_g1 = index_data(_doc_to_index,
                                   deployment_env_key="DEPLOYMENT_GROUP1",
                                   model_env_key="MODEL_GROUP1", indexing_structure="list-index")
            
            query_engine, output_parser = prepare_schema_index_query_g1_ndc_pre(_index_g1, _ndcs)
            query = os.environ["group_1_ndc_pre"].format(ndcs = ", ".join(_ndcs))
            
            response = query_engine.query(query)
            # print(response) -----getting an error in retrieving the response
            answer = output_parser.parse(response.response)

            product_size_ndc = answer[f"NDC {_ndc} Information"]
            #print("product_size_ndc", product_size_ndc, end=": ")
            if product_size_ndc == 'Not Available':
                _index_g1 = index_data(_doc_to_index,
                                       deployment_env_key="DEPLOYMENT_GROUP1",
                                       model_env_key="MODEL_GROUP1")
                query_engine, output_parser = prepare_schema_index_query_g1_setid(_index_g1)
                query = os.environ["qa_prompt"]
            else:
                query = os.environ["group_1_ndc_pos"].replace("{selected_product}", product_size_ndc)
                _index_g1_pos = index_data(_doc_to_index,
                                           deployment_env_key="DEPLOYMENT_GROUP1-pos",
                                           model_env_key="MODEL_GROUP1-pos")
                query_engine, output_parser = prepare_schema_index_query_g1_ndc_pos(_index_g1_pos, product_size_ndc)

        response = query_engine.query(query)
        # print(response.response)
        found_ing, found_route, found_df, found_ndc_info = process_output_group1(response.response, output_parser, _inactive_ing)
        if "unknown" in response.response.lower() or (found_ing == [] and not found_ndc_info):
            query_engine, output_parser = prepare_schema_index_query_g1_setid(_index_g1)
            query = os.environ["qa_prompt"]
            response = query_engine.query(query)
            found_ing, found_route, found_df, found_ndc_info = process_output_group1(response.response, output_parser, _inactive_ing)

        # will start by saving the IDs of Group 1
        result_ids_g1 = [list(_inactive_ids[inactive])[0] for inactive in found_ing if _inactive_groups[inactive] == 1]

        # Configurations for Rules on Groups 2,3,4,5 (filtered by focused groups)
        df = pd.read_csv(RULES_CONFIG_FILE).fillna("")
        df.FDB_HICDDESC = df.FDB_HICDDESC.str.lower()
        df = df.loc[df.Group.isin(_filter_groups)]
        name2id = {k.lower(): v for k, v in df.set_index('Name').to_dict()['ReportedInactiveID'].items()}
        df_gp3 = df.loc[df.FDB_HICDDESC.isin(found_ing) & (df.Group == 3)]
        df_gp2 = df.loc[df.FDB_HICDDESC.isin(found_ing) & (df.Group == 2)]
        df_gp4 = df.loc[df.Group == 4]

        # Only run Group 2 and 3 Query if there were any ingredient found
        if (df_gp2.shape[0] + df_gp3.shape[0]) > 0:
            chain = prepare_schema_query_g2_3(df_gp2, df_gp3)
            answer = chain.run(route=found_route, dosage_form=found_df)
        else:
            answer = {}

        result_ids_g2_3 = process_output_group2_3(answer, name2id)

        # Group 4
        _index_g4 = index_data(_doc_to_index,
                               deployment_env_key="DEPLOYMENT_GROUP4-5",
                               model_env_key="MODEL_GROUP4-5")
        query_engine, output_parser = prepare_schema_query_g4(_index_g4, df_gp4)
        response = query_engine.query(os.environ["schema_group4_5_query"])
        result_ids_g4 = process_output_group4_5(response, output_parser, name2id)

        # Group 5
        whole_txt = "\n".join([_index_g4.docstore.docs[doc].dict()['text'] for doc in _index_g4.docstore.docs])
        result_ids_g5 = []
        if "latex" in whole_txt.lower():
            _index_g5 = index_data(_doc_to_index,
                                   deployment_env_key="DEPLOYMENT_GROUP4-5",
                                   model_env_key="MODEL_GROUP4-5")
            answer = prepare_schema_query_g5(_index_g5, "latex or any latex related substance", "Latex")
            if "Found Latex" in answer and answer["Found Latex"] in [1, '1']:
                result_ids_g5.append(name2id["latex"])
        elif "rubber" in whole_txt.lower():
            _index_g5 = index_data(_doc_to_index,
                                   deployment_env_key="DEPLOYMENT_GROUP4-5",
                                   model_env_key="MODEL_GROUP4-5")
            answer = prepare_schema_query_g5(_index_g5, "rubber or rubber stopper or any rubber related substance", "Rubber")
            if "Found Rubber" in answer and answer["Found Rubber"] in [1, '1']:
                result_ids_g5.append(name2id["rubber"])

        result_ids = result_ids_g1 + result_ids_g2_3 + result_ids_g4 + result_ids_g5

        # In case it finds any issue save to a logger file the text being used, to try to debug what's happening
        if _true_ing is not None and sorted(_true_ing) != sorted(result_ids):
            with open(f'data/parsed_texts/{_setid}_{os.environ["EXTRACT_METHOD"]}.txt', 'w+') as f:
                f.write(whole_txt)

        if _logger is not None:
            _logger.info(f"Took overall: {print_time(time.time() - start)}\n")

        return result_ids, product_size_ndc
    except Exception as e:
        if _logger is not None:
            _logger.error(f"Got an error extracting ingredients. Error: '{e.__str__()}'")
            _logger.info(f"Took overall: {print_time(time.time() - start)}\n")
        else:
            print(f"Got an error extracting ingredients. Error: '{e.__str__()}'\n")

        return None, None
