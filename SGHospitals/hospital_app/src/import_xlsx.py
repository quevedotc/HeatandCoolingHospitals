import pandas as pd
from pandas.api.types import is_numeric_dtype

def get_info_xls(xlsx_file):
    import pandas as pd

    planilha = pd.read_excel(xlsx_file, sheet_name='Dados da UH', index_col=None,
    header=None)

    nome_uh = planilha[2][0]
    code = planilha[4][5]
    num_app = planilha[2][5]

    CEES = {
        'nome APP': [],
        'CEE aquecimento': [],
        'CEE resfriamento': []
    }

    tipologia = planilha [2][1]
    cond_solo = []
    cond_cob = []

    area_condicionada = 0
    i = 0
    while i < num_app:

        amb = planilha[i + 2][8]
        nome_app = f'{amb} {planilha[i + 2][6]}'
        csolo = planilha[i + 2][11]
        cond_solo.append(csolo)
        ccob = planilha[i+2][12]
        cond_cob.append(ccob)

        cee_resf = planilha[i+2][9]
        cee_aquec = planilha[i+2][10]
        CEES['CEE aquecimento'].append(cee_aquec)
        CEES['CEE resfriamento'].append(cee_resf)
        CEES['nome APP'].append(f'{nome_app}')
        area_condicionada += planilha[i + 2][13]

        i += 1



    # caso haja APPs em condicoes de exposicao diferentes (UHs de 2 andares), retorna a pior condição
    if len(set(cond_solo)) == 1:
        condicao_solo = cond_solo[0]
    else:
        condicao_solo = 'Entre pavimentos'

    if len(set(cond_cob)) == 1:
        condicao_cob = cond_cob[0]
    else:
        condicao_cob = 'Exposto ao sol e ao vento'

    climas = pd.read_csv('db/baseweb_inmet.csv')
    epw = planilha[2][2]
    zb = climas.loc[climas.cidade == epw]['zona_bioclimatica'].tolist()[0]


    return (nome_uh, code, CEES, condicao_solo, condicao_cob, zb, tipologia, area_condicionada)


def metamodelo(xlsx_file):

    import pandas as pd
    from pandas.api.types import is_numeric_dtype

    climas = pd.read_csv('db/baseweb_inmet.csv')
    planilha = pd.read_excel(xlsx_file, sheet_name='Dados da UH', index_col=None,
    header=None)

    epw = planilha[2][2]
    area_apt = planilha[2][3]
    num_app = planilha[2][5]

    i = 0
    data = {
        "APP_CeilingHeight": [],
        "BLDG_TotalBuildingAreaNaoCondicionada": [],
        "SAMPLE_wall_abs": [],
        "SAMPLE_roof_abs": [],
        "SAMPLE_shgc": [],
        "SAMPLE_uVidro": [],
        "SAMPLE_openFactor": [],
        "CONST_cob_CT": [],
        "CONST_par_ext_CT": [],
        "CONST_laje_CT": [],
        "SAMPLE_blind": [],
        "APP_FloorArea": [],
        "ANG_N_anghd": [],
        "ANG_S_anghd": [],
        "ANG_L_anghd": [],
        "ANG_O_anghd": [],
        "ANG_N_anghe": [],
        "ANG_S_anghe": [],
        'ANG_L_anghe': [],
        'ANG_O_anghe': [],
        'ANG_N_ange': [],
        'ANG_S_ange': [],
        'ANG_L_ange': [],
        'ANG_O_ange': [],
        'ANG_N_angv': [],
        'ANG_S_angv': [],
        'ANG_L_angv': [],
        'ANG_O_angv': [],
        'APP_N_Window_SUP_AreaGross': [],
        'APP_S_Window_SUP_AreaGross': [],
        'APP_E_Window_SUP_AreaGross': [],
        'APP_W_Window_SUP_AreaGross': [],
        'APP_N_Door_isIn': [],
        'APP_S_Door_isIn': [],
        'APP_E_Door_isIn': [],
        'APP_W_Door_isIn': [],
        'MAR_azi_resto': [],
        'MAR_wall_area_apt': [],
        'MAR_wall_area_dorm': [],
        'MAR_wall_area_sala': [],
        'APP_N_ParExt_SUP_AreaGross': [],
        'APP_S_ParExt_SUP_AreaGross': [],
        'APP_E_ParExt_SUP_AreaGross': [],
        'APP_W_ParExt_SUP_AreaGross': [],
        'APP_N_ParInt_SUP_AreaGross': [],
        'APP_S_ParInt_SUP_AreaGross': [],
        'APP_E_ParInt_SUP_AreaGross': [],
        'APP_W_ParInt_SUP_AreaGross': [],
        'APP_ExteriorWindowArea': [],
        'CARAC_ambiente': [],
        'CARAC_condicoes': [],
        'CONST_ThermalConductance_COB': [],
        'CONST_ThermalConductance_PAR_EXT': [],
        'CONST_ThermalConductance_PISO_TERREO': [],
        'CLIMA_TOMax': [],
        'CLIMA_TBSm':[]

    }
    nome = {
        'APP':[]
    }


    while i < num_app:

        data['BLDG_TotalBuildingAreaNaoCondicionada'].append(area_apt)
        amb = planilha[i + 2][8]
        uso_amb = 0 if amb == 'Sala' else 1
        data['CARAC_ambiente'].append(uso_amb)
        nome_app = f'{amb} {planilha[i+2][6]}'
        carac_piso = planilha[i+2][11]
        carac_cob = planilha[i+2][12]
        if carac_piso == 'Contato com o solo' and carac_cob == 'Exposto ao sol e ao vento':
            carac_condicoes = 3
        elif carac_piso == 'Contato com o solo' and carac_cob == 'Entre pavimentos':
            carac_condicoes = 0
        elif carac_piso == 'Entre pavimentos' and carac_cob == 'Entre pavimentos':
            carac_condicoes = 1
        elif carac_piso == 'Entre pavimentos' and carac_cob == 'Exposto ao sol e ao vento':
            carac_condicoes = 2

        data['CARAC_condicoes'].append(carac_condicoes)
        data['APP_FloorArea'].append(planilha[i + 2][13])
        pe_direito = planilha[i + 2][14]
        data['APP_CeilingHeight'].append(pe_direito)
        veneziana = 1 if (planilha[i + 2][15]) == 'Sim' else 0
        data['SAMPLE_blind'].append(veneziana)
        azimute = planilha[i + 2][16]
        azi_resto = azimute % 90 if (azimute % 90) < 45 else (azimute % 90) - 90
        data['MAR_azi_resto'].append(azi_resto)
        ab_ventila = planilha[i + 2][17]
        u_vidro = planilha[i + 2][18]
        data['SAMPLE_uVidro'].append(u_vidro)
        fs_vidro = planilha[i + 2][19]
        data['SAMPLE_shgc'].append(fs_vidro)
        u_piso = planilha[i + 2][20]
        data['CONST_ThermalConductance_PISO_TERREO'].append(1 / ((1 / u_piso) - 0.17))
        ct_piso = planilha[i + 2][21]
        data['CONST_laje_CT'].append(ct_piso)
        abs_par_ext = planilha[i+2][22]
        data['SAMPLE_wall_abs'].append(abs_par_ext)
        u_par_ext = planilha[i + 2][23]
        data['CONST_ThermalConductance_PAR_EXT'].append(1 / ((1 / u_par_ext) - 0.17))
        ct_par_ext = planilha[i + 2][24]
        data['CONST_par_ext_CT'].append(ct_par_ext)
        abs_cob = planilha[i+2][25]
        data['SAMPLE_roof_abs'].append(abs_cob)
        u_cob = planilha[i+2][26]
        data['CONST_ThermalConductance_COB'].append(
            (1 / ((1 / u_cob) - 0.21)) if carac_cob == 'Exposto ao sol e ao vento'
            else (1 / ((1 / u_cob) - 0.17)))
        ct_cob = planilha[i+2][27]
        data['CONST_cob_CT'].append(ct_cob)

        data['MAR_wall_area_apt'].append(planilha[i+2][28]*pe_direito)
        data['MAR_wall_area_dorm'].append(planilha[i+2][29]*pe_direito)
        data['MAR_wall_area_sala'].append(planilha[i+2][30]*pe_direito)
        data['ANG_N_anghd'].append(planilha[i+2][31])
        data['ANG_N_anghe'].append(planilha[i+2][32])
        data['ANG_N_ange'].append(planilha[i+2][33])
        data['ANG_N_angv'].append(planilha[i+2][34])
        data['APP_N_ParExt_SUP_AreaGross'].append((planilha[i+2][35])*pe_direito)
        data['APP_N_ParInt_SUP_AreaGross'].append((planilha[i+2][36])*pe_direito)
        data['APP_N_Window_SUP_AreaGross'].append(planilha[i+2][37])
        data['ANG_S_anghd'].append(planilha[i+2][38])
        data['ANG_S_anghe'].append(planilha[i+2][39])
        data['ANG_S_ange'].append(planilha[i+2][40])
        data['ANG_S_angv'].append(planilha[i+2][41])
        data['APP_S_ParExt_SUP_AreaGross'].append((planilha[i+2][42])*pe_direito)
        data['APP_S_ParInt_SUP_AreaGross'].append((planilha[i+2][43])*pe_direito)
        data['APP_S_Window_SUP_AreaGross'].append(planilha[i+2][44])
        data['ANG_L_anghd'].append(planilha[i+2][45])
        data['ANG_L_anghe'].append(planilha[i+2][46])
        data['ANG_L_ange'].append(planilha[i+2][47])
        data['ANG_L_angv'].append(planilha[i+2][48])
        data['APP_E_ParExt_SUP_AreaGross'].append((planilha[i+2][49])*pe_direito)
        data['APP_E_ParInt_SUP_AreaGross'].append((planilha[i+2][50])*pe_direito)
        data['APP_E_Window_SUP_AreaGross'].append(planilha[i+2][51])
        data['ANG_O_anghd'].append(planilha[i+2][52])
        data['ANG_O_anghe'].append(planilha[i+2][53])
        data['ANG_O_ange'].append(planilha[i+2][54])
        data['ANG_O_angv'].append(planilha[i+2][55])
        data['APP_W_ParExt_SUP_AreaGross'].append((planilha[i+2][56])*pe_direito)
        data['APP_W_ParInt_SUP_AreaGross'].append((planilha[i+2][57])*pe_direito)
        data['APP_W_Window_SUP_AreaGross'].append(planilha[i+2][58])
        data['APP_N_Door_isIn'].append(1 if planilha[i+2][59] == 'Sim' else 0)
        data['APP_S_Door_isIn'].append(1 if planilha[i + 2][60] == 'Sim' else 0)
        data['APP_E_Door_isIn'].append(1 if planilha[i + 2][61] == 'Sim' else 0)
        data['APP_W_Door_isIn'].append(1 if planilha[i + 2][62] == 'Sim' else 0)

        area_jan_app = (planilha[i+2][37])+(planilha[i+2][44])+(planilha[i+2][51])+(planilha[i+2][58])
        data['APP_ExteriorWindowArea'].append(area_jan_app)
        data['SAMPLE_openFactor'].append(ab_ventila/area_jan_app)

        media_tbs = climas.loc[climas.cidade == epw]['TBSm'].mean()
        media_tbs = round(media_tbs, 1)

        zb = climas.loc[climas.cidade == epw]['zona_bioclimatica'].tolist()[0]

        if media_tbs <= 25:
            data['CLIMA_TOMax'].append(26)
        elif 25 <= media_tbs < 27:
            data['CLIMA_TOMax'].append(28)
        else:
            data['CLIMA_TOMax'].append(30)

        data['CLIMA_TBSm'] = media_tbs

        nome['APP'].append(nome_app)

        i += 1

    df = pd.DataFrame(data)
    df_nome = pd.DataFrame(nome)


    def set_dummies(col, uniques):
        for i in uniques:
            df[col + '_' + str(i)] = 0
            df.loc[df[col] == i, col + '_' + str(i)] = 1


    # aplicando as dummies variables para ambiente, condicoes e tomax
    set_dummies('CARAC_condicoes', [0, 1, 2, 3])
    set_dummies('CARAC_ambiente', [0, 1])
    set_dummies('CLIMA_TOMax', [26, 28, 30])

    # soma para o building
    df['BLDG_W_ParExt'] = df['APP_W_ParExt_SUP_AreaGross'].sum() * 12
    df['BLDG_E_ParExt'] = df['APP_E_ParExt_SUP_AreaGross'].sum() * 12
    df['BLDG_S_ParExt'] = df['APP_S_ParExt_SUP_AreaGross'].sum() * 12
    df['BLDG_N_ParExt'] = df['APP_N_ParExt_SUP_AreaGross'].sum() * 12
    df['BLDG_W_ParInt'] = df['APP_W_ParInt_SUP_AreaGross'].sum() * 12
    df['BLDG_E_ParInt'] = df['APP_E_ParInt_SUP_AreaGross'].sum() * 12
    df['BLDG_S_ParInt'] = df['APP_S_ParInt_SUP_AreaGross'].sum() * 12
    df['BLDG_N_ParInt'] = df['APP_N_ParInt_SUP_AreaGross'].sum() * 12
    df['BLDG_W_Window'] = df['APP_W_Window_SUP_AreaGross'].sum() * 12
    df['BLDG_E_Window'] = df['APP_E_Window_SUP_AreaGross'].sum() * 12
    df['BLDG_S_Window'] = df['APP_S_Window_SUP_AreaGross'].sum() * 12
    df['BLDG_N_Window'] = df['APP_N_Window_SUP_AreaGross'].sum() * 12
    df['BLDG_NetConditionedBuildingArea'] = df['APP_FloorArea'].sum()

    df = df.drop(['CARAC_ambiente', 'CLIMA_TOMax'], axis=1)  # 'CARAC_condicoes',


    df_ref = df.copy()


    contador_janelas = 0
    df_ref['CONST_par_ext_CT'] = 220
    df_ref['CONST_ThermalConductance_PAR_EXT'] = 1 / (1 / 4.4 - 0.17)
    df_ref['SAMPLE_wall_abs'] = 0.58
    df_ref['CONST_ThermalConductance_PISO_TERREO'] = 1 / (1 / 3.74 - 0.17)
    df_ref['CONST_laje_CT'] = 220
    df_ref['SAMPLE_shgc'] = 0.87
    df_ref['SAMPLE_uVidro'] = 5.7
    df_ref['SAMPLE_openFactor'] = 0.45
    df_ref['APP_ExteriorWindowArea'] = df_ref['APP_FloorArea'] * 0.17
    df_ref["ANG_N_angv"] = 0
    df_ref["ANG_S_angv"] = 0
    df_ref["ANG_L_angv"] = 0
    df_ref["ANG_O_angv"] = 0

    df_ref = df_ref.to_dict()

    for key, value in df_ref.items():
        i = 0
        while i < len(value):
            if df_ref['APP_N_Window_SUP_AreaGross'][i] != 0:
                contador_janelas += 1
            if df_ref['APP_S_Window_SUP_AreaGross'][i] != 0:
                contador_janelas += 1
            if df_ref['APP_E_Window_SUP_AreaGross'][i] != 0:
                contador_janelas += 1
            if df_ref['APP_W_Window_SUP_AreaGross'][i] != 0:
                contador_janelas += 1

            if df_ref['APP_N_Window_SUP_AreaGross'][i] != 0:
                df_ref['APP_N_Window_SUP_AreaGross'][i] = df_ref['APP_ExteriorWindowArea'][i] / contador_janelas
                df_ref['BLDG_N_Window'][i] = (df_ref['BLDG_NetConditionedBuildingArea'][i] * 0.17) / contador_janelas
            if df_ref['APP_S_Window_SUP_AreaGross'][i] != 0:
                df_ref['APP_S_Window_SUP_AreaGross'][i] = df_ref['APP_ExteriorWindowArea'][i] / contador_janelas
                df_ref['BLDG_S_Window'][i] = (df_ref['BLDG_NetConditionedBuildingArea'][i] * 0.17) / contador_janelas
            if df_ref['APP_E_Window_SUP_AreaGross'][i] != 0:
                df_ref['APP_E_Window_SUP_AreaGross'][i] = df_ref['APP_ExteriorWindowArea'][i] / contador_janelas
                df_ref['BLDG_E_Window'][i] = (df_ref['BLDG_NetConditionedBuildingArea'][i] * 0.17) / contador_janelas
            if df_ref['APP_W_Window_SUP_AreaGross'][i] != 0:
                df_ref['APP_W_Window_SUP_AreaGross'][i] = df_ref['APP_ExteriorWindowArea'][i] / contador_janelas
                df_ref['BLDG_W_Window'][i] = (df_ref['BLDG_NetConditionedBuildingArea'][i] * 0.17) / contador_janelas

            if carac_condicoes == 3 or carac_condicoes == 2:
                if zb == "ZB8":
                    df_ref['CONST_cob_CT'][i] = 228.57
                    df_ref['CONST_ThermalConductance_COB'][i] = 1.057  # com isolamento
                    df_ref['SAMPLE_roof_abs'][i] = 0.7
                else:
                    df_ref['CONST_cob_CT'][i] = 228.57
                    df_ref['CONST_ThermalConductance_COB'][i] = 1 / (1 / 2.06 - 0.21)
                    df_ref['SAMPLE_roof_abs'][i] = 0.65
            else:
                df_ref['CONST_cob_CT'][i] = 220
                df_ref['CONST_ThermalConductance_COB'][i] = 1 / (1 / 3.74 - 0.17)
            i += 1




    df_ref = pd.DataFrame.from_dict(df_ref)


    df2 = df.copy()
    df_ref2 = df_ref.copy()

    nome_2 = df_nome.copy()


    # climas por último faz climas para cada linha, então colocar em cada linha os apps antes!!!
    for i in range(12):
        clima = climas.loc[(climas.cidade == epw) & (climas.month == i + 1)]


        df2['mes'] = i + 1
        s = i + 1
        nome_2['mes'] = clima['month'].iloc[0]
        df2['CLIMA_month'] = clima['month'].iloc[0]
        df2['CLIMA_ws_std'] = clima['ws_std'].iloc[0]
        df2['CLIMA_ws_min'] = clima['ws_min'].iloc[0]
        df2['CLIMA_ws_mean'] = clima['ws_mean'].iloc[0]
        df2['CLIMA_ws_max'] = clima['ws_max'].iloc[0]
        df2['CLIMA_ws_75p'] = clima['ws_75p'].iloc[0]
        df2['CLIMA_ws_50p'] = clima['ws_50p'].iloc[0]
        df2['CLIMA_ws_25p'] = clima['ws_25p'].iloc[0]
        df2['CLIMA_wd_std'] = clima['wd_std'].iloc[0]
        df2['CLIMA_wd_min'] = clima['wd_min'].iloc[0]
        df2['CLIMA_wd_mean'] = clima['wd_mean'].iloc[0]
        df2['CLIMA_wd_max'] = clima['wd_max'].iloc[0]
        df2['CLIMA_wd_75p'] = clima['wd_75p'].iloc[0]
        df2['CLIMA_wd_50p'] = clima['wd_50p'].iloc[0]
        df2['CLIMA_wd_25p'] = clima['wd_25p'].iloc[0]
        df2['CLIMA_ts_std'] = clima['ts_std'].iloc[0]
        df2['CLIMA_ts_min'] = clima['ts_min'].iloc[0]
        df2['CLIMA_ts_mean'] = clima['ts_mean'].iloc[0]
        df2['CLIMA_ts_max'] = clima['ts_max'].iloc[0]
        df2['CLIMA_ts_75p'] = clima['ts_75p'].iloc[0]
        df2['CLIMA_ts_50p'] = clima['ts_50p'].iloc[0]
        df2['CLIMA_ts_25p'] = clima['ts_25p'].iloc[0]
        df2['CLIMA_ghr_std'] = clima['ghr_std'].iloc[0]
        df2['CLIMA_ghr_min'] = clima['ghr_min'].iloc[0]
        df2['CLIMA_ghr_mean'] = clima['ghr_mean'].iloc[0]
        df2['CLIMA_ghr_max'] = clima['ghr_max'].iloc[0]
        df2['CLIMA_ghr_75p'] = clima['ghr_75p'].iloc[0]
        df2['CLIMA_ghr_50p'] = clima['ghr_50p'].iloc[0]
        df2['CLIMA_ghr_25p'] = clima['ghr_25p'].iloc[0]
        df2['CLIMA_dpt_std'] = clima['dpt_std'].iloc[0]
        df2['CLIMA_dpt_min'] = clima['dpt_min'].iloc[0]
        df2['CLIMA_dpt_mean'] = clima['dpt_mean'].iloc[0]
        df2['CLIMA_dpt_max'] = clima['dpt_max'].iloc[0]
        df2['CLIMA_dpt_75p'] = clima['dpt_75p'].iloc[0]
        df2['CLIMA_dpt_50p'] = clima['dpt_50p'].iloc[0]
        df2['CLIMA_dpt_25p'] = clima['dpt_25p'].iloc[0]
        df2['CLIMA_dnr_std'] = clima['dnr_std'].iloc[0]
        df2['CLIMA_dnr_min'] = clima['dnr_min'].iloc[0]
        df2['CLIMA_dnr_mean'] = clima['dnr_mean'].iloc[0]
        df2['CLIMA_dnr_max'] = clima['dnr_max'].iloc[0]
        df2['CLIMA_dnr_75p'] = clima['dnr_75p'].iloc[0]
        df2['CLIMA_dnr_50p'] = clima['dnr_50p'].iloc[0]
        df2['CLIMA_dnr_25p'] = clima['dnr_25p'].iloc[0]
        df2['CLIMA_dhr_std'] = clima['dhr_std'].iloc[0]
        df2['CLIMA_dhr_min'] = clima['dhr_min'].iloc[0]
        df2['CLIMA_dhr_mean'] = clima['dhr_mean'].iloc[0]
        df2['CLIMA_dhr_max'] = clima['dhr_max'].iloc[0]
        df2['CLIMA_dhr_75p'] = clima['dhr_75p'].iloc[0]
        df2['CLIMA_dhr_50p'] = clima['dhr_50p'].iloc[0]
        df2['CLIMA_dhr_25p'] = clima['dhr_25p'].iloc[0]
        df2['CLIMA_dbt_std'] = clima['dbt_std'].iloc[0]
        df2['CLIMA_dbt_min'] = clima['dbt_min'].iloc[0]
        df2['CLIMA_dbt_mean'] = clima['dbt_mean'].iloc[0]
        df2['CLIMA_dbt_max'] = clima['dbt_max'].iloc[0]
        df2['CLIMA_dbt_75p'] = clima['dbt_75p'].iloc[0]
        df2['CLIMA_dbt_50p'] = clima['dbt_50p'].iloc[0]
        df2['CLIMA_dbt_25p'] = clima['dbt_25p'].iloc[0]
        df2['EPW_Elevation'] = clima['alt'].iloc[0]
        df2['EPW_Latitude'] = clima['lat'].iloc[0]
        df2['CLIMA_dbt_dia_25p'] = clima['dbt_dia_25p'].iloc[0]
        df2['CLIMA_dbt_dia_50p'] = clima['dbt_dia_50p'].iloc[0]
        df2['CLIMA_dbt_dia_75p'] = clima['dbt_dia_75p'].iloc[0]
        df2['CLIMA_dbt_dia_max'] = clima['dbt_dia_max'].iloc[0]
        df2['CLIMA_dbt_dia_mean'] = clima['dbt_dia_mean'].iloc[0]
        df2['CLIMA_dbt_dia_min'] = clima['dbt_dia_min'].iloc[0]
        df2['CLIMA_dbt_dia_std'] = clima['dbt_dia_std'].iloc[0]
        df2['CLIMA_dbt_noite_25p'] = clima['dbt_noite_25p'].iloc[0]
        df2['CLIMA_dbt_noite_50p'] = clima['dbt_noite_50p'].iloc[0]
        df2['CLIMA_dbt_noite_75p'] = clima['dbt_noite_75p'].iloc[0]
        df2['CLIMA_dbt_noite_max'] = clima['dbt_noite_max'].iloc[0]
        df2['CLIMA_dbt_noite_mean'] = clima['dbt_noite_mean'].iloc[0]
        df2['CLIMA_dbt_noite_min'] = clima['dbt_noite_min'].iloc[0]
        df2['CLIMA_dbt_noite_std'] = clima['dbt_noite_std'].iloc[0]
        df2['CLIMA_dpt_dia_25p'] = clima['dpt_dia_25p'].iloc[0]
        df2['CLIMA_dpt_dia_50p'] = clima['dpt_dia_50p'].iloc[0]
        df2['CLIMA_dpt_dia_75p'] = clima['dpt_dia_75p'].iloc[0]
        df2['CLIMA_dpt_dia_max'] = clima['dpt_dia_max'].iloc[0]
        df2['CLIMA_dpt_dia_mean'] = clima['dpt_dia_mean'].iloc[0]
        df2['CLIMA_dpt_dia_min'] = clima['dpt_dia_min'].iloc[0]
        df2['CLIMA_dpt_dia_std'] = clima['dpt_dia_std'].iloc[0]
        df2['CLIMA_dpt_noite_25p'] = clima['dpt_noite_25p'].iloc[0]
        df2['CLIMA_dpt_noite_50p'] = clima['dpt_noite_50p'].iloc[0]
        df2['CLIMA_dpt_noite_75p'] = clima['dpt_noite_75p'].iloc[0]
        df2['CLIMA_dpt_noite_max'] = clima['dpt_noite_max'].iloc[0]
        df2['CLIMA_dpt_noite_mean'] = clima['dpt_noite_mean'].iloc[0]
        df2['CLIMA_dpt_noite_min'] = clima['dpt_noite_min'].iloc[0]
        df2['CLIMA_dpt_noite_std'] = clima['dpt_noite_std'].iloc[0]
        df2['CLIMA_ph_inf_dia'] = clima['ph_inf_dia'].iloc[0]
        df2['CLIMA_ph_inf_noite'] = clima['ph_inf_noite'].iloc[0]
        df2['CLIMA_ph_sup_dia'] = clima['ph_sup_dia'].iloc[0]
        df2['CLIMA_ph_sup_noite'] = clima['ph_sup_noite'].iloc[0]
        df2['CLIMA_ts_dia_25p'] = clima['ts_dia_25p'].iloc[0]
        df2['CLIMA_ts_dia_50p'] = clima['ts_dia_50p'].iloc[0]
        df2['CLIMA_ts_dia_75p'] = clima['ts_dia_75p'].iloc[0]
        df2['CLIMA_ts_dia_max'] = clima['ts_dia_max'].iloc[0]
        df2['CLIMA_ts_dia_mean'] = clima['ts_dia_mean'].iloc[0]
        df2['CLIMA_ts_dia_min'] = clima['ts_dia_min'].iloc[0]
        df2['CLIMA_ts_dia_std'] = clima['ts_dia_std'].iloc[0]
        df2['CLIMA_ts_noite_25p'] = clima['ts_noite_25p'].iloc[0]
        df2['CLIMA_ts_noite_50p'] = clima['ts_noite_50p'].iloc[0]
        df2['CLIMA_ts_noite_75p'] = clima['ts_noite_75p'].iloc[0]
        df2['CLIMA_ts_noite_max'] = clima['ts_noite_max'].iloc[0]
        df2['CLIMA_ts_noite_mean'] = clima['ts_noite_mean'].iloc[0]
        df2['CLIMA_ts_noite_min'] = clima['ts_noite_min'].iloc[0]
        df2['CLIMA_ts_noite_std'] = clima['ts_noite_std'].iloc[0]
        df2['CLIMA_wd_dia_25p'] = clima['wd_dia_25p'].iloc[0]
        df2['CLIMA_wd_dia_50p'] = clima['wd_dia_50p'].iloc[0]
        df2['CLIMA_wd_dia_75p'] = clima['wd_dia_75p'].iloc[0]
        df2['CLIMA_wd_dia_max'] = clima['wd_dia_max'].iloc[0]
        df2['CLIMA_wd_dia_mean'] = clima['wd_dia_mean'].iloc[0]
        df2['CLIMA_wd_dia_min'] = clima['wd_dia_min'].iloc[0]
        df2['CLIMA_wd_dia_std'] = clima['wd_dia_std'].iloc[0]
        df2['CLIMA_wd_noite_25p'] = clima['wd_noite_25p'].iloc[0]
        df2['CLIMA_wd_noite_50p'] = clima['wd_noite_50p'].iloc[0]
        df2['CLIMA_wd_noite_75p'] = clima['wd_noite_75p'].iloc[0]
        df2['CLIMA_wd_noite_max'] = clima['wd_noite_max'].iloc[0]
        df2['CLIMA_wd_noite_mean'] = clima['wd_noite_mean'].iloc[0]
        df2['CLIMA_wd_noite_min'] = clima['wd_noite_min'].iloc[0]
        df2['CLIMA_wd_noite_std'] = clima['wd_noite_std'].iloc[0]
        df2['CLIMA_ws_dia_25p'] = clima['ws_dia_25p'].iloc[0]
        df2['CLIMA_ws_dia_50p'] = clima['ws_dia_50p'].iloc[0]
        df2['CLIMA_ws_dia_75p'] = clima['ws_dia_75p'].iloc[0]
        df2['CLIMA_ws_dia_max'] = clima['ws_dia_max'].iloc[0]
        df2['CLIMA_ws_dia_mean'] = clima['ws_dia_mean'].iloc[0]
        df2['CLIMA_ws_dia_min'] = clima['ws_dia_min'].iloc[0]
        df2['CLIMA_ws_dia_std'] = clima['ws_dia_std'].iloc[0]
        df2['CLIMA_ws_noite_25p'] = clima['ws_noite_25p'].iloc[0]
        df2['CLIMA_ws_noite_50p'] = clima['ws_noite_50p'].iloc[0]
        df2['CLIMA_ws_noite_75p'] = clima['ws_noite_75p'].iloc[0]
        df2['CLIMA_ws_noite_max'] = clima['ws_noite_max'].iloc[0]
        df2['CLIMA_ws_noite_mean'] = clima['ws_noite_mean'].iloc[0]
        df2['CLIMA_ws_noite_min'] = clima['ws_noite_min'].iloc[0]
        df2['CLIMA_ws_noite_std'] = clima['ws_noite_std'].iloc[0]
        if i == 0:
            df = df2.copy()

        else:
            df = df.append(df2, ignore_index=True)
            df_nome = df_nome.append(nome_2, ignore_index=True)

        df_ref2['mes'] = i + 1
        nome_2['mes'] = clima['month'].iloc[0]
        df_ref2['CLIMA_month'] = clima['month'].iloc[0]
        df_ref2['CLIMA_ws_std'] = clima['ws_std'].iloc[0]
        df_ref2['CLIMA_ws_min'] = clima['ws_min'].iloc[0]
        df_ref2['CLIMA_ws_mean'] = clima['ws_mean'].iloc[0]
        df_ref2['CLIMA_ws_max'] = clima['ws_max'].iloc[0]
        df_ref2['CLIMA_ws_75p'] = clima['ws_75p'].iloc[0]
        df_ref2['CLIMA_ws_50p'] = clima['ws_50p'].iloc[0]
        df_ref2['CLIMA_ws_25p'] = clima['ws_25p'].iloc[0]
        df_ref2['CLIMA_wd_std'] = clima['wd_std'].iloc[0]
        df_ref2['CLIMA_wd_min'] = clima['wd_min'].iloc[0]
        df_ref2['CLIMA_wd_mean'] = clima['wd_mean'].iloc[0]
        df_ref2['CLIMA_wd_max'] = clima['wd_max'].iloc[0]
        df_ref2['CLIMA_wd_75p'] = clima['wd_75p'].iloc[0]
        df_ref2['CLIMA_wd_50p'] = clima['wd_50p'].iloc[0]
        df_ref2['CLIMA_wd_25p'] = clima['wd_25p'].iloc[0]
        df_ref2['CLIMA_ts_std'] = clima['ts_std'].iloc[0]
        df_ref2['CLIMA_ts_min'] = clima['ts_min'].iloc[0]
        df_ref2['CLIMA_ts_mean'] = clima['ts_mean'].iloc[0]
        df_ref2['CLIMA_ts_max'] = clima['ts_max'].iloc[0]
        df_ref2['CLIMA_ts_75p'] = clima['ts_75p'].iloc[0]
        df_ref2['CLIMA_ts_50p'] = clima['ts_50p'].iloc[0]
        df_ref2['CLIMA_ts_25p'] = clima['ts_25p'].iloc[0]
        df_ref2['CLIMA_ghr_std'] = clima['ghr_std'].iloc[0]
        df_ref2['CLIMA_ghr_min'] = clima['ghr_min'].iloc[0]
        df_ref2['CLIMA_ghr_mean'] = clima['ghr_mean'].iloc[0]
        df_ref2['CLIMA_ghr_max'] = clima['ghr_max'].iloc[0]
        df_ref2['CLIMA_ghr_75p'] = clima['ghr_75p'].iloc[0]
        df_ref2['CLIMA_ghr_50p'] = clima['ghr_50p'].iloc[0]
        df_ref2['CLIMA_ghr_25p'] = clima['ghr_25p'].iloc[0]
        df_ref2['CLIMA_dpt_std'] = clima['dpt_std'].iloc[0]
        df_ref2['CLIMA_dpt_min'] = clima['dpt_min'].iloc[0]
        df_ref2['CLIMA_dpt_mean'] = clima['dpt_mean'].iloc[0]
        df_ref2['CLIMA_dpt_max'] = clima['dpt_max'].iloc[0]
        df_ref2['CLIMA_dpt_75p'] = clima['dpt_75p'].iloc[0]
        df_ref2['CLIMA_dpt_50p'] = clima['dpt_50p'].iloc[0]
        df_ref2['CLIMA_dpt_25p'] = clima['dpt_25p'].iloc[0]
        df_ref2['CLIMA_dnr_std'] = clima['dnr_std'].iloc[0]
        df_ref2['CLIMA_dnr_min'] = clima['dnr_min'].iloc[0]
        df_ref2['CLIMA_dnr_mean'] = clima['dnr_mean'].iloc[0]
        df_ref2['CLIMA_dnr_max'] = clima['dnr_max'].iloc[0]
        df_ref2['CLIMA_dnr_75p'] = clima['dnr_75p'].iloc[0]
        df_ref2['CLIMA_dnr_50p'] = clima['dnr_50p'].iloc[0]
        df_ref2['CLIMA_dnr_25p'] = clima['dnr_25p'].iloc[0]
        df_ref2['CLIMA_dhr_std'] = clima['dhr_std'].iloc[0]
        df_ref2['CLIMA_dhr_min'] = clima['dhr_min'].iloc[0]
        df_ref2['CLIMA_dhr_mean'] = clima['dhr_mean'].iloc[0]
        df_ref2['CLIMA_dhr_max'] = clima['dhr_max'].iloc[0]
        df_ref2['CLIMA_dhr_75p'] = clima['dhr_75p'].iloc[0]
        df_ref2['CLIMA_dhr_50p'] = clima['dhr_50p'].iloc[0]
        df_ref2['CLIMA_dhr_25p'] = clima['dhr_25p'].iloc[0]
        df_ref2['CLIMA_dbt_std'] = clima['dbt_std'].iloc[0]
        df_ref2['CLIMA_dbt_min'] = clima['dbt_min'].iloc[0]
        df_ref2['CLIMA_dbt_mean'] = clima['dbt_mean'].iloc[0]
        df_ref2['CLIMA_dbt_max'] = clima['dbt_max'].iloc[0]
        df_ref2['CLIMA_dbt_75p'] = clima['dbt_75p'].iloc[0]
        df_ref2['CLIMA_dbt_50p'] = clima['dbt_50p'].iloc[0]
        df_ref2['CLIMA_dbt_25p'] = clima['dbt_25p'].iloc[0]
        df_ref2['EPW_Elevation'] = clima['alt'].iloc[0]
        df_ref2['EPW_Latitude'] = clima['lat'].iloc[0]
        df_ref2['CLIMA_dbt_dia_25p'] = clima['dbt_dia_25p'].iloc[0]
        df_ref2['CLIMA_dbt_dia_50p'] = clima['dbt_dia_50p'].iloc[0]
        df_ref2['CLIMA_dbt_dia_75p'] = clima['dbt_dia_75p'].iloc[0]
        df_ref2['CLIMA_dbt_dia_max'] = clima['dbt_dia_max'].iloc[0]
        df_ref2['CLIMA_dbt_dia_mean'] = clima['dbt_dia_mean'].iloc[0]
        df_ref2['CLIMA_dbt_dia_min'] = clima['dbt_dia_min'].iloc[0]
        df_ref2['CLIMA_dbt_dia_std'] = clima['dbt_dia_std'].iloc[0]
        df_ref2['CLIMA_dbt_noite_25p'] = clima['dbt_noite_25p'].iloc[0]
        df_ref2['CLIMA_dbt_noite_50p'] = clima['dbt_noite_50p'].iloc[0]
        df_ref2['CLIMA_dbt_noite_75p'] = clima['dbt_noite_75p'].iloc[0]
        df_ref2['CLIMA_dbt_noite_max'] = clima['dbt_noite_max'].iloc[0]
        df_ref2['CLIMA_dbt_noite_mean'] = clima['dbt_noite_mean'].iloc[0]
        df_ref2['CLIMA_dbt_noite_min'] = clima['dbt_noite_min'].iloc[0]
        df_ref2['CLIMA_dbt_noite_std'] = clima['dbt_noite_std'].iloc[0]
        df_ref2['CLIMA_dpt_dia_25p'] = clima['dpt_dia_25p'].iloc[0]
        df_ref2['CLIMA_dpt_dia_50p'] = clima['dpt_dia_50p'].iloc[0]
        df_ref2['CLIMA_dpt_dia_75p'] = clima['dpt_dia_75p'].iloc[0]
        df_ref2['CLIMA_dpt_dia_max'] = clima['dpt_dia_max'].iloc[0]
        df_ref2['CLIMA_dpt_dia_mean'] = clima['dpt_dia_mean'].iloc[0]
        df_ref2['CLIMA_dpt_dia_min'] = clima['dpt_dia_min'].iloc[0]
        df_ref2['CLIMA_dpt_dia_std'] = clima['dpt_dia_std'].iloc[0]
        df_ref2['CLIMA_dpt_noite_25p'] = clima['dpt_noite_25p'].iloc[0]
        df_ref2['CLIMA_dpt_noite_50p'] = clima['dpt_noite_50p'].iloc[0]
        df_ref2['CLIMA_dpt_noite_75p'] = clima['dpt_noite_75p'].iloc[0]
        df_ref2['CLIMA_dpt_noite_max'] = clima['dpt_noite_max'].iloc[0]
        df_ref2['CLIMA_dpt_noite_mean'] = clima['dpt_noite_mean'].iloc[0]
        df_ref2['CLIMA_dpt_noite_min'] = clima['dpt_noite_min'].iloc[0]
        df_ref2['CLIMA_dpt_noite_std'] = clima['dpt_noite_std'].iloc[0]
        df_ref2['CLIMA_ph_inf_dia'] = clima['ph_inf_dia'].iloc[0]
        df_ref2['CLIMA_ph_inf_noite'] = clima['ph_inf_noite'].iloc[0]
        df_ref2['CLIMA_ph_sup_dia'] = clima['ph_sup_dia'].iloc[0]
        df_ref2['CLIMA_ph_sup_noite'] = clima['ph_sup_noite'].iloc[0]
        df_ref2['CLIMA_ts_dia_25p'] = clima['ts_dia_25p'].iloc[0]
        df_ref2['CLIMA_ts_dia_50p'] = clima['ts_dia_50p'].iloc[0]
        df_ref2['CLIMA_ts_dia_75p'] = clima['ts_dia_75p'].iloc[0]
        df_ref2['CLIMA_ts_dia_max'] = clima['ts_dia_max'].iloc[0]
        df_ref2['CLIMA_ts_dia_mean'] = clima['ts_dia_mean'].iloc[0]
        df_ref2['CLIMA_ts_dia_min'] = clima['ts_dia_min'].iloc[0]
        df_ref2['CLIMA_ts_dia_std'] = clima['ts_dia_std'].iloc[0]
        df_ref2['CLIMA_ts_noite_25p'] = clima['ts_noite_25p'].iloc[0]
        df_ref2['CLIMA_ts_noite_50p'] = clima['ts_noite_50p'].iloc[0]
        df_ref2['CLIMA_ts_noite_75p'] = clima['ts_noite_75p'].iloc[0]
        df_ref2['CLIMA_ts_noite_max'] = clima['ts_noite_max'].iloc[0]
        df_ref2['CLIMA_ts_noite_mean'] = clima['ts_noite_mean'].iloc[0]
        df_ref2['CLIMA_ts_noite_min'] = clima['ts_noite_min'].iloc[0]
        df_ref2['CLIMA_ts_noite_std'] = clima['ts_noite_std'].iloc[0]
        df_ref2['CLIMA_wd_dia_25p'] = clima['wd_dia_25p'].iloc[0]
        df_ref2['CLIMA_wd_dia_50p'] = clima['wd_dia_50p'].iloc[0]
        df_ref2['CLIMA_wd_dia_75p'] = clima['wd_dia_75p'].iloc[0]
        df_ref2['CLIMA_wd_dia_max'] = clima['wd_dia_max'].iloc[0]
        df_ref2['CLIMA_wd_dia_mean'] = clima['wd_dia_mean'].iloc[0]
        df_ref2['CLIMA_wd_dia_min'] = clima['wd_dia_min'].iloc[0]
        df_ref2['CLIMA_wd_dia_std'] = clima['wd_dia_std'].iloc[0]
        df_ref2['CLIMA_wd_noite_25p'] = clima['wd_noite_25p'].iloc[0]
        df_ref2['CLIMA_wd_noite_50p'] = clima['wd_noite_50p'].iloc[0]
        df_ref2['CLIMA_wd_noite_75p'] = clima['wd_noite_75p'].iloc[0]
        df_ref2['CLIMA_wd_noite_max'] = clima['wd_noite_max'].iloc[0]
        df_ref2['CLIMA_wd_noite_mean'] = clima['wd_noite_mean'].iloc[0]
        df_ref2['CLIMA_wd_noite_min'] = clima['wd_noite_min'].iloc[0]
        df_ref2['CLIMA_wd_noite_std'] = clima['wd_noite_std'].iloc[0]
        df_ref2['CLIMA_ws_dia_25p'] = clima['ws_dia_25p'].iloc[0]
        df_ref2['CLIMA_ws_dia_50p'] = clima['ws_dia_50p'].iloc[0]
        df_ref2['CLIMA_ws_dia_75p'] = clima['ws_dia_75p'].iloc[0]
        df_ref2['CLIMA_ws_dia_max'] = clima['ws_dia_max'].iloc[0]
        df_ref2['CLIMA_ws_dia_mean'] = clima['ws_dia_mean'].iloc[0]
        df_ref2['CLIMA_ws_dia_min'] = clima['ws_dia_min'].iloc[0]
        df_ref2['CLIMA_ws_dia_std'] = clima['ws_dia_std'].iloc[0]
        df_ref2['CLIMA_ws_noite_25p'] = clima['ws_noite_25p'].iloc[0]
        df_ref2['CLIMA_ws_noite_50p'] = clima['ws_noite_50p'].iloc[0]
        df_ref2['CLIMA_ws_noite_75p'] = clima['ws_noite_75p'].iloc[0]
        df_ref2['CLIMA_ws_noite_max'] = clima['ws_noite_max'].iloc[0]
        df_ref2['CLIMA_ws_noite_mean'] = clima['ws_noite_mean'].iloc[0]
        df_ref2['CLIMA_ws_noite_min'] = clima['ws_noite_min'].iloc[0]
        df_ref2['CLIMA_ws_noite_std'] = clima['ws_noite_std'].iloc[0]
        if i == 0:
            df_ref = df_ref2.copy()

        else:
            df_ref = df_ref.append(df_ref2, ignore_index=True)


    areas = df['APP_FloorArea']
    nomes_app = df_nome['APP']
    lista = pd.read_csv('db/exemplo_entradas.csv').columns  # csv com dados de entrada
    limites = pd.read_csv('db/limites_metamodelo.csv')  # csv com os limites do metamodelo
    df = df[lista]

    df_ref = df_ref[lista]

    input_names = limites.columns[0]
    for i in limites[input_names]:
        if i in df.columns:
            if is_numeric_dtype(df[i]):
                df[i] = (df[i] - float(limites.loc[limites[input_names] == i, 'min'])) / (
                    float(limites.loc[limites[input_names] == i, 'max']) - float(
                        limites.loc[limites[input_names] == i, 'min']),)
                ### para o ref ###
                df_ref[i] = (df_ref[i] - float(limites.loc[limites[input_names] == i, 'min'])) / (
                    float(limites.loc[limites[input_names] == i, 'max']) - float(
                        limites.loc[limites[input_names] == i, 'min']),)


    input_names = limites.columns[0]
    for i in limites[input_names]:
        if i in df.columns:
            if is_numeric_dtype(df[i]):
                df[i] = (df[i] * 2) - 1
                df_ref[i] = (df_ref[i] * 2) - 1


    for c in df.columns:
            if is_numeric_dtype(df[c]):
                df.loc[df[c] > 1, c] = 1
                df.loc[df[c] < -1, c] = -1
                ### para o ref ###
                df_ref.loc[df_ref[c] > 1, c] = 1
                df_ref.loc[df_ref[c] < -1, c] = -1


    df.to_csv('entradas_ANN.csv', index=None)
    df_ref.to_csv('entradas_ref.csv', index=None)



    import pandas as pd
    import glob
    import onnxruntime
    import os

    df_nome = 'entradas_ANN.csv'
    df_ref_nome = 'entradas_ref.csv'

    df = open(df_nome, 'r')
    df_ref = open(df_ref_nome, 'r')

    entradas = []
    entradas_ref = []


    first_line = True
    for line in df:
        if first_line:
            first_line = False
        else:
            line = [float(i) for i in line.split(',')]
            entradas.append(line)

    first_line = True
    for line in df_ref:
        if first_line:
            first_line = False
        else:
            line = [float(i) for i in line.split(',')]
            entradas_ref.append(line)


    df_out = pd.DataFrame()
    df_out_ref = pd.DataFrame()


    for onnxfile in glob.glob('network/*.onnx'):
        print(onnxfile)
        temp_model_file = onnxfile
        sess = onnxruntime.InferenceSession(temp_model_file)
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        res = sess.run([label_name], {input_name: entradas})[0].reshape(1, -1)[0]
        df_out = pd.concat([df_out, pd.DataFrame({onnxfile: pd.Series(res)})], axis=1)

        res_ref = sess.run([label_name], {input_name: entradas_ref})[0].reshape(1, -1)[0]
        df_out_ref = pd.concat([df_out_ref, pd.DataFrame({onnxfile: pd.Series(res_ref)})], axis=1)


    df_out = df_out.rename(
        columns={'network\dnn_OUT_CgTT_Cooling_0.99547_0.4165_11.92.onnx': 'Carga_termica_resfriamento',
                 'network\dnn_OUT_CgTT_Heating_0.99845_0.1747_11.43.onnx': 'Carga_termica_aquecimento',
                 'network\dnn_OUT_PHFFT_Calor_0.99715_1.7158_8.16.onnx': 'PHsFT',
                 'network\dnn_OUT_PHFFT_Frio_0.99955_0.6177_4.68.onnx': 'PHiFT',
                 'network\dnn_OUT_TOMax_0.99826_0.201_0.76.onnx': 'Tomax',
                 "network\dnn_OUT_TOMin_0.99885_0.1647_0.82.onnx": 'Tomin'})

    df_ref_out = df_out_ref.rename(
        columns={'network\dnn_OUT_CgTT_Cooling_0.99547_0.4165_11.92.onnx': 'Carga_termica_resfriamento',
                 'network\dnn_OUT_CgTT_Heating_0.99845_0.1747_11.43.onnx': 'Carga_termica_aquecimento',
                 'network\dnn_OUT_PHFFT_Calor_0.99715_1.7158_8.16.onnx': 'PHsFT',
                 'network\dnn_OUT_PHFFT_Frio_0.99955_0.6177_4.68.onnx': 'PHiFT',
                 'network\dnn_OUT_TOMax_0.99826_0.201_0.76.onnx': 'Tomax',
                 "network\dnn_OUT_TOMin_0.99885_0.1647_0.82.onnx": 'Tomin'})


    df_out['indice'] = 'UH'
    df_out['Carga_termica_resfriamento'] = df_out['Carga_termica_resfriamento'] * areas
    df_out['Carga_termica_aquecimento'] = df_out['Carga_termica_aquecimento'] * areas
    df_out['APP'] = nomes_app
    phft_calor = df_out.groupby(['APP'])[['PHsFT']].mean()
    phft_frio = df_out.groupby(['APP'])[['PHiFT']].mean()
    cooling = df_out.groupby(['APP'])[['Carga_termica_resfriamento']].sum()
    heating = df_out.groupby(['APP'])[['Carga_termica_aquecimento']].sum()
    tomax = df_out.groupby(['APP'])[['Tomax']].max()
    tomin = df_out.groupby(['APP'])[['Tomin']].min()
    df2 = phft_calor.merge(phft_frio, on=['APP'])
    df2 = df2.merge(cooling, on=['APP'])
    df2 = df2.merge(heating, on=['APP'])
    df2 = df2.merge(tomax, on=['APP'])
    df2 = df2.merge(tomin, on=['APP'])

    #### ref ####
    df_ref_out['indice'] = 'UH'
    df_ref_out['Carga_termica_resfriamento'] = df_ref_out['Carga_termica_resfriamento'] * areas
    df_ref_out['Carga_termica_aquecimento'] = df_ref_out['Carga_termica_aquecimento'] * areas
    df_ref_out['APP'] = nomes_app
    phft_calor = df_ref_out.groupby(['APP'])[['PHsFT']].mean()
    phft_frio = df_ref_out.groupby(['APP'])[['PHiFT']].mean()
    cooling = df_ref_out.groupby(['APP'])[['Carga_termica_resfriamento']].sum()
    heating = df_ref_out.groupby(['APP'])[['Carga_termica_aquecimento']].sum()
    tomax = df_ref_out.groupby(['APP'])[['Tomax']].max()
    tomin = df_ref_out.groupby(['APP'])[['Tomin']].min()
    df_ref2 = phft_calor.merge(phft_frio, on=['APP'])
    df_ref2 = df_ref2.merge(cooling, on=['APP'])
    df_ref2 = df_ref2.merge(heating, on=['APP'])
    df_ref2 = df_ref2.merge(tomax, on=['APP'])
    df_ref2 = df_ref2.merge(tomin, on=['APP'])

    df.close()
    df_ref.close()

    os.remove(df_nome)
    os.remove(df_ref_nome)

    return df2, df_ref2

