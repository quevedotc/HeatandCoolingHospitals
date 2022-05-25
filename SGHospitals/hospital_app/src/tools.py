import onnxruntime
import pandas as pd


def read_csv(fname):
    with open(fname, 'r') as f:
        df = f.readlines()

    df = [i.replace('\n', '').split(',') for i in df]
    df = list(zip(*df))
    df = [list(i) for i in df]

    for i, col in enumerate(df):
        for j, linha in enumerate(col):
            try:
                df[i][j] = float(df[i][j])
            except:
                pass

    df = {col[0]: col[1:] for col in df}

    return df


def normalizar_maxmin(valor, nome_col, dflim):
    indice_col = dflim[''].index(nome_col)
    maximo = dflim['max'][indice_col]
    minimo = dflim['min'][indice_col]
    valor = (valor - minimo) / (maximo - minimo)
    valor = (valor * 2) - 1
    if valor > 1:
        valor = 1
    if valor < -1:
        valor = -1

    return valor


def run_models(nomeredes, entradas):
    resultados = {}
    for col in nomeredes:
        sess = onnxruntime.InferenceSession(nomeredes[col])

        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name

        res = sess.run([label_name], {input_name: entradas})[0].reshape(1, -1)[0]
        resultados[col] = res

    return resultados['CgTR'], resultados['CgTA'], resultados['PHsFT'], resultados['PHiFT'], resultados['TOMax'], \
           resultados[
               'TOMin']  # , resultados['PHsFT'], resultados['PHiFT']


def get_complementos(data):
    complementos = {
        "CEEr": data["CEEr_app"],
        "CEEa": data["CEEa_app"]
    }
    tipologia = 1 if (data['piso'] == "solo" and data['cob'] == "sol") else 2

    return complementos, tipologia


def get_ZB(dfclimas, ij):
    ZB = {
        "zona_bioclimatica": dfclimas["zona_bioclimatica"][ij]
    }

    return ZB


def get_dicio_ref(data, dicionario, ZB):
    tipologia = "unifamiliar" if (data['piso'] == "solo" and data['cob'] == "sol") else "multifamiliar"

    contador_janelas = 0
    dicionario['CONST_par_ext_CT'] = 220
    dicionario['CONST_ThermalConductance_PAR_EXT'] = 1 / (1 / 4.4 - 0.17)
    dicionario['SAMPLE_wall_abs'] = 0.58
    dicionario['CONST_ThermalConductance_PISO_TERREO'] = 1 / (1 / 3.74 - 0.17)
    dicionario['CONST_laje_CT'] = 220
    dicionario['SAMPLE_shgc'] = 0.87
    dicionario['SAMPLE_uVidro'] = 5.7
    dicionario['SAMPLE_openFactor'] = 0.45
    dicionario['APP_ExteriorWindowArea'] = dicionario['APP_FloorArea'] * 0.17
    dicionario["ANG_N_angv"] = 0
    dicionario["ANG_S_angv"] = 0
    dicionario["ANG_L_angv"] = 0
    dicionario["ANG_O_angv"] = 0


    if dicionario['APP_N_Window_SUP_AreaGross'] != 0:
        contador_janelas += 1
    if dicionario['APP_S_Window_SUP_AreaGross'] != 0:
        contador_janelas += 1
    if dicionario['APP_E_Window_SUP_AreaGross'] != 0:
        contador_janelas += 1
    if dicionario['APP_W_Window_SUP_AreaGross'] != 0:
        contador_janelas += 1

    if dicionario['APP_N_Window_SUP_AreaGross'] != 0:
        dicionario['APP_N_Window_SUP_AreaGross'] = dicionario['APP_ExteriorWindowArea'] / contador_janelas
        dicionario['BLDG_N_Window'] = (dicionario['BLDG_NetConditionedBuildingArea'] * 0.17) / contador_janelas
    if dicionario['APP_S_Window_SUP_AreaGross'] != 0:
        dicionario['APP_S_Window_SUP_AreaGross'] = dicionario['APP_ExteriorWindowArea'] / contador_janelas
        dicionario['BLDG_S_Window'] = (dicionario['BLDG_NetConditionedBuildingArea'] * 0.17) / contador_janelas
    if dicionario['APP_E_Window_SUP_AreaGross'] != 0:
        dicionario['APP_E_Window_SUP_AreaGross'] = dicionario['APP_ExteriorWindowArea'] / contador_janelas
        dicionario['BLDG_E_Window'] = (dicionario['BLDG_NetConditionedBuildingArea'] * 0.17) / contador_janelas
    if dicionario['APP_W_Window_SUP_AreaGross'] != 0:
        dicionario['APP_W_Window_SUP_AreaGross'] = dicionario['APP_ExteriorWindowArea'] / contador_janelas
        dicionario['BLDG_W_Window'] = (dicionario['BLDG_NetConditionedBuildingArea'] * 0.17) / contador_janelas

    if tipologia == "unifamiliar" or (tipologia == "multifamiliar" and data['cob'] == "sol"):
        if ZB == "ZB8":
            dicionario['CONST_cob_CT'] = 228.57
            dicionario['CONST_ThermalConductance_COB'] = 1.057  # com isolamento
            dicionario['SAMPLE_roof_abs'] = 0.7
        else:
            dicionario['CONST_cob_CT'] = 228.57
            dicionario['CONST_ThermalConductance_COB'] = 1 / (1 / 2.06 - 0.21)
            dicionario['SAMPLE_roof_abs'] = 0.65
    else:
        dicionario['CONST_cob_CT'] = 220
        dicionario['CONST_ThermalConductance_COB'] = 1 / (1 / 3.74 - 0.17)

    return dicionario


def get_in2use(data):
    in2use = {
        "BLDG_NetConditionedBuildingArea": data['aTotAPP'],
        "BLDG_N_Window": data['aTJan_N'] * 12,
        "BLDG_S_Window": data['aTJan_S'] * 12,
        "BLDG_E_Window": data['aTJan_L'] * 12,
        "BLDG_W_Window": data['aTJan_O'] * 12,
        "APP_CeilingHeight": data["pedireito"],
        "BLDG_TotalBuildingAreaNaoCondicionada": data["area_apt"],
        "SAMPLE_wall_abs": data["abs_parext"],
        "SAMPLE_roof_abs": data["abs_cob"],
        "SAMPLE_shgc": data["fs_vidro"],
        "SAMPLE_uVidro": data["u_vidro"],
        "SAMPLE_openFactor": data["fv"]/(data["aJan_N"]+data["aJan_S"]+data["aJan_L"]+data["aJan_O"]),
        "CONST_cob_CT": data["ct_cob"],
        "CONST_par_ext_CT": data["ct_parext"],
        "CONST_laje_CT": data["ct_piso"],
        "SAMPLE_blind": data["vene"],
        "APP_FloorArea": data["aAPP"],
        "ANG_N_anghd": data["ahd_N"],
        "ANG_S_anghd": data["ahd_S"],
        "ANG_L_anghd": data["ahd_L"],
        "ANG_O_anghd": data["ahd_O"],
        "ANG_N_anghe": data["ahe_N"],
        "ANG_S_anghe": data["ahe_S"],
        "ANG_L_anghe": data["ahe_L"],
        "ANG_O_anghe": data["ahe_O"],
        "ANG_N_ange": data["ave_N"],
        "ANG_S_ange": data["ave_S"],
        "ANG_L_ange": data["ave_L"],
        "ANG_O_ange": data["ave_O"],
        "ANG_N_angv": data["avs_N"],
        "ANG_S_angv": data["avs_S"],
        "ANG_L_angv": data["avs_L"],
        "ANG_O_angv": data["avs_O"],
        "APP_N_Window_SUP_AreaGross": data["aJan_N"],
        "APP_S_Window_SUP_AreaGross": data["aJan_S"],
        "APP_E_Window_SUP_AreaGross": data["aJan_L"],
        "APP_W_Window_SUP_AreaGross": data["aJan_O"],
        "APP_N_Door_isIn": data["porta_N"],
        "APP_S_Door_isIn": data["porta_S"],
        "APP_E_Door_isIn": data["porta_L"],
        "APP_W_Door_isIn": data["porta_O"],
        "MAR_azi_resto": data["azimute"] % 90 if (data["azimute"] % 90) <= 45 else (data["azimute"] % 90) - 90,
        "MAR_wall_area_apt": data["contato_apt"] * data["pedireito"],
        "MAR_wall_area_dorm": data["contato_dorm"] * data["pedireito"],
        "MAR_wall_area_sala": data["contato_sala"] * data["pedireito"]
    }

    in2calc = {
        'APP_N_ParExt_SUP_AreaGross': data['DHext_N'] * data['pedireito'],
        'APP_S_ParExt_SUP_AreaGross': data['DHext_S'] * data['pedireito'],
        'APP_E_ParExt_SUP_AreaGross': data['DHext_L'] * data['pedireito'],
        'APP_W_ParExt_SUP_AreaGross': data['DHext_O'] * data['pedireito'],
        'APP_N_ParInt_SUP_AreaGross': data['DHint_N'] * data['pedireito'],
        'APP_S_ParInt_SUP_AreaGross': data['DHint_S'] * data['pedireito'],
        'APP_E_ParInt_SUP_AreaGross': data['DHint_L'] * data['pedireito'],
        'APP_W_ParInt_SUP_AreaGross': data['DHint_O'] * data['pedireito'],
        "BLDG_N_ParExt": data['dPExt_N'] * data['pedireito'] * 12,
        "BLDG_S_ParExt": data['dPExt_S'] * data['pedireito'] * 12,
        'BLDG_E_ParExt': data['dPExt_L'] * data['pedireito'] * 12,
        "BLDG_W_ParExt": data['dPExt_O'] * data['pedireito'] * 12,
        "BLDG_N_ParInt": data['dPInt_N'] * data['pedireito'] * 12,
        "BLDG_S_ParInt": data['dPInt_S'] * data['pedireito'] * 12,
        'BLDG_E_ParInt': data['dPInt_L'] * data['pedireito'] * 12,
        "BLDG_W_ParInt": data['dPInt_O'] * data['pedireito'] * 12,
        'APP_ExteriorWindowArea': sum([data[f"aJan_{ori}"] for ori in ['N', 'S', 'L', 'O']]),
        "CARAC_ambiente_0": 1 if data['amb'] == 0 else 0,
        "CARAC_ambiente_1": 1 if data['amb'] == 1 else 0,
        "CARAC_condicoes_0": 1 if (data['piso'] == 'solo' and data['cob'] == 'pav') else 0,
        "CARAC_condicoes_1": 1 if (data['piso'] == 'pav' and data['cob'] == 'pav') else 0,
        "CARAC_condicoes_2": 1 if (data['piso'] == 'pav' and data['cob'] == 'sol') else 0,
        "CARAC_condicoes_3": 1 if (data['piso'] == 'solo' and data['cob'] == 'sol') else 0,
        "CONST_ThermalConductance_COB": 1 / (1 / data["u_cob"]) - 0.21 if (data['cob'] == 'sol') else 1 / (
                1 / data["u_cob"] - 0.17),
        "CONST_ThermalConductance_PAR_EXT": 1 / (1 / data["u_parext"] - 0.17),
        "CONST_ThermalConductance_PISO_TERREO": 1 / (1 / data["u_piso"] - 0.17)
    }

    in2use.update(in2calc)

    return in2use


def converter2float(data):
    for i in data:
        try:
            data[i] = float(data[i])
        except:
            pass
    return data


'''def get_city_id(city):
    result_seq = ''
    count = 0
    for i in reversed(city):
        if i.isnumeric():
            result_seq += i
            count += 1
            if count >= 6:
                return result_seq[::-1]
        elif count > 0:
            result_seq = ''
            count = 0

    return 'no sequence found'''


def get_indices_clima(dfclimas, data):
    city = str(data["city"])
    df = pd.DataFrame(dfclimas)
    df = df[df['cidade'] == city]
    indices = df['indices'].values.tolist()
    indices_clima = []
    for i in indices:
        ind = int(i)
        indices_clima.append(ind)
    return indices_clima


def get_indice_ij_clima(indices_clima, dfclimas, month):
    ij = [i for i in indices_clima if dfclimas['month'][i] == month]
    return ij[0]


def get_in2clima(dfclimas, ij):
    in2clima = {
        "CLIMA_TBSm": dfclimas["TBSm"][ij],
        "CLIMA_TOMax_26": 1 if dfclimas["TOMax"][ij] == 26 else 0,
        "CLIMA_TOMax_28": 1 if dfclimas["TOMax"][ij] == 28 else 0,
        "CLIMA_TOMax_30": 1 if dfclimas["TOMax"][ij] == 30 else 0,
        "CLIMA_month": dfclimas['month'][ij],
        "CLIMA_ghr_std": dfclimas['ghr_std'][ij],
        "CLIMA_ghr_min": dfclimas['ghr_min'][ij],
        "CLIMA_ghr_mean": dfclimas['ghr_mean'][ij],
        "CLIMA_ghr_max": dfclimas['ghr_max'][ij],
        "CLIMA_ghr_75p": dfclimas['ghr_75p'][ij],
        "CLIMA_ghr_50p": dfclimas['ghr_50p'][ij],
        "CLIMA_ghr_25p": dfclimas['ghr_25p'][ij],
        "CLIMA_dnr_std": dfclimas['dnr_std'][ij],
        "CLIMA_dnr_min": dfclimas['dnr_min'][ij],
        "CLIMA_dnr_mean": dfclimas['dnr_mean'][ij],
        "CLIMA_dnr_max": dfclimas['dnr_max'][ij],
        "CLIMA_dnr_75p": dfclimas['dnr_75p'][ij],
        "CLIMA_dnr_50p": dfclimas['dnr_50p'][ij],
        "CLIMA_dnr_25p": dfclimas['dnr_25p'][ij],
        "CLIMA_dhr_std": dfclimas['dhr_std'][ij],
        "CLIMA_dhr_min": dfclimas['dhr_min'][ij],
        "CLIMA_dhr_mean": dfclimas['dhr_mean'][ij],
        "CLIMA_dhr_max": dfclimas['dhr_max'][ij],
        "CLIMA_dhr_75p": dfclimas['dhr_75p'][ij],
        "CLIMA_dhr_50p": dfclimas['dhr_50p'][ij],
        "CLIMA_dhr_25p": dfclimas['dhr_25p'][ij],
        "CLIMA_dbt_dia_25p": dfclimas['dbt_dia_25p'][ij],
        "CLIMA_dbt_dia_50p": dfclimas['dbt_dia_50p'][ij],
        "CLIMA_dbt_dia_75p": dfclimas['dbt_dia_75p'][ij],
        "CLIMA_dbt_dia_max": dfclimas['dbt_dia_max'][ij],
        "CLIMA_dbt_dia_mean": dfclimas['dbt_dia_mean'][ij],
        "CLIMA_dbt_dia_min": dfclimas['dbt_dia_min'][ij],
        "CLIMA_dbt_dia_std": dfclimas['dbt_dia_std'][ij],
        "CLIMA_dbt_noite_25p": dfclimas['dbt_noite_25p'][ij],
        "CLIMA_dbt_noite_50p": dfclimas['dbt_noite_50p'][ij],
        "CLIMA_dbt_noite_75p": dfclimas['dbt_noite_75p'][ij],
        "CLIMA_dbt_noite_max": dfclimas['dbt_noite_max'][ij],
        "CLIMA_dbt_noite_mean": dfclimas['dbt_noite_mean'][ij],
        "CLIMA_dbt_noite_min": dfclimas['dbt_noite_min'][ij],
        "CLIMA_dbt_noite_std": dfclimas['dbt_noite_std'][ij],
        "CLIMA_dpt_dia_25p": dfclimas['dpt_dia_25p'][ij],
        "CLIMA_dpt_dia_50p": dfclimas['dpt_dia_50p'][ij],
        "CLIMA_dpt_dia_75p": dfclimas['dpt_dia_75p'][ij],
        "CLIMA_dpt_dia_max": dfclimas['dpt_dia_max'][ij],
        "CLIMA_dpt_dia_mean": dfclimas['dpt_dia_mean'][ij],
        "CLIMA_dpt_dia_min": dfclimas['dpt_dia_min'][ij],
        "CLIMA_dpt_dia_std": dfclimas['dpt_dia_std'][ij],
        "CLIMA_dpt_noite_25p": dfclimas['dpt_noite_25p'][ij],
        "CLIMA_dpt_noite_50p": dfclimas['dpt_noite_50p'][ij],
        "CLIMA_dpt_noite_75p": dfclimas['dpt_noite_75p'][ij],
        "CLIMA_dpt_noite_max": dfclimas['dpt_noite_max'][ij],
        "CLIMA_dpt_noite_mean": dfclimas['dpt_noite_mean'][ij],
        "CLIMA_dpt_noite_min": dfclimas['dpt_noite_min'][ij],
        "CLIMA_dpt_noite_std": dfclimas['dpt_noite_std'][ij],
        "CLIMA_ph_inf_dia": dfclimas['ph_inf_dia'][ij],
        "CLIMA_ph_inf_noite": dfclimas['ph_inf_noite'][ij],
        "CLIMA_ph_sup_dia": dfclimas['ph_sup_dia'][ij],
        "CLIMA_ph_sup_noite": dfclimas['ph_sup_noite'][ij],
        "CLIMA_ts_dia_25p": dfclimas['ts_dia_25p'][ij],
        "CLIMA_ts_dia_50p": dfclimas['ts_dia_50p'][ij],
        "CLIMA_ts_dia_75p": dfclimas['ts_dia_75p'][ij],
        "CLIMA_ts_dia_max": dfclimas['ts_dia_max'][ij],
        "CLIMA_ts_dia_mean": dfclimas['ts_dia_mean'][ij],
        "CLIMA_ts_dia_min": dfclimas['ts_dia_min'][ij],
        "CLIMA_ts_dia_std": dfclimas['ts_dia_std'][ij],
        "CLIMA_ts_noite_25p": dfclimas['ts_noite_25p'][ij],
        "CLIMA_ts_noite_50p": dfclimas['ts_noite_50p'][ij],
        "CLIMA_ts_noite_75p": dfclimas['ts_noite_75p'][ij],
        "CLIMA_ts_noite_max": dfclimas['ts_noite_max'][ij],
        "CLIMA_ts_noite_mean": dfclimas['ts_noite_mean'][ij],
        "CLIMA_ts_noite_min": dfclimas['ts_noite_min'][ij],
        "CLIMA_ts_noite_std": dfclimas['ts_noite_std'][ij],
        "CLIMA_wd_dia_25p": dfclimas['wd_dia_25p'][ij],
        "CLIMA_wd_dia_50p": dfclimas['wd_dia_50p'][ij],
        "CLIMA_wd_dia_75p": dfclimas['wd_dia_75p'][ij],
        "CLIMA_wd_dia_max": dfclimas['wd_dia_max'][ij],
        "CLIMA_wd_dia_mean": dfclimas['wd_dia_mean'][ij],
        "CLIMA_wd_dia_min": dfclimas['wd_dia_min'][ij],
        "CLIMA_wd_dia_std": dfclimas['wd_dia_std'][ij],
        "CLIMA_wd_noite_25p": dfclimas['wd_noite_25p'][ij],
        "CLIMA_wd_noite_50p": dfclimas['wd_noite_50p'][ij],
        "CLIMA_wd_noite_75p": dfclimas['wd_noite_75p'][ij],
        "CLIMA_wd_noite_max": dfclimas['wd_noite_max'][ij],
        "CLIMA_wd_noite_mean": dfclimas['wd_noite_mean'][ij],
        "CLIMA_wd_noite_min": dfclimas['wd_noite_min'][ij],
        "CLIMA_wd_noite_std": dfclimas['wd_noite_std'][ij],
        "CLIMA_ws_dia_25p": dfclimas['ws_dia_25p'][ij],
        "CLIMA_ws_dia_50p": dfclimas['ws_dia_50p'][ij],
        "CLIMA_ws_dia_75p": dfclimas['ws_dia_75p'][ij],
        "CLIMA_ws_dia_max": dfclimas['ws_dia_max'][ij],
        "CLIMA_ws_dia_mean": dfclimas['ws_dia_mean'][ij],
        "CLIMA_ws_dia_min": dfclimas['ws_dia_min'][ij],
        "CLIMA_ws_dia_std": dfclimas['ws_dia_std'][ij],
        "CLIMA_ws_noite_25p": dfclimas['ws_noite_25p'][ij],
        "CLIMA_ws_noite_50p": dfclimas['ws_noite_50p'][ij],
        "CLIMA_ws_noite_75p": dfclimas['ws_noite_75p'][ij],
        "CLIMA_ws_noite_max": dfclimas['ws_noite_max'][ij],
        "CLIMA_ws_noite_mean": dfclimas['ws_noite_mean'][ij],
        "CLIMA_ws_noite_min": dfclimas['ws_noite_min'][ij],
        "CLIMA_ws_noite_std": dfclimas['ws_noite_std'][ij],
        "EPW_Elevation": dfclimas["alt"][ij],
        "EPW_Latitude": dfclimas["lat"][ij]
    }

    return in2clima
