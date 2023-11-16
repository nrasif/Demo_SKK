from dash import Dash, html
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
from dash_iconify import DashIconify
import dash_ag_grid as dag

from ...data.source import DataSource
# from ..production_performance.multiselect_helper import to_multiselect_options
from .. import ids, cns


def render(app: Dash, source: DataSource) -> html.Div:
    @app.callback(
        Output(ids.PREVIEW_DATA_TABLE, "rowData"),
        Output(ids.PREVIEW_DATA_TABLE, "columnDefs"),
        Input(ids.SELECT_DATA_SEGCONTROL, "value"),
    )
    def create_table(data: str):

        df_production = source.df_production
        df_log = source.df_log
        gdf_blocks = source.gdf_blocks
        gdf_wells = source.gdf_wells
        
        production_columns = df_production.drop(columns=["MOVING_AVERAGE", "MOVING_AVERAGE_OIL", "MOVING_AVERAGE_WI", "WATER_CUT_DAILY", "GAS_OIL_RATIO"]).columns.to_list()
        log_columns = df_log.columns.to_list()
        blocks_columns = gdf_blocks.drop(columns=["tooltip","popup","geometry"]).columns.to_list()
        wells_columns = gdf_wells.drop(columns=["tooltip","popup","geometry"]).columns.to_list()
        
        if data == "data_production":
            return df_production.to_dict("records"), [{"field": i} for i in production_columns]
        
        elif data == "data_log":
            return df_log.to_dict("records"), [{"field": i} for i in log_columns]
        
        elif data == "geodata_blocks":
            return gdf_blocks.drop(columns=["tooltip","popup","geometry"]).to_dict("records"),[{"field": i} for i in blocks_columns]
        
        elif data == "geodata_wells":
            return gdf_wells.drop(columns=["tooltip","popup","geometry"]).to_dict("records"),[{"field": i} for i in wells_columns]
        
        else:
            pass
        
        
    return html.Div(
        html.Div(
            className=cns.OVW_PREVIEW_DATA_CONTAINER,
            children=[
                html.H2("Preview Data Table",
                        className=cns.GNG_GRAPH_TITLE),
                dmc.SegmentedControl(
                    id=ids.SELECT_DATA_SEGCONTROL,
                    className=cns.OVW_SELECT_DATA_SEGCONTROL,
                    value="data_production",
                    data=[
                        {"value": "data_production", "label": "Production Data"},
                        {"value": "data_log", "label": "Log Data"},
                        {"value": "geodata_blocks", "label": "Blocks Data"},
                        {"value": "geodata_wells", "label": "Wells Data"},
                    ],
                    mt=10,
                ),
                dag.AgGrid(
                    id=ids.PREVIEW_DATA_TABLE,
                    className=cns.OVW_PREVIEW_DATA_TABLE,
                    defaultColDef={
                        "resizeable": True,
                        "sortable": True,
                        "filter": True,
                    },
                    dashGridOptions={"pagination": True},
                ),
            ],
        ),
    )
