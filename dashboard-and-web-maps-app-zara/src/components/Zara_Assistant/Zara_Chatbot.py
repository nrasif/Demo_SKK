from dash import Dash, html, Input, Output, ctx, State, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from ...data.source import DataSource
from ...components import ids, cns
from ...components.Zara_Assistant import openai_api_key

import pandas as pd
import time

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

import chartgpt as cg

from io import StringIO

openai_api_key = openai_api_key.KEY
llm = OpenAI(api_token=openai_api_key)

conv_hist = []

def contains_word(text, word_list):
    for word in word_list:
        if text.find(word) != -1:
            return True
    return False

word_list = ['table', 'summary', 'summerize', 'rangkum', 'rangkuman']
plot_list = ['plot']

def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table

def render(app: Dash, source: DataSource) -> html.Div:
    
    @app.callback(
        Output(ids.RESPONSE_CHAT, 'children'),
        Input(ids.ZARA_SUBMIT_BUTTON, 'n_clicks'),
        State(ids.ZARA_CHAT_AREA, 'value'),
        Input(ids.MEMORY_OUTPUT, 'data')
    )
    
    def update_convo(n, human_prompt, data_chosen):
        button_click = ctx.triggered_id
        global conv_hist
        
        if button_click == ids.ZARA_SUBMIT_BUTTON:
            time.sleep(1)
            
            if contains_word(human_prompt.lower(), word_list):
                call_API = SmartDataframe(data_chosen, config={'llm':llm})
                chatbot_resp = call_API.chat(human_prompt)
                
                bot_table_output = f"{chatbot_resp}"
                df_ = pd.read_csv(StringIO(bot_table_output), delim_whitespace=True, header=0, index_col=0)
                df_ = df_.transpose()
                df_.reset_index(inplace=True)
                
                final_table = dmc.Table(create_table(df_))
                
                whole_div = html.Div(children=[
                    dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=30), color='gray', radius='xl', size='30px', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className=cns.ZARA_PROFILE_GRID),
                                                    dmc.Col(html.Div(dmc.Text(human_prompt,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div'),
                    dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:face-agent", width=30), color='blue', radius='xl', size='30px', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className=cns.ZARA_PROFILE_GRID),
                                                    dmc.Col(html.Div([final_table]), className='grid-chat-for-table')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div')
                ])
                
                conv_hist.append(whole_div)
                
                return conv_hist
            
            elif contains_word(human_prompt.lower(), plot_list):
                dfchart = pd.DataFrame(data_chosen)
                chart = cg.Chart(dfchart, api_key=openai_api_key)
                fig = chart.plot(human_prompt, return_fig=True)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                graph_bot = dcc.Graph(figure=fig)

                whole_div = html.Div(children=[
                    dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=30), color='gray', radius='xl', size='30px', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className=cns.ZARA_PROFILE_GRID),
                                                    dmc.Col(html.Div(dmc.Text(human_prompt,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div'),
                    dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:face-agent", width=30), color='blue', radius='xl', size='30px', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className=cns.ZARA_PROFILE_GRID),
                                                    dmc.Col(html.Div(graph_bot), className='grid-chat-for-table')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div')
                    ])
                
                conv_hist.append(whole_div)
                
                return conv_hist
            
            else:
                call_API = SmartDataframe(data_chosen, config={'llm':llm})
                chatbot_resp = call_API.chat(human_prompt)
                
                whole_div = html.Div(children=[
                    dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=30), color='gray', radius='xl', size='30px', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className=cns.ZARA_PROFILE_GRID),
                                                    dmc.Col(html.Div(dmc.Text(human_prompt,style={'text-align':'left', 'font-weight':700})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div'),
                    dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:face-agent", width=30), color='blue', radius='xl', size='30px', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className=cns.ZARA_PROFILE_GRID),
                                                    dmc.Col(html.Div(dmc.Text(chatbot_resp,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div')
                ])

                conv_hist.append(whole_div)

                return conv_hist
    
        else:
            return None


    return html.Div(
        className=cns.ZARA_CHAT_INPUT,
        children=[
            dmc.Textarea(
                className=cns.ZARA_CHAT_AREA,
                id=ids.ZARA_CHAT_AREA,
                placeholder='Write your question here...',
                autosize=False,
                minRows=2,
                maxRows=2,
                variant='default',
                radius='lg',
                debounce=True
            ),
            html.Div(className=cns.ZARA_SUBMIT_BUTTON,
                     children=[
                         dmc.ActionIcon(
                             DashIconify(icon='formkit:submit', width=25),
                             id=ids.ZARA_SUBMIT_BUTTON,
                             radius='md',
                             size=60,
                             variant='subtle',
                             color='gray',
                             n_clicks=0
                         )
                     ])
        ]
    )