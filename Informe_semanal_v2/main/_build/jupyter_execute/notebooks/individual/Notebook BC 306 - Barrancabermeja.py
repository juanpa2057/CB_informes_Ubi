#!/usr/bin/env python
# coding: utf-8

# # BC 306 - Barrancabermeja

# In[1]:


DEVICE_NAME = 'BC 306 - Barrancabermeja'
import warnings
warnings.filterwarnings("ignore")


# In[2]:


import pandas as pd
import numpy as np
import datetime as dt
import json
from datetime import datetime

import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

pio.renderers.default = "notebook"
pio.templates.default = "plotly_white"


# this enables relative path imports
import os
from dotenv import load_dotenv
load_dotenv()
_PROJECT_PATH: str = os.environ["_project_path"]
_PICKLED_DATA_FILENAME: str = os.environ["_pickled_data_filename"]

import sys
from pathlib import Path
project_path = Path(_PROJECT_PATH)
sys.path.append(str(project_path))

import config_v2 as cfg

from library_report_v2 import Cleaning as cln
from library_report_v2 import Graphing as grp
from library_report_v2 import Processing as pro
from library_report_v2 import Configuration as repcfg


# ## Functions

# In[3]:


def show_response_contents(df):
    print("The response contains:")
    print(json.dumps(list(df['variable'].unique()), sort_keys=True, indent=4))
    print(json.dumps(list(df['device'].unique()), sort_keys=True, indent=4))


# ## Preprocessing

# In[4]:


df = pd.read_pickle(project_path / 'data' / _PICKLED_DATA_FILENAME)
df = df.query("device_name == @DEVICE_NAME")
show_response_contents(df)


# In[5]:


df = df.sort_values(by=['variable','datetime'])
df = pro.datetime_attributes(df)

df_bl, df_st = pro.split_into_baseline_and_study(df, baseline=cfg.BASELINE, study=cfg.STUDY, inclusive='left')
df_bl['Periodo'] = 'Baseline'
df_st['Periodo'] = 'Estudio'

past_w = df_bl.loc[cfg.PAST_WEEK[0]:cfg.PAST_WEEK[1]]

# df_cons = df.query("variable == 'front-consumo-activa'")
# df_ea = cln.recover_energy_from_consumption(df_cons, new_varname='front-energia-activa-acumulada')
# df_pa_synth = cln.differentiate_single_variable(df_ea, 'front-potencia-activa-sintetica', remove_gap_data=True)
# df_ea_interp = cln.linearly_interpolate_series(df_ea, data_rate_in_minutes=None)


# In[6]:


df_pa = df.query("variable == 'front-potencia-activa'").copy()
cargas = df_st[df_st["variable"].isin(cfg.ENERGY_VAR_LABELS)].copy()
front = df_st[df_st["variable"].isin(['front-consumo-activa'])].copy()
front_reactiva = df_st[df_st["variable"].isin(['consumo-energia-reactiva-total'])].copy()
factor_potencia = df_st[df_st["variable"].isin(['factor-de-potencia'])].copy()
factor_potencia_bl = df_bl[df_bl["variable"].isin(['factor-de-potencia'])].copy()
demanda_aa = df_st[df_st["variable"].isin(['kw-tr'])].copy()
demanda_aa_bl = df_bl[df_bl["variable"].isin(['kw-tr'])].copy()

front_bl = df_bl[df_bl["variable"].isin(['front-consumo-activa'])].copy()
cargas_bl = df_bl[df_bl["variable"].isin(cfg.ENERGY_VAR_LABELS)].copy()
cargas_bl['Periodo'] = 'Baseline'
cargas['Periodo'] = 'Estudio'


Area = df_bl[df_bl["variable"].isin(['area'])].copy().max().values[0]
TR = df_bl[df_bl["variable"].isin(['tr'])].copy().max().values[0]


front_bl =cln.remove_outliers_by_zscore(front_bl, zscore=4)
df_pa = cln.remove_outliers_by_zscore(df_pa, zscore=4)
cargas = cln.remove_outliers_by_zscore(cargas, zscore=4)
front = cln.remove_outliers_by_zscore(front, zscore=4)
front_reactiva = cln.remove_outliers_by_zscore(front, zscore=4)

past_w_front = past_w[past_w["variable"].isin(['front-consumo-activa'])].copy()


# In[7]:


cargas_hour = cargas.groupby(by=["variable"]).resample(
    '1h').sum().round(2).reset_index().set_index('datetime')
cargas_hour = pro.datetime_attributes(cargas_hour)

cargas_day = cargas.groupby(by=["variable"]).resample(
    '1D').sum().reset_index().set_index('datetime')
cargas_day = pro.datetime_attributes(cargas_day)

cargas_month = cargas.groupby(by=["variable"]).resample(
    '1M').sum().reset_index().set_index('datetime')
cargas_month = pro.datetime_attributes(cargas_month)

front_hour = front.groupby(by=["variable"]).resample(
    '1h').sum().round(2).reset_index().set_index('datetime')
front_hour = pro.datetime_attributes(front_hour)

front_day = front.groupby(by=["variable"]).resample(
    '1D').sum().reset_index().set_index('datetime')
front_day = pro.datetime_attributes(front_day)
front_day['Periodo'] = 'Estudio'

front_day_bl = front_bl.groupby(by=["variable"]).resample(
    '1D').sum().reset_index().set_index('datetime')
front_day_bl = pro.datetime_attributes(front_day_bl)
front_day_bl['Periodo'] = 'Baseline'

front_month = front.groupby(by=["variable"]).resample(
    '1M').sum().reset_index().set_index('datetime')
front_month = pro.datetime_attributes(front_month)

front_month_pw = past_w_front.groupby(by=["variable"]).resample(
    '1M').sum().reset_index().set_index('datetime')
front_month_pw = pro.datetime_attributes(front_month_pw)

front_reactiva_hour = front_reactiva.groupby(by=["variable"]).resample(
    '1h').sum().round(2).reset_index().set_index('datetime')
front_reactiva_hour = pro.datetime_attributes(front_reactiva_hour)


# ## Plots

# In[8]:


df_concat = pd.concat([cargas_day, front_day])

# Crear una columna 'month_day' combinando 'month' y 'day'
df_concat['month_day'] = df_concat['month'].astype(str) + '-' + df_concat['day'].astype(str)

# Ordenar los datos por la columna 'datetime'
df_concat = df_concat.sort_values('datetime')

# Agregamos los valores de las dos variables por month_day
agg_df = df_concat.groupby(['month_day', 'variable'])['value'].sum().reset_index()


# In[9]:


fig = px.bar(
    df_concat,
    x="month_day",
    y="value",
    barmode='group',
    color='variable',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'month_day':'Mes - Día', 'value':'Consumo [kWh]'},
    title=f"{DEVICE_NAME}: Consumo diario de energía activa [kWh]",
)

fig.add_hline(y=front_day_bl['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Línea base: {front_day_bl['value'].mean():.2f} kWh/dia", annotation_position="top left")

# Ajustamos la escala y el formato del eje x
fig.update_xaxes(
    type='category',  # Usar una escala categórica en lugar de fecha
    tickvals=list(agg_df['month_day']),  # Valores en el eje x
    ticktext=list(agg_df['month_day']),  # Etiquetas en el eje x
    title_text='Mes - Día',  # Título del eje x
)

fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)

fig.show()


# In[10]:


front_cons_total = front_month["value"].sum()
front_cons_pw_total = front_month_pw["value"].sum()

dif_mes_anterior = (front_cons_total - front_cons_pw_total) / front_cons_pw_total * 100

"""
if front_cons_total - front_cons_pw_total > 0:
    print(f"El consumo de energía de la semana pasada fue {front_cons_total:.0f}kWh, lo que representa un aumento de {abs(front_cons_total - front_cons_pw_total) :.0f} kWh, un {dif_mes_anterior:.0f} % respecto a la semana anterior.")
else:
    print(f"El consumo de energía de la semana pasada fue {front_cons_total:.0f}kWh, lo que representa una disminución de {abs(front_cons_total - front_cons_pw_total) :.0f} kWh, un {dif_mes_anterior:.0f} % respecto a la semana anterior.")

"""


# In[11]:


fig = px.box(
    pd.concat([front_day_bl, front_day]),
    y="value",
    color='Periodo',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day':'Día', 'value':'Consumo [kWh/dia]'},
    title=f"{DEVICE_NAME}: Consumo típico diario",
    
)

fig.add_hline(y=front_day_bl['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Línea base: {front_day_bl['value'].mean():.2f} kWh/dia", annotation_position="top left")
fig.add_hline(y=front_day['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo semana : {front_day['value'].mean():.2f} kWh/dia", annotation_position="top right")


fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)

fig.show()


if front_day_bl['value'].mean() - front_day['value'].mean() > 0:
    
    print(f"Se evidencia una diferencia del consumo promedio diario de {abs(front_day_bl['value'].mean() - front_day['value'].mean()):.2f} kWh/dia, lo que representa un {abs(front_day_bl['value'].mean() - front_day['value'].mean()) / front_day_bl['value'].mean() * 100:.0f} % de disminución respecto a la línea base.")
else:
    
    print(f"Se evidencia una diferencia del consumo promedio diario de {abs(front_day_bl['value'].mean() - front_day['value'].mean()):.2f} kWh/dia, lo que representa un {abs(front_day_bl['value'].mean() - front_day['value'].mean()) / front_day_bl['value'].mean() * 100:.0f} % de aumento respecto a la línea base.")


# In[12]:


df_front_cargas = pd.concat([cargas, cargas_bl])

front_nighttime_cons = front[front["hour"].isin(cfg.NIGHT_HOURS)].copy()

cargas_nighttime_cons = df_front_cargas[df_front_cargas["hour"].isin(cfg.NIGHT_HOURS)].copy()
cargas_nighttime_cons = pro.datetime_attributes(cargas_nighttime_cons)

cargas_nighttime_cons_bl = cargas_nighttime_cons[cargas_nighttime_cons["Periodo"] == "Baseline"].copy()
cargas_nighttime_cons_st = cargas_nighttime_cons[cargas_nighttime_cons["Periodo"] == "Estudio"].copy()

cargas_nighttime_cons_bl_daily = cargas_nighttime_cons_bl.groupby(by=["variable"]).resample('1D').sum().reset_index().set_index('datetime')
cargas_nighttime_cons_bl_daily = pro.datetime_attributes(cargas_nighttime_cons_bl_daily)
cargas_nighttime_cons_bl_daily['Periodo'] = 'Baseline'

cargas_nighttime_cons_st_daily = cargas_nighttime_cons_st.groupby(by=["variable"]).resample('1D').sum().reset_index().set_index('datetime')
cargas_nighttime_cons_st_daily = pro.datetime_attributes(cargas_nighttime_cons_st_daily)
cargas_nighttime_cons_st_daily['Periodo'] = 'Estudio'


# Crear una columna 'month_day' combinando 'month' y 'day'
cargas_nighttime_cons_st_daily['month_day'] = cargas_nighttime_cons_st_daily['month'].astype(str) + '-' + cargas_nighttime_cons_st_daily['day'].astype(str)
# Ordenar los datos por la columna 'datetime'
cargas_nighttime_cons_st_daily = cargas_nighttime_cons_st_daily.sort_values('datetime')
# Agregamos los valores de las dos variables por month_day
agg_cargas_nighttime_cons_st_daily = cargas_nighttime_cons_st_daily.groupby(['month_day', 'variable'])['value'].sum().reset_index()


if (cargas_nighttime_cons_st_daily.shape[0] > 0):
    fig = px.bar(
        cargas_nighttime_cons_st_daily.reset_index(),
        x="month_day",
        y="value",
        barmode='group',
        color_discrete_sequence=repcfg.FULL_PALETTE,
        labels={'month_day':'Mes - Día', 'value':'Consumo [kWh]'},
        title=f"{DEVICE_NAME}: Consumo nocturno de energía activa AA/Ilu [kWh/día]",
    )

    fig.add_hline(y=cargas_nighttime_cons_bl_daily['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Línea base: {cargas_nighttime_cons_bl_daily['value'].mean():.2f} kWh/día", annotation_position="top left")
    fig.add_hline(y=cargas_nighttime_cons_st_daily['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo semana : {cargas_nighttime_cons_st_daily['value'].mean():.2f} kWh/dia", annotation_position="top right")

    # Ajustamos la escala y el formato del eje x
    fig.update_xaxes(
    type='category',  # Usar una escala categórica en lugar de fecha
    tickvals=list(agg_cargas_nighttime_cons_st_daily['month_day']),  # Valores en el eje x
    ticktext=list(agg_cargas_nighttime_cons_st_daily['month_day']),  # Etiquetas en el eje x
    title_text='Mes - Día',  # Título del eje x
)


    fig.update_layout(
        font_family=repcfg.CELSIA_FONT,
        font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
        font_color=repcfg.FULL_PALETTE[1],
        title_x=repcfg.PLOTLY_TITLE_X,
        width=repcfg.JBOOK_PLOTLY_WIDTH,
        height=repcfg.JBOOK_PLOTLY_HEIGHT
    )

    # fig.update_traces(marker_color=grp.hex_to_rgb(repcfg.FULL_PALETTE[0]))
    fig.show()


# In[13]:


fig = px.box(
    pd.concat([cargas_nighttime_cons_st_daily, cargas_nighttime_cons_bl_daily]),
    y="value",
    color='Periodo',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day':'Día', 'value':'Consumo [kWh/dia]'},
    title=f"{DEVICE_NAME}: Consumo nocturno típico diario",
    
)

fig.add_hline(y=cargas_nighttime_cons_bl_daily['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Línea base: {cargas_nighttime_cons_bl_daily['value'].mean():.2f} kWh/dia", annotation_position="top left")
fig.add_hline(y=cargas_nighttime_cons_st_daily['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo semana: {cargas_nighttime_cons_st_daily['value'].mean():.2f} kWh/dia", annotation_position="top right")

fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)



# In[14]:


total_night_cons = front_nighttime_cons.query("variable == 'front-consumo-activa'")
consumo_nocturno = total_night_cons["value"].sum()

print(f"Durante la semana pasada se consumió un total de {consumo_nocturno:.0f}kWh fuera del horario establecido.")


# In[15]:


total_night_cons = front_nighttime_cons.query("variable == 'front-consumo-activa'")
consumo_nocturno = total_night_cons["value"].sum()

night_cons_percent = 100 * consumo_nocturno / front_cons_total

print(f"El consumo nocturno representó el {night_cons_percent:.1f}% del consumo total")


# In[16]:


cargas_cons_total = cargas_month['value'].sum()
consumo_otros =  front_cons_total - cargas_cons_total

if (consumo_otros < 0):
    consumo_otros = 0

df_pie = cargas_month[['variable','value']].copy()

df_pie.loc[-1] = ['otros', consumo_otros]
df_pie = df_pie.reset_index(drop=True)
df_pie['value'] = df_pie['value'].round(1)


if (df_pie.value >= 0).all():
    fig = px.pie(
        df_pie, 
        values="value", 
        names='variable', 
        hover_data=['value'], 
        labels={'variable':'Carga', 'value':'Consumo [kWh]'},
        title=f"{DEVICE_NAME}: Consumo total de energía activa por carga [kWh]",
        color_discrete_sequence=repcfg.FULL_PALETTE, 
    )

    fig.update_layout(
        font_family=repcfg.CELSIA_FONT,
        font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
        font_color=repcfg.FULL_PALETTE[1],
        title_x=repcfg.PLOTLY_TITLE_X,
        width=repcfg.JBOOK_PLOTLY_WIDTH,
        height=repcfg.JBOOK_PLOTLY_HEIGHT
    )

    fig.update_traces(
        textposition='inside', 
        textinfo='percent', 
        insidetextorientation='radial'
    )

    fig.update(
        layout_showlegend=True
    )

    fig.show()


# In[17]:


df_plot = pd.concat([front_hour, cargas_hour])

list_vars = [
    'front-consumo-activa',
    'aa-consumo-activa',
    'ilu-consumo-activa'
]

alpha = 0.75
fig = go.Figure()
hex_color_primary = repcfg.FULL_PALETTE[0]
hex_color_secondary = repcfg.FULL_PALETTE[1]

idx = 0
for variable in list_vars:
    df_var = df_plot.query("variable == @variable")
    hex_color = repcfg.FULL_PALETTE[idx % len(repcfg.FULL_PALETTE)]
    rgba_color = grp.hex_to_rgb(hex_color, alpha)
    idx += 1

    if (len(df_var) > 0):
        fig.add_trace(go.Scatter(
            x=df_var.index,
            y=df_var.value,
            line_color=rgba_color,
            name=variable,
            showlegend=True,
        ))



fig.update_layout(
    title=f"{DEVICE_NAME}: Consumo de energía activa [kWh]",
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT,
    yaxis=dict(title_text="Consumo Activa [kWh]")
)

fig.update_traces(mode='lines')
# fig.update_xaxes(rangemode="tozero")
fig.update_yaxes(rangemode="tozero")
fig.show()


# In[18]:


df_pa_bl, df_pa_st = pro.split_into_baseline_and_study(df_pa, baseline=cfg.BASELINE, study=cfg.STUDY, inclusive='both')

if (len(df_pa_bl) > 0) & (len(df_pa_st) > 0):
    df_pa_bl_day = (
        df_pa_bl
        .reset_index()
        .groupby(['device_name','variable','hour'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    df_pa_st_day = (
        df_pa_st
        .reset_index()
        .groupby(['device_name','variable','hour'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    grp.compare_baseline_day_by_hour(
        df_pa_bl_day,
        df_pa_st_day,
        title=f"{DEVICE_NAME}: Día típico",
        bl_label="Promedio línea base",
        st_label="Promedio semanal",
        bl_ci_label="Intervalo línea base",
        include_ci=True,
        fill_ci=True
    )


    df_pa_bl_week = (
        df_pa_bl
        .reset_index()
        .groupby(['device_name','variable','cont_dow'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    df_pa_st_week = (
        df_pa_st
        .reset_index()
        .groupby(['device_name','variable','cont_dow'])['value']
        .agg(['median','mean','std','min',pro.q_low,pro.q_high,'max','count'])
        .reset_index()
    )

    grp.compare_baseline_week_by_day(
        df_pa_bl_week,
        df_pa_st_week,
        title=f"{DEVICE_NAME}: Semana típica",
        bl_label="Promedio línea base",
        st_label="Promedio semanal",
        bl_ci_label="Intervalo línea base",
        include_ci=True,
        fill_ci=True
    )


# In[19]:


fig = px.box(
    pd.concat([factor_potencia, factor_potencia_bl]),
    y="value",
    color='Periodo',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day':'Día', 'value':'Factor de potencia'},
    title=f"{DEVICE_NAME}: Factor de potencia",
    
)


fig.add_hline(y=factor_potencia['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo semana: {factor_potencia['value'].mean():.2f}", annotation_position="top right")


fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)


fig.show()

if factor_potencia_bl['value'].mean() > 0.9:
    print(f"Durante la semana pasada, el factor de potencia promedio estuvo en {factor_potencia_bl['value'].mean():.2f}, lo que representa un consumo normal de energía reactiva.")
else:
    print(f"Durante la semana pasada, el factor de potencia promedio estuvo en {factor_potencia_bl['value'].mean():.2f}")
    print("lo que representa un consumo alto de energía reactiva, esto podría representar penalidades por parte del comercializador de energía.")


# In[20]:


fig = px.box(
    pd.concat([demanda_aa, demanda_aa_bl]),
    y="value",
    color='Periodo',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day':'Día', 'value':'Demanda [kW/TR]'},
    title=f"{DEVICE_NAME}: Demanda del sistema de AA (kW/TR)",
    
)

fig.add_hline(y=demanda_aa['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo semana: {demanda_aa['value'].mean():.2f}", annotation_position="top right")


fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)


fig.show()

print(f"Durante la semana pasada, la demanda del sistema de AA estuvo en promedio en  {demanda_aa['value'].mean():.2f} kW/TR")
print(f"lo que representa un factor de uso del {(demanda_aa['value'].mean()/demanda_aa_bl['value'].max())*100:.2f}% respecto a la máxima demanda histórica.")


# In[21]:


# print(f"El sistema de AA de esta sede fue diseñado pensando en {TR/Area:.2f} TR/m2, por lo que la demanda actual es {(demanda_aa['value'].mean()/(TR/Area)):.2f} veces mayor a la demanda proyectada.")



# In[22]:


consumo_aa = df_st[df_st['variable']=='aa-consumo-activa']
consumo_aa_bl = df_bl[df_bl['variable']=='aa-consumo-activa']

consumo_aa_box =pd.concat([consumo_aa, consumo_aa_bl])
consumo_aa_box_diario =consumo_aa_box.groupby(by=["variable"]).resample('D').sum().round(2).reset_index().set_index('datetime')
consumo_aa_box_diario = pro.datetime_attributes(consumo_aa_box_diario)
consumo_aa_box_diario_bl, consumo_aa_box_diario_st = pro.split_into_baseline_and_study(consumo_aa_box_diario, baseline=cfg.BASELINE, study=cfg.STUDY, inclusive='both')
consumo_aa_box_diario_bl['Periodo'] = 'Baseline'
consumo_aa_box_diario_st['Periodo'] = 'Estudio'


fig = px.box(
    pd.concat([consumo_aa_box_diario_bl, consumo_aa_box_diario_st]),
    y="value",
    color='Periodo',
    color_discrete_sequence=repcfg.FULL_PALETTE,
    labels={'day':'Día', 'value':'Consumo [kWh/día]'},
    title=f"{DEVICE_NAME}: Distribución del consumo del sistema de AA (kWh/día)",
    
)


fig.add_hline(y=consumo_aa_box_diario_st['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo semana: {consumo_aa_box_diario_st['value'].mean():.2f}", annotation_position="top right")
fig.add_hline(y=consumo_aa_box_diario_bl['value'].mean(), line_dash="dash", line_color=repcfg.FULL_PALETTE[1], annotation_text=f"Consumo línea base: {consumo_aa_box_diario_bl['value'].mean():.2f}", annotation_position="top left")


fig.update_layout(
    font_family=repcfg.CELSIA_FONT,
    font_size=repcfg.PLOTLY_TITLE_FONT_SIZE,
    font_color=repcfg.FULL_PALETTE[1],
    title_x=repcfg.PLOTLY_TITLE_X,
    width=repcfg.JBOOK_PLOTLY_WIDTH,
    height=repcfg.JBOOK_PLOTLY_HEIGHT
)


fig.show()


# In[23]:


print( f"Esta sede fue diseñada con un sistema de aa de {TR} TR, lo que representa una distribución por área de {TR/Area:.2f} TR/m2.")

