import os
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from llama_index import QuestionAnswerPrompt, RefinePrompt
from llama_index.output_parsers import LangchainOutputParser
from llama_index.prompts.default_prompts import DEFAULT_TEXT_QA_PROMPT_TMPL, DEFAULT_REFINE_PROMPT_TMPL
from langchain.output_parsers import ResponseSchema, StructuredOutputParser


def prepare_schema_index_query_g1_setid(_index):
    """ Schema for extracting required information for Group 1

    Parameters
    ----------
    _index : llama_index.schema.indices
        document index which will be used to generate query engine

    Returns
    -------
    query_engine : QueryEngine
        query engine from the index
    output_parser : StructuredOutputParser
        parser which helps to extract the information in a structured way
    """

    found_inactive = ResponseSchema(name="FoundInactiveIngredients", type="array",
                                    description=os.environ["schema_main_list"])

    found_printing = ResponseSchema(name="IngredientsPrintingInk", type="array",
                                    description=os.environ["schema_printing_list"])

    found_both_print_outside = ResponseSchema(name="IngredientsPrintingInkOutside", type="array",
                                              description=os.environ["schema_both_print_list"])

    product_route = ResponseSchema(name="Product_route", type="string",
                                   description=os.environ["schema_product_route"])

    product_df = ResponseSchema(name="Product_dosage_form", type="string",
                                description=os.environ["schema_product_df"])

    mint_found = ResponseSchema(name="Product_found_mint", type="integer",
                                description=os.environ["schema_mint_found"])

    menthol_found = ResponseSchema(name="Product_found_menthol", type="integer",
                                   description=os.environ["schema_menthol_found"])

    response_schemas = [product_route, product_df, mint_found, found_inactive, found_printing, found_both_print_outside,
                        menthol_found]

    lc_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    output_parser = LangchainOutputParser(lc_output_parser)

    # format each prompt with output parser instructions
    fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
    fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)
    qa_prompt = QuestionAnswerPrompt(fmt_qa_tmpl, output_parser=output_parser)
    refine_prompt = RefinePrompt(fmt_refine_tmpl, output_parser=output_parser)

    query_engine = _index.as_query_engine(text_qa_template=qa_prompt, refine_template=refine_prompt)

    return query_engine, output_parser


def prepare_schema_index_query_g1_ndc_pre(_index, _ndcs):
    """ Schema for extracting required information for Group 1

    Parameters
    ----------
    _index : llama_index.schema.indices
        document index which will be used to generate query engine
    _ndcs : list
        list of all RAW _NDCs present in FDB for the specific SetID

    Returns
    -------
    query_engine : QueryEngine
        query engine from the index
    output_parser : StructuredOutputParser
        parser which helps to extract the information in a structured way

    """

    response_schemas = [ResponseSchema(name=f"NDC {ndc} Information", type="string",
                                       description=f"The product dosage and size for NDC {ndc}. In case you don't find any relevant information return 'Not Available'")
                        for ndc in _ndcs]

    lc_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    output_parser = LangchainOutputParser(lc_output_parser)

    # format each prompt with output parser instructions
    fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
    fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)
    qa_prompt = QuestionAnswerPrompt(fmt_qa_tmpl, output_parser=output_parser)
    refine_prompt = RefinePrompt(fmt_refine_tmpl, output_parser=output_parser)

    query_engine = _index.as_query_engine(text_qa_template=qa_prompt, refine_template=refine_prompt)

    return query_engine, output_parser


def prepare_schema_index_query_g1_ndc_pos(_index, selected_product):
    """ Schema for extracting required information for Group 1

    Parameters
    ----------
    _index : llama_index.schema.indices
        document index which will be used to generate query engine
    selected_product : str
        description obtained from the 1st step of the LLM containing the description of the size of the NDC

    Returns
    -------
    query_engine : QueryEngine
        query engine from the index
    output_parser : StructuredOutputParser
        parser which helps to extract the information in a structured way
    """

    found_inactive = ResponseSchema(name="FoundInactiveIngredients", type="array",
                                    description=os.environ["schema_ndc_list"].replace("{selected_product}", selected_product))

    found_printing = ResponseSchema(name="IngredientsPrintingInk", type="array",
                                    description=os.environ["schema_printing_list"])

    found_both_print_outside = ResponseSchema(name="IngredientsPrintingInkOutside", type="array",
                                              description=os.environ["schema_both_print_list"])

    product_route = ResponseSchema(name="Product_route", type="string",
                                   description=os.environ["schema_product_route"])

    product_df = ResponseSchema(name="Product_dosage_form", type="string",
                                description=os.environ["schema_product_df"])

    mint_found = ResponseSchema(name="Product_found_mint", type="integer",
                                description=os.environ["schema_mint_found"])

    menthol_found = ResponseSchema(name="Product_found_menthol", type="integer",
                                   description=os.environ["schema_menthol_found"])

    ndc_specific_info = ResponseSchema(name="Found NDC Specific Information", type="integer",
                                       description=os.environ["schema_ndc_specific"].replace("{selected_product}", selected_product))

    response_schemas = [product_route, product_df, mint_found, found_inactive, found_printing, found_both_print_outside,
                        menthol_found, ndc_specific_info]

    lc_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    output_parser = LangchainOutputParser(lc_output_parser)

    # format each prompt with output parser instructions
    fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
    fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)
    qa_prompt = QuestionAnswerPrompt(fmt_qa_tmpl, output_parser=output_parser)
    refine_prompt = RefinePrompt(fmt_refine_tmpl, output_parser=output_parser)

    query_engine = _index.as_query_engine(text_qa_template=qa_prompt, refine_template=refine_prompt)

    return query_engine, output_parser


def prepare_schema_query_g2_3(df_gp2, df_gp3):
    """Schema for extracting required information for Group 2 and 3

    Parameters
    ----------
    df_gp2 : pandas.DataFrame
        information of the ingredients and its rules for Group 2
    df_gp3 : pandas.DataFrame
        information of the ingredients and its rules for Group 3

    Returns
    -------
    LangChain.create_structured_output_chain
        chain prepared to execute LLM question
    """
    json_schema = {
        "title": "Extract Inactive Ingredients",
        "description": "Extract Inactive Ingredients Medical Product",
        "type": "object",
        "properties": {},
        "required": []
    }

    for name, include, exclude in df_gp2.loc[df_gp2.Include != '', ['Name', 'Include', 'Exclude']].values.tolist():
        if exclude != '' and include != '':
            description = f"Choose 'Include' if product meets the criteria: '{include}', or 'Exclude' if product meets criteria '{exclude}'."
        elif exclude == '':
            description = f"Choose 'Include' if product meets the criteria: '{include}', or 'Exclude' otherwise."
        elif include == '':
            description = f"Choose 'Exclude' if product meets the criteria: '{exclude}', or 'Include' otherwise."
        else:
            print('DEBUG: shouldnt have got here include-exclude group 2')
            description = ""

        json_schema["properties"][name] = {
            "title": name, "type": "string", "enum": ['Include', 'Exclude'], "description": description
        }
        json_schema["required"] += [name]

    for name, options, includes in df_gp3.groupby('FDB_HICDDESC').agg(
            {'Name': list, 'Include': list}).reset_index().values.tolist():
        description = "Choose between " + " or ".join(
            [f" '{n}' if it matches '{i}' " for n, i in zip(options, includes)])
        json_schema["properties"][name] = {
            "title": name, "type": "string", "enum": options, "description": description
        }
        json_schema["required"] += [name]

    model = os.environ["MODEL_GROUP2-3"]
    llm = AzureChatOpenAI(model=model,
                          deployment_name=os.environ.get("DEPLOYMENT_GROUP2-3", model),
                          temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "You are an expert related to medical information and the differences between systemic and non systemic formulations."),
            ("human", "You are expected to choose the right option based on the information provided related to a medical Product."),
            ("human", os.environ["schema_group2_3_query"]),
            ("human", "Tip: Make sure to answer in the correct format"),
        ]
    )

    chain = create_structured_output_chain(json_schema, llm, prompt, verbose=False)

    return chain


def prepare_schema_query_g4(_index, df):
    """ Schema for extracting required information for Group 4 and 5

    Parameters
    ----------
    _index : llama_index.schema.indices
        document index which will be used to generate query engine
    df : pandas.DataFrame
        information of the ingredients and its rules for Group 4 and 5

    Returns
    -------
    query_engine : QueryEngine
        query engine from the index
    output_parser : StructuredOutputParser
        parser which helps to extract the information in a structured way
    """
    response_schemas = []
    for name, include, exclude in df.loc[df.Include != '', ['Name', 'Include', 'Exclude']].values.tolist():
        if exclude != '' and include != '':
            description = f"Return '1'  if product meets the criteria: '{include}', or '0'' if product meets criteria '{exclude}'."
        elif exclude == '':
            description = f"Return '1' if product meets the criteria: '{include}', or '0' otherwise."
        elif include == '':
            description = f"Choose '0' if product meets the criteria: '{exclude}', or '1' otherwise."
        else:
            print('DEBUG: shouldnt have got here include-exclude group 4-5')
            description = ""

        rule = ResponseSchema(name=f"Found {name}", type="integer", description=description)

        response_schemas.append(rule)

    lc_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    output_parser = LangchainOutputParser(lc_output_parser)

    # format each prompt with output parser instructions
    fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
    fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)
    qa_prompt = QuestionAnswerPrompt(fmt_qa_tmpl, output_parser=output_parser)
    refine_prompt = RefinePrompt(fmt_refine_tmpl, output_parser=output_parser)

    query_engine = _index.as_query_engine(text_qa_template=qa_prompt, refine_template=refine_prompt)

    return query_engine, output_parser


#
def prepare_schema_query_g5(_index, ingredient, ingredient_name):
    """

    Parameters
    ----------
    _index : llama_index.schema.indices
        document index which will be used to generate query engine
    ingredient : str
        Complete description of the element to search for within the text, for example (latex or any latex related substance)
    ingredient_name : str
        Name of the ingredient to check if found or not (example 'Latex', or 'Rubber')

    Returns
    -------
    answer : dict
        Answer from the LLM whether it found the ingredient or not '1' for found '0' for not

    """
    desc = f"Return 1 if found mention to {ingredient}, related with substance or being a part " \
           "of the drug formulation and any mention in any context such as in packaging components " \
           "or in the manufacturing process. Otherwise return 0"
    rule = ResponseSchema(name=f"Found {ingredient_name}", type="integer", description=desc)
    lc_output_parser = StructuredOutputParser.from_response_schemas([rule])
    output_parser = LangchainOutputParser(lc_output_parser)

    # format each prompt with output parser instructions
    fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
    fmt_refine_tmpl = output_parser.format(DEFAULT_REFINE_PROMPT_TMPL)
    qa_prompt = QuestionAnswerPrompt(fmt_qa_tmpl, output_parser=output_parser)
    refine_prompt = RefinePrompt(fmt_refine_tmpl, output_parser=output_parser)

    query_engine = _index.as_query_engine(text_qa_template=qa_prompt, refine_template=refine_prompt)
    query = "Please thoroughly review the medical label. Check all " \
            "sections, including descriptions, instructions, warnings, and any other text, " \
            "for mentions of specific substances. Ensure to look for both the substance being a part " \
            "of the drug formulation and any mention in any context such as in packaging components " \
            "or in the manufacturing process. Please provide a binary output, marking '1' if a " \
            "substance is mentioned in any context, or '0' if a substance is not mentioned at all."
    response = query_engine.query(query)
    answer = output_parser.parse(response.response)

    return answer
