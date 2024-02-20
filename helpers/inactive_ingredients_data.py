import pandas as pd

DEFAULT_INACTIVE_CSV, DEFAULT_ALIAS_CSV = "data/LLM03_RI.txt", "data/LLM04_RI_ALIAS.txt"
DEFAULT_DESC_FIELD = 'FDB_HICDDESC'


def get_data(root=""):
    """ Get the data from the SPL which is in the provided CSV files:
    ( LLM01_NDCSPL.txt | LLM02_NDCRI.txt | LLM03_RI.txt | LLM04_RI_ALIAS.txt)
    And return the data into DataFrame format
    In the code also find description of what each CSV stands for

    Parameters
    ----------
    root : str
        Root path for where CSV files are located

    Returns
    -------
    ndc2spl : pandas.DataFrame
        Information regarding NDC to SPL
    ndc2ri : pandas.DataFrame
        Information regarding NDC to Reported Inactive Ingredient
    ri : pandas.DataFrame
        Information regarding the available Reported Ingredients
    ri2alias : pandas.DataFrame
        Aliases of Inactive Ingredients
    """

    import pandas as pd

    # Original description:
    #   CSV file that maps an NDC to the SPL used. NDC is represented as both NDC11 and RawNDC.
    #   (NDC11, RawNDC, ProprietaryName, DocID, SetID, FileRevisionNumber, S3Key)
    # Joao description:
    #   CSV containing info on products (product codes and version of label, path to XML)
    ndc2spl = pd.read_csv(root + 'LLM01_NDCSPL.txt')

    # Original description:
    #   CSV file listing ingredients for all supported NDCs as of 7/14/2023. Ingredient is represented by HICSEQNO and
    #   ReportedInactiveID. NOTE: No HICSEQNO will be provided and the RI ID will be 0 when no DAM or DDIM warnings
    #   are desired. (i.e. The product does not contain any clinically significant inactive ingredients.)
    #   (NDC11, HICSEQNO, ReportedInactiveID, Note)
    # Joao description:
    #   The Inactive Ingredients contained in each Product
    ndc2ri = pd.read_csv(root + 'LLM02_NDCRI.txt')

    # Original description:
    #   CSV file of the 83 "reported inactives" and their IDs and definitions. Includes frequency of use and "complexity
    #   group". (ReportedInactiveID, ReportedInactiveDescription, FDB_HICSEQNO, FDB_HICDDESC, Frequency, GroupNumber,
    #   GroupDescription, Discussion)
    # Joao description:
    #   Information on Inactive ingredients (it's description grouping, ...)
    ri = pd.read_csv(root + 'LLM03_RI.txt')

    # Original Description:
    #   CSV file listing the aliases (synonyms) of each of the ingredients. (ReportedInactiveID, Alias, AliasType)
    #
    ri2alias = pd.read_csv(root + 'LLM04_RI_ALIAS.txt')

    return ndc2spl, ndc2ri, ri, ri2alias


def get_todd_ingredients(_search, _ndc_setid, ndc11, filter_group=None):
    """ Funtion to get what is currently seen as the "true" labels meaning the ingredients found by Todd's Rules

    Parameters
    ----------
    _search : List[str]
        internal id of drug to extract XML
    _ndc_setid : str
        Whether the extraction is occuring at SETID level or NDC (value: 'ndc' or 'setid')
    ndc11 : str
        NDC value to search for
    filter_group : list
        filtered groups that should be taken into account

    Returns
    -------
    true : list
        IDs found in Todd's rules which correspond at the moment to the "true" labels
    """

    _ndc2spl, _ndc2ri, _ri, _ = get_data(root="data/")

    if filter_group is not None:
        valid_inactive_ids = _ri.loc[_ri.GroupNumber.isin(filter_group), 'ReportedInactiveID'].values.tolist()
    else:
        valid_inactive_ids = _ri.ReportedInactiveID.values.tolist()

    if _ndc_setid == 'setid':
        ndc_list = _ndc2spl.loc[_ndc2spl.SetID == _search, 'NDC11'].values.tolist()
    else:
        ndc_list = [ndc11]

    rep_inactive_id = _ndc2ri.loc[(_ndc2ri.NDC11.isin(ndc_list)) &
                                  (_ndc2ri.ReportedInactiveID.isin(valid_inactive_ids)), 'ReportedInactiveID'].unique().tolist()

    return rep_inactive_id


def possible_inactive_ingredients(filename_inactive=DEFAULT_INACTIVE_CSV, filename_alias=DEFAULT_ALIAS_CSV,
                                  description_field=DEFAULT_DESC_FIELD, filter_group=[], filter_alias=None,
                                  logger=None):
    """ Retrieve a list of all inactive Ingredients and its alias

    Parameters
    ----------
    filename_inactive : str
        file containing inactive ingredients
    filename_alias : str
        file containing alias from inactive ingredients
    description_field : str
        which field of the CSV to take the description from
    filter_group : list
        group of inactive ingredients to filter the list from. -1 if no filter
    filter_alias : list
        filter criteria for the type of alias to keep as list. Options: ['SYN', 'PT', 'UNII']
    logger : logging
        logger file or type logging for debug | error | warning | info

    Returns
    -------
    content_dict : dict
        dictionary containing (inactive ingredient):(inactive ingredient aliases)
    inact_group : dict
        dictionary containing (inactive ingredient):(group)
    inact_id : dict
        dictionary containing (inactive ingredient):(inactive ingredient id)
    id_inact : dict
        dictionary containing (inactive ingredient id):(inactive ingredient)
    """

    import pandas as pd

    if logger:
        logger.info(f"Starting to load inactive ingredients.")

    try:
        inactive = pd.read_csv(filename_inactive)
        alias = pd.read_csv(filename_alias)

        if filter_group:
            inactive = inactive.loc[inactive.GroupNumber.isin(filter_group)]

        if filter_alias is not None:
            alias = alias.loc[alias.AliasType.isin(filter_alias)]

        df = alias.merge(inactive, how="right")
        df.fillna('', inplace=True)
        df.rename(columns={description_field: 'Inactive'}, inplace=True)
        df['Inactive'] = df['Inactive'].apply(str.lower)
        df['Alias'] = df['Alias'].apply(str.lower)
        df = df.drop_duplicates(subset=['Alias', 'Inactive', 'ReportedInactiveID'])

        df = df.groupby('Inactive').agg({'Alias': list, 'GroupNumber': 'first', 'ReportedInactiveID': set}).reset_index()
        df.ReportedInactiveID = df.ReportedInactiveID.apply(lambda x: list(x))
        df['Alias'] = df.apply(lambda x: x['Alias'] + ([] if x['Inactive'] in x['Alias'] else [x['Inactive']]), axis=1)
        df['Alias'] = df['Alias'].apply(lambda x: [a for a in x if a != ''])

        content_dict = df.set_index('Inactive').to_dict()['Alias']
        inact_group = df.set_index('Inactive').to_dict()['GroupNumber']
        inact_id = df.set_index('Inactive').to_dict()['ReportedInactiveID']
        id_inact = {k: ina for ids, ina in zip(df.ReportedInactiveID.values, df.Inactive.values) for k in ids}

        if logger:
            logger.info(f"Loaded inactive ingredients.\n")

        return content_dict, inact_group, inact_id, id_inact
    except Exception as e:
        if logger:
            logger.error(f"error: Retrieving inactive ingredients filenames: {(filename_inactive, filename_alias)}. "
                         f"Error: '{e.__str__()}'\n")
        else:
            print(f"error: Retrieving inactive ingredients filenames: {(filename_inactive, filename_alias)}. "
                  f"Error: '{e.__str__()}'\n")
        return None, None, None, None


def get_set_id_from_ndc(ndc):
    """ Get the set ID of the product from a RAW NDC

    Parameters
    ----------
    ndc : str
        NDC Raw value to look for the SETID

    Returns
    -------
    setid : str
        Set ID belonging to the NDC
    ndcs : str
        list of all RAW _NDCs present in FDB for the specific SetID
    ndc11 : str
        NDC value to search for

    """
    _ndc2spl = pd.read_csv('data/LLM01_NDCSPL.txt')
    setid = _ndc2spl.loc[_ndc2spl.RawNDC == ndc, 'SetID'].iloc[0]
    ndc11 = _ndc2spl.loc[_ndc2spl.RawNDC == ndc, 'NDC11'].iloc[0]
    ndcs = _ndc2spl.loc[_ndc2spl.SetID == setid, 'RawNDC'].tolist()

    return setid, ndcs, ndc11
