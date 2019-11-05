# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import time

app = dash.Dash()

app.title = 'Dashboard for material_analysis'

app.layout = html.Div(
    html.Div([
        html.Div([
            html.H1(children=u'原料预估销量误差统计平台',
                    className = "nine columns")
        ], className = "row"),

        html.Div(
            [
                html.Div(
                    [
                        html.P('输入原料编码进行初始化:'),
                        dcc.Input(
                            id='material_code',
                            placeholder='Enter a value...',
                            type='text',
                            value='1000004'
                        ),
                        html.Button('Submit_and_initialize', id='Submit_and_initialize'),
                        html.Div(
                            id='init_state',
                            children='页面首次刷新, 请输入原料点击提交进行初始化...'
                        ),
                    ],
                    className='six columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        html.P('输入微仓信息:'),
                        dcc.Input(
                            id='warehouse_code',
                            placeholder='微仓编码',
                            type='text',
                            value=''
                        ),
                        dcc.Input(
                            id='central_warehouse_code',
                            placeholder='大仓编码',
                            type='text',
                            value='cwh'
                        ),
                        html.Button('Submit(warehouse_code/central_warehouse_code)', id='Submit'),
                    ],
                    className='six columns',
                    style={'margin-top': '20'}
                ),
            ], className="row"
        ),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='example-graph'
                )
            ], className = 'six columns',
            style={'height': 1000})
        ], className = "row")
    ], className='ten columns offset-by-one')
)    

@app.callback(dash.dependencies.Output('init_state','children'),
    [dash.dependencies.Input('Submit_and_initialize', 'n_clicks')],
    [dash.dependencies.State('material_code', 'value')
    ])
def initailize_data(n_clicks, material_code):
    print('原料编码:',material_code, '点击次数n_clicks:',n_clicks)
    global raw_data
    a = time.time()
    if n_clicks == None:
        rint('-----------页面首次刷新-----------')
        return '页面首次刷新, 请输入原料点击提交进行初始化...'
    elif n_clicks >= 1:
        raw_data = generate_data(material_code) #所有大仓的这个原料的过去30天销量/load
        print('-----------完成数据初始化-----------')
    if raw_data.shape[0]>0:
        return '初始化成功, 耗时{:.4}s'.format(time.time()-a)
    else:
        return '初始化失败，请输入正确的原料编码并重试'

@app.callback(
    dash.dependencies.Output('example-graph', 'figure'),
    [dash.dependencies.Input('Submit', 'n_clicks')],
    [dash.dependencies.State('warehouse_code', 'value'),
     dash.dependencies.State('central_warehouse_code', 'value')
    ])
def update_graph_src(n_clicks, warehouse_code, central_warehouse_code):
    print('运行时间:',time.asctime(),'微仓编码:',warehouse_code,'大仓编码',central_warehouse_code)
    plot_data = []
    try: 
        material_code = raw_data.material_code.values[0]
    except: 
        material_code = ''

    if len(warehouse_code)>1 and len(central_warehouse_code)>1:
        return {'layout': {'title': '***微仓编码和大仓编码只能填写一项***'}}
    elif len(warehouse_code)==0 and len(central_warehouse_code)==0:
        return {'layout': {'title': '***微仓编码和大仓编码需选填一项***'}}
    elif len(central_warehouse_code)==0:
        df_data = raw_data[raw_data.warehouse_code==warehouse_code]
        print(df_data.shape)
        if df_data.shape[0]==0:
            return {'layout': {'title': '***该微仓数据不存在***'}}
        title = '微仓原料 {} {}'.format(warehouse_code,material_code)
    elif len(warehouse_code)==0:
        df_data = raw_data[raw_data.central_warehouse_code==central_warehouse_code]
        df_data = df_data.groupby(['ptdate','material_code','central_warehouse_code']).sum().reset_index()
        if df_data.shape[0]==0:
            return {'layout': {'title': '***该大仓数据不存在***'}}
        title = '大仓原料 {} {}'.format(central_warehouse_code,material_code)

    print('data is ready')
    xy = df_data.sort_values(['ptdate']) 
    x = list(xy.ptdate)
    y1 = list(xy.theory_sale_cnt)
    y2 = list(xy.pre_sale_num_l1)
    y3 = list(xy.fact_still_cnt)
    y4 = list(xy.today_can_still_cnt)
    plot_data.append({'x': x, 'y': y1, 'type': 'line', 'name': '理论销量'})
    plot_data.append({'x': x, 'y': y2, 'type': 'line', 'name': '预估销量'})
    plot_data.append({'x': x, 'y': y3, 'type': 'line', 'name': '实际今日还能'})
    plot_data.append({'x': x, 'y': y4, 'type': 'line', 'name': '预估今日还能'})

    figure = {
        'data': plot_data,
        'layout': {
            'title': title,
            'xaxis': dict(
                title=u'日期',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=20,
                    color='#7f7f7f'
                    )
                ),
            'yaxis': dict(
                title=u'销量',
                titlefont=dict(
                    family='Helvetica, monospace',
                    size=20,
                    color='#7f7f7f'
                    )
                )
        }
    }

    return figure

def generate_data(material_code):
    time.sleep(10)
    data = pd.DataFrame([
        ['2019-10-01','1000004','wh1','cwh',1,2,3,4,5,1],
        ['2019-10-02','1000004','wh1','cwh',2,5,2,7,0,1],
        ['2019-10-03','1000004','wh1','cwh',4,3,3,2,7,1],
        ['2019-10-04','1000004','wh1','cwh',1,2,5,4,9,3],
        ['2019-10-01','1000002','wh1','cwh',1,2,3,4,5,1],
        ['2019-10-02','1000002','wh1','cwh',2,5,2,7,0,1],
        ['2019-10-03','1000002','wh1','cwh',4,3,3,2,100,1],
        ['2019-10-04','1000002','wh1','cwh',1,2,5,4,9,3],
        ['2019-10-01','1000004','wh2','cwh',1,2,3,4,5,1],
        ['2019-10-02','1000004','wh2','cwh',2,5,2,7,0,1],
        ['2019-10-03','1000004','wh2','cwh',4,3,3,2,7,1],
        ['2019-10-04','1000004','wh2','cwh',2,2,20,17,9,3],
        ['2019-10-01','1000002','wh2','cwh',4,2,3,4,10,1],
        ['2019-10-02','1000002','wh2','cwh',5,6,2,7,13,1],
        ['2019-10-03','1000002','wh2','cwh',7,3,3,10,18,1],
        ['2019-10-04','1000002','wh2','cwh',20,10,19,21,17,4],
        ],
        columns=['ptdate','material_code','warehouse_code','central_warehouse_code'\
        ,'theory_sale_cnt','pre_sale_num_l1','fact_still_cnt','today_can_still_cnt','Ottawa','Montreal']
    )
    return data[data.material_code==material_code]

raw_data = pd.DataFrame(columns=['ptdate','material_code','warehouse_code','central_warehouse_code'\
        ,'theory_sale_cnt','pre_sale_num_l1','fact_still_cnt','today_can_still_cnt'])


if __name__ == '__main__':
    app.run_server(debug=False,host='127.0.0.1',port='8051')