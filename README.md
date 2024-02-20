# FDB.USA Inactive Ingredients

## Solution Architecture

![architecture.jpg](img%2Farchitecture.jpg)

## Current Status

### NDC Searches
- Group 1 tested 317; accuracy: 92.74% [with 23 errors and 255/264  (96.59%) True Positive Rate; 14/67 (20.9%) False Positive Rate]
- Group 2 tested 317; accuracy: 96.53% [with 11 errors and 43/45  (95.56%) True Positive Rate; 9/281 (3.2%) False Positive Rate]
- Group 3 tested 317; accuracy: 98.11% [with 6 errors and 9/14  (64.29%) True Positive Rate; 6/309 (1.94%) False Positive Rate]
- Group 4 tested 317; accuracy: 99.37% [with 2 errors and 22/22  (100%) True Positive Rate; 2/297 (0.67%) False Positive Rate]
- Group 5 tested 317; accuracy: 94.01% [with 19 errors and 13/18  (72.22%) True Positive Rate; 17/316 (5.38%) False Positive Rate]

### SetID Searches
- Group 1 tested 303; accuracy: 96.04% [with 12 errors and 234/242  (96.69%) True Positive Rate; 6/67 (8.96%) False Positive Rate]
- Group 2 tested 303; accuracy: 96.7% [with 10 errors and 62/70  (88.57%) True Positive Rate; 2/235 (0.85%) False Positive Rate]
- Group 3 tested 303; accuracy: 97.69% [with 7 errors and 12/16  (75%) True Positive Rate; 4/291 (1.37%) False Positive Rate]
- Group 4 tested 303; accuracy: 100% [with 0 errors and 28/28  (100%) True Positive Rate; 0/275 (0%) False Positive Rate]
- Group 5 tested 303; accuracy: 97.36% [with 8 errors and 11/13  (84.62%) True Positive Rate; 6/296 (2.03%) False Positive Rate]

### Current Problems

#### NDC Issues

- `14/49` errors No information on NDC product size
- `12/49` errors Latex/Rubber contained in some NDCs but not in others
- `10/49` errors Latex/Rubber mentions it doesn't contain
- `6/49` errors Ambiguous information on the ingredients and product information for the NDC
- `4/49` errors Special Cases (ex: extracted too much information for the product description, inconsistent results, sometimes it works others it doesn’t, peanut shape)
- `3/49` errors Clarity from clinical team

## Project Structure

### Folders

```
├── config            # folder with config environment files (.env) 
├── data              # data folder with DailyMed files with Todd Ingredient's / NDC / SetID / Aliases / Rules  
│   └── parsed_texts  # text of labels which aren't matched LLm vs Todd Ingredients, in order to debug  
├── helpers           # Python Helper Functions 
└── logs              # Log Files of the runs
```

### Helper Python Files

```
├── helpers
│   ├── config.py                     # config helper which loads environmental variables, sets some global variables and OPENAI needed environment
│   ├── extraction.py                 # LLM extraction part of the solution 
│   ├── get_spl_data.py               # extraction of SPL / NDC data from Daily Med
│   ├── inactive_ingredients_data.py  # Todd Ingredients and Aliases data mapping
│   ├── prompt.py                     # selection of prompts version. versioning helps to easily switch between different versions of prompts  
│   ├── schemas.py                    # extraction schemas to be used by Llama Index and LangChain 
│   └── util.py                       # General util functions like time printing, logging functions, ...
└── main.py                           # Starter Script 
```

### Data Files

```
└── data
    ├── LLM01_NDCSPL.txt           # NDC to SPL (setID) conversion
    ├── LLM02_NDCRI.txt            # NDC to Reported Inactive ingredients (the Inactive Ingredients inside an NDC)
    ├── LLM03_RI.txt               # Inactive ingredients information (groups, name, ids, ...)
    ├── LLM04_RI_ALIAS.txt         # Aliases of Inactive Ingredients
    └── LLM05_GROUP_2-5_RULES.csv  # Rules of Inclusion or Exclusion of ingredient
```

## Installation

```console
git clone https://github.com/octo-source/fdb-inactive-ingredients.git
cd fdb-inactive-ingredients
conda create -n Hearst python=3.10
conda activate Hearst
pip install -r requirements.txt 
```

## Usage

### Environmental Variables
> _OPENAI_API_KEY_: Open AI Key <br>
> _AZURE_API_: Azure API string (if empty, then not using) <br>
> _OPENAI_USE_EMBEDDINGS_: Whether to use Embeddings or not<br>
> _OPENAI_EMBEDDINGS_DEPLOYMENT_: The Embeddings deployment (Azure only). If unset will default to _OPENAI_EMBEDDINGS_MODEL_ value.<br>
> _OPENAI_EMBEDDINGS_MODEL_: The Embeddings model <br>
> _OPENAI_API_BASE_: API Base used for Azure<br>
> _OPENAI_API_VERSION_: OPENAI API version <br>
> _DEPLOYMENT_GROUP1_: Deployment to use for Group 1 pass (Azure only).  If unset will default to _MODEL_GROUP1_ value.<br>
> _MODEL_GROUP1_: OPENAI Model Name for Group 1 pass<br>
> _DEPLOYMENT_GROUP1-pre_: Deployment to use for Group 1 pre pass (Azure only).  If unset will default to _MODEL_GROUP1_ value.<br>
> _MODEL_GROUP1-pre_: OPENAI Model Name for Group 1 pre pass<br>
> _DEPLOYMENT_GROUP1-pos_: Deployment to use for Group 1 pos pass (Azure only)<br>
> _MODEL_GROUP1-pos_: OPENAI Model Name for Group 1 post pass<br>
> _DEPLOYMENT_GROUP2-3_: Deployment to use for Group 2 and 3 pass (Azure only)<br>
> _MODEL_GROUP2-3_: OPENAI Model Name for Group 2 and 3 pass<br>
> _DEPLOYMENT_GROUP4-5_: Deployment to use for Group 4 and 5 pass (Azure only)<br>
> _MODEL_GROUP4-5_: OPENAI Model Name for Group 4 and 5 pass<br>
> _EXTRACT_METHOD_: Extraction method (pdf, xml, both)<br>
> _XML_EXTRACTION_: XML type of extraction (1-Unstructured, 2-XHTML, 3-HTM5)<br>
> _NDC_SETID_: 'NDC' or 'SETID' to define which is the search method<br>
> _INDEXING_METHOD_: The indexing type of data ('vector-store', 'list-index', 'vector-store', 'keyword-table', 'knowledge-graph') <br>
> _TYPE_OF_OUTPUT_: Either 'simple' which outputs only SETID/NDC: response, or 'complex' which debugs more things<br>
> _LOG_DIR_: Folder path of Logs<br>
> _PROMPT_SET_: Name of the prompt sets for example set1, set2 <br>
> _DEBUG_: False or True, to display debugging information<br>
> _SELECTED_GROUPS_: Groups separated with comma to consider (example: '1,2,3')<br>
> _SELECTED_ALIAS_TYPE_: Alias types separated with comma, which should be taken into account ('PT,SYN,NEW')<br>



### Start

Change `list_searches` in [main.py](main.py) to include the SetIDs or NDCs.
Example: 
- `['0591-0860-01', '0591-0860-05', '0591-0861-01', '0591-0861-05', '0591-0862-01', '0591-0862-05']`
- `['ead1fca3-eff4-478f-8a8f-67510f80151a', 'bbc5b820-4973-11e2-a192-0002a5d5c51b', 'f2ec923a-2b88-43c0-ac2a-7ae20c053039', '189c13db-b4b7-4534-ae3c-1c52bb879e2b', '0f60b857-7898-4a9e-935c-a9ddf0eb9194']`

## Remaining Engineering Items for future
- Understanding cases where ingredients are not being mapped to NDCs correctly and updating prompts to resolve
- Extracting ingredient amounts to support thresholds 
- Minor prompt tuning for a few edge cases
