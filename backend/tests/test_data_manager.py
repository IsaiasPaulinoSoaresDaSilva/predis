from backend.data_management.data_manager import DataManager


def test_get_combined_data_for_known_region_has_expected_columns():
    df = DataManager().get_combined_data('leste')
    assert not df.empty
    for col in ['data', 'precipitacao_mm', 'nivel_rio_m',
                'previsao_chuva_d1', 'previsao_chuva_d2', 'previsao_chuva_d3']:
        assert col in df.columns


def test_get_combined_data_unknown_region_falls_back_to_default():
    df_unknown = DataManager().get_combined_data('atlantida-perdida')
    df_default = DataManager().get_combined_data('default')
    assert not df_unknown.empty
    assert len(df_unknown) == len(df_default)


def test_get_combined_data_all_sjc_regions_are_non_empty():
    dm = DataManager()
    for region_id in ['centro', 'norte', 'sul', 'leste', 'oeste', 'sudeste']:
        df = dm.get_combined_data(region_id)
        assert not df.empty, f"DataManager retornou vazio para '{region_id}'"
