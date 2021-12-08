from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
import numpy as np
import networkx as nx
from Funciones import crear_tabla_tipo_cambio, extraer_edge_list_log, extraer_edge_list, search_negative_cycles_log_sum, search_positive_cycles_mul 


if __name__=='__main__':

    tickers = ['XRP', 'BTC', 'ETH', 'USDT', 'USDC', 'ADA', 'BNB', 'LTC', 'NEO', 'SOL']
    tabla_df = pd.DataFrame()
    edge_list_FX = []
    Arb_op = []

    crear_tabla_tipo_cambio(tabla_df= tabla_df,
    tickers=tickers,
    apikey='',
    secret_key='')

    extraer_edge_list(df= tabla_df, edge_list= edge_list_FX)
    
    # Creamos la Red
    G_FX = nx.Graph()
    # añadimos los nodos y los pesos
    G_FX.add_weighted_edges_from(edge_list_FX)

    search_positive_cycles_mul(G_FX, Aux=Arb_op)

    
    print("los edges son:", edge_list_FX)
    print("las oportunidades Son:", Arb_op)




