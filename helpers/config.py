from dotenv import load_dotenv
import openai
import os

# load environment variables configuration which will be used through application
load_dotenv("config/azure_canada_example.env")

if 'AZURE_API' in os.environ and os.environ['AZURE_API'] != '':
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_type = "azure"
    openai.api_base = os.getenv("OPENAI_API_BASE")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")
    os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
else:
    openai.api_key = os.getenv("OPENAI_API_KEY")

TYPE_OF_OUTPUT = 'normal' if 'TYPE_OF_OUTPUT' not in os.environ or os.environ['TYPE_OF_OUTPUT'] != 'simple' else 'simple'
SELECTED_GROUPS = list(map(int, os.environ['SELECTED_GROUPS'].split(",")))
SELECTED_ALIAS_TYPE = [a.strip() for a in os.environ['SELECTED_ALIAS_TYPE'].split(",")]
NDC_SETID = "ndc" if 'NDC_SETID' not in os.environ or os.environ['NDC_SETID'] != 'setid' else 'setid'
