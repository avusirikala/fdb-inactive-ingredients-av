import os

set_1 = {
    "qa_prompt": "What are all inactive ingredients in the entire text?",
    "schema_main_list": "A list of ALL the inactive ingredients in the entire text "
                        "and different sections that are clearly identified as an inactive ingredient."
                        "If more than one section or paragraphs of inactive ingredients, gather all the inactive "
                        "ingredients in them. ",
    "schema_printing_list": "List of ingredients contained in the 'printing ink'. ",
    "schema_list_of_texts": "",
}

set_2 = {
    "qa_prompt": "What are all inactive ingredients in the entire text? And the Route of Administration and Dosage "
                 "Form of the Product?",
    "schema_main_list": "A list of ALL the inactive ingredients in the entire text "
                        "and different sections that are clearly identified as an inactive ingredient. "
                        "If more than one section or paragraphs of inactive ingredients, gather all the inactive "
                        "ingredients in them. "
                        "Don't include active ingredients only include inactive ingredients. "
                        "Make sure you only include ingredients which are clearly identified as inactive ingredients "
                        "in case of ambiguity, don't include them. "
                        "In case there's not a clear list of inactive ingredients, return empty list.",
    "schema_printing_list": "List of ingredients contained in the 'printing ink'. ",
    "schema_both_print_list": "List of ingredients which are both contained in the printing ink as mentioned in other "
                              "parts of the text.",
    "schema_list_of_texts": "",
    "schema_product_route": "What is the route of administration of the product? (examples of routes are: Auricular, "
                            "Cutaneous, Dental, subcutaneous)",
    "schema_product_df": "What is the dosage form of the product? (examples of dousage form are: Injection, Powder, "
                         "Solution, tablet)",
}

set_3 = {
    "qa_prompt": "What are all inactive ingredients in the entire text? And the Route of Administration and Dosage "
                 "Form of the Product? And if there is mint or menthol is present in the text.",
    "group_1_ndc_pre": "Knowing that we have NDCs {ndcs}. Match the product dosage and size to each NDC.",
    "group_1_ndc_pos": "List the inactive ingredients for the NDC {selected_product}, in case there isn't any "
                       "specific information on inactive ingredients for the NDC {selected_product}, find all the "
                       "inactive ingredients for the entire product. And the Route of Administration and Dosage"
                       "Form of the Product? And if there is mint or menthol is present in the text.",
    "schema_ndc_list": "A list of the inactive ingredients found in the NDC {selected_product} in case there is no "
                       "specific information related to the NDC {selected_product}, then list all the inactive "
                       "ingredients of the product.",
    "schema_main_list": "A list of ALL the inactive ingredients in the entire text "
                        "and different sections that are clearly identified as an inactive ingredient. "
                        "If more than one section or paragraphs of inactive ingredients, list all the inactive "
                        "ingredients in them. "
                        "Don't include active ingredients only include inactive ingredients. "
                        "Make sure you only include ingredients which are clearly identified as inactive ingredients "
                        "in case of ambiguity, don't include them. "
                        "After you find an instance of inactive ingredients, continue to search if there are more "
                        "instances in the text and capture all of the ingredients in them."
                        "In case there's not a clear list of inactive ingredients, return empty list.",
    "schema_printing_list": "List of ingredients contained in the 'printing ink'. ",
    "schema_both_print_list": "List of ingredients which are both contained in the 'printing ink' and contained or "
                              "used also in other parts of the product.",
    "schema_list_of_texts": "",
    "schema_product_route": "What is the route of administration of the product? (examples of routes are: Auricular, "
                            "Cutaneous, Dental, subcutaneous)",
    "schema_product_df": "What is the dosage form of the product? (examples of dousage form are: Injection, Powder, "
                         "Solution, tablet)",
    "schema_mint_found": "Does the product has Mint as a flavour? Return 1 if found or 0 if not found.",
    "schema_menthol_found": "Does the product has Menthol as a flavour? Return 1 if found or 0 if not found.",
    "schema_ndc_specific": "If found inactive ingredient related to the NDC {selected_product} return 1 else return 0.",
    "schema_group2_include": "If product meets the following criteria: '{include}' return 1 else return 0.",
    "schema_group2_exclude": "If product meets the following criteria: '{exclude}' return 1 else return 0.",
    "schema_group2_3_query": "You have a medical product with following route of administration: '{route}' and "
                             "following dosage form: '{dosage_form}', according to that choose the ingredients. ",
    "schema_group3_include": "Choose option {name} in case the product matches below requirement '{include}'; ",
    "schema_group4_5_query": "Please thoroughly review the medical label. Check all "
                             "sections, including descriptions, instructions, warnings, and any other text, "
                             "for mentions of specific substances. Ensure to look for both the substance being a part "
                             "of the drug formulation and any mention in any context such as in packaging components "
                             "or in the manufacturing process. Please provide a binary output, marking '1' if a "
                             "substance is mentioned in any context, or '0' if a substance is not mentioned at all.",
}

set_4 = {
    "qa_prompt": "What are all inactive ingredients in the entire text? And the Route of Administration and Dosage "
                 "Form of the Product? And if there is mint or menthol is present in the text.",
    "group_1_ndc_pre": "Knowing that we have NDCs {ndcs}. Match the product dosage, number of counts, size, package, any relevant NDC specific information to each NDC. "
                       "In case you don't find all the information per NDC, extract whatever is relevant for that NDC.  You may need to look into every section to find this information.",
    "group_1_ndc_pos": "List the inactive ingredients for the NDC {selected_product}, in case there isn't any "
                       "specific information on inactive ingredients for the NDC {selected_product}, find all the "
                       "inactive ingredients for the entire product. And the Route of Administration and Dosage"
                       "Form of the Product? And if there is mint or menthol is present in the text.",
    "schema_ndc_list": "A list of the inactive ingredients found in the NDC {selected_product} in case there is no "
                       "specific information related to the NDC {selected_product}, then list all the inactive "
                       "ingredients of the product.",
    "schema_main_list": "A list of ALL the inactive ingredients in the entire text "
                        "and different sections that are clearly identified as an inactive ingredient. "
                        "If more than one section or paragraphs of inactive ingredients, list all the inactive "
                        "ingredients in them. "
                        "Don't include active ingredients only include inactive ingredients. "
                        "Make sure you only include ingredients which are clearly identified as inactive ingredients "
                        "in case of ambiguity, don't include them. "
                        "After you find an instance of inactive ingredients, continue to search if there are more "
                        "instances in the text and capture all of the ingredients in them."
                        "In case there's not a clear list of inactive ingredients, return empty list.",
    "schema_printing_list": "List of ingredients contained in the 'printing ink'. ",
    "schema_both_print_list": "List of ingredients which are both contained in the 'printing ink' and contained or "
                              "used also in other parts of the product.",
    "schema_list_of_texts": "",
    "schema_product_route": "What is the route of administration of the product? (examples of routes are: Auricular, "
                            "Cutaneous, Dental, subcutaneous)",
    "schema_product_df": "What is the dosage form of the product? (examples of dousage form are: Injection, Powder, "
                         "Solution, tablet)",
    "schema_mint_found": "Does the product has Mint as a flavour? Return 1 if found or 0 if not found.",
    "schema_menthol_found": "Does the product has Menthol as a flavour? Return 1 if found or 0 if not found.",
    "schema_ndc_specific": "If found inactive ingredient related to the NDC {selected_product} return 1 else return 0.",
    "schema_group2_include": "If product meets the following criteria: '{include}' return 1 else return 0.",
    "schema_group2_exclude": "If product meets the following criteria: '{exclude}' return 1 else return 0.",
    "schema_group2_3_query": "You have a medical product with following route of administration: '{route}' and "
                             "following dosage form: '{dosage_form}', according to that choose the ingredients. ",
    "schema_group3_include": "Choose option {name} in case the product matches below requirement '{include}'; ",
    "schema_group4_5_query": "Please thoroughly review the medical label. Check all "
                             "sections, including descriptions, instructions, warnings, and any other text, "
                             "for mentions of specific substances. Ensure to look for both the substance being a part "
                             "of the drug formulation and any mention in any context such as in packaging components "
                             "or in the manufacturing process. Please provide a binary output, marking '1' if a "
                             "substance is mentioned in any context, or '0' if a substance is not mentioned at all.",
}

if os.environ["PROMPT_SET"] == "set1":
    for k in set_1.keys():
        os.environ[k] = set_1[k]
elif os.environ["PROMPT_SET"] == "set2":
    for k in set_2.keys():
        os.environ[k] = set_2[k]
elif os.environ["PROMPT_SET"] == "set3":
    for k in set_3.keys():
        os.environ[k] = set_3[k]
elif os.environ["PROMPT_SET"] == "set4":
    for k in set_4.keys():
        os.environ[k] = set_4[k]
