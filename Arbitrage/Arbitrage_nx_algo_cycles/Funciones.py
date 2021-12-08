from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
import numpy as np
import networkx as nx

def crear_tabla_tipo_cambio(tabla_df, tickers, apikey, secret_key):
    ### Esta funcion nos permite crear un DataFrame que contiene como columnas e indices los tickers y en el cuerpo
    ### contiene los tipos de cambio entre estas monedas (considerando la conversion, indice -> columna)
    ### retorna tabla_df
    
    client = Client(apikey, secret_key) #iniciamos el cliente de binance
    
    tipo_cambio = client.get_all_tickers() #obtenemos los datos de binance, estos estan de la forma "{'symbol': 'ETHBTC', 'price': '0.08344700'}"
    tipo_cambio_df = pd.DataFrame(tipo_cambio)
    tipo_cambio_df.set_index('symbol', inplace=True)
    
    table = np.zeros((len(tickers),len(tickers))) # creamos una matriz cuadrada vacia con el tamaño que calce el numero de tickers
    np.fill_diagonal(table, 1) # dado que es una matriz cuadrada de tipo de cambio, la diagonal debe ser de unos (debemos llenarla nosotros porque en los datos no existen pares identicos)
    tabla_df = pd.DataFrame(data = table, index = tickers, columns = tickers)  # creamos la tabla en un data frame

    # El siguiente loop ingresar los datos en el dataframe (tabla_df)
    # Para esto debemos buscar la combinacion de tickers y asignar a los valores correpsondientes a cada par de monedas

    for i in range(len(tickers)):
        
        for a in range(len(tickers)):
            
            for b in range(len(tipo_cambio_df.index)):
                
                if (tabla_df.columns[i] + tabla_df.index[a]) == tipo_cambio_df.index[b]:
                    tabla_df.loc[tabla_df.index[a], tabla_df.columns[i]] = tipo_cambio_df.iloc[b][0]
                
                elif (tabla_df.index[a] + tabla_df.columns[i]) == tipo_cambio_df.index[b]:
                    tabla_df.loc[tabla_df.columns[i], tabla_df.index[a]] = tipo_cambio_df.iloc[b][0]
        
                else:
                    continue

    # A continuacion vamos a utilizar operaciones matematicas por ende requerimos que los datos sea numericos
    tabla_df = tabla_df._convert(numeric=True)
    # Este segundo loop  nos permite completar la simetria de nuestra tabla de tipo de cambio, puesto que algunos pares pueden estar al reves.
    
    for i in range(len(tickers)): #row
        
        for a in range(len(tickers)): #column
            
            if (tabla_df.iloc[i,a] == 0 and tabla_df.iloc[a,i] != 0 and i > a):
                tabla_df.iloc[i,a] = 1/tabla_df.iloc[a,i]

            elif (tabla_df.iloc[a,i] == 0 and tabla_df.iloc[i,a] != 0) and a > i:
                tabla_df.iloc[a,i] = 1/tabla_df.iloc[i,a]
            
            else:
                continue



#--------------------------------------------------------------------------------------------------------------------------------


def extraer_edge_list_log(df, edge_list):
    ### Esta funcion recibe un data frame de n X n con la info sobre le tipo de cambio y una lista vacia para guardar los valores  los edges y los nodos corrspondientes de la forma:
    ### return: ('XRP', 'BTC', 1.652e-05) donde el peso esta en -log()
    for row in range(len(df)): #estamo trabajando con una matriz cuadrada
        for column in range(len(df)):
            edge_list.append((df.index[row], df.columns[column], -np.log(df.iloc[row, column]))) #creamos un tuple de la forma (tikr1, tikr2, pesos de su conexion que corresponde al tipo de cambio en forma log())
            edge_list.append((df.index[column], df.columns[row], 1/(-np.log(df.iloc[row, column])))) #creamos un tuple de la forma (tikr2, tikr1, pesos de su conexion que corresponde al tipo de cambio en forma log())



#--------------------------------------------------------------------------------------------------------------------------------


def extraer_edge_list(df, edge_list):
    ### Esta funcion recibe un data frame de n X n con la info sobre le tipo de cambio y una lista vacia para guardar los valores  los edges y los nodos corrspondientes de la forma:
    ### return: ('XRP', 'BTC', 1.652e-05) donde el peso esta numeric/float64
    for row in range(len(df)): #estamo trabajando con una matriz cuadrada
        for column in range(len(df)):
            edge_list.append((df.index[row], df.columns[column], (df.iloc[row, column]))) #sin el log para poder realizar algunas operaciones
            edge_list.append((df.index[column], df.columns[row], 1/(df.iloc[row, column])))

#--------------------------------------------------------------------------------------------------------------------------------


def search_negative_cycles_log_sum(G, Aux):
    # Recibe un objeto Graph (G) al cual tiene los pesos de sus edges en formato -log() y una variable AUX para exportar nuestro hallazgos 
    # y calcula los cycles que poseen Oportunidad de arbitrage
    cycle_list = nx.algorithms.cycles.minimum_cycle_basis(G)
    for i in cycle_list:
        if len(i) > 2:
            cycle_sum = 0
            cycle_sum = [G.get_edge_data(i[b], i[b+1])['weight'] if (b < len(i)-1) else G.get_edge_data(i[-1], i[0])['weight'] for b in range(len(i))]
            cycle_sum = np.sum(cycle_sum)
            if cycle_sum < 0:
                Aux.append((cycle_sum, i))
                
        else:
            continue


#--------------------------------------------------------------------------------------------------------------------------------
    
        
def search_positive_cycles_mul(G, Aux):
    # Recibe un objeto Graph (G) al cual tiene los pesos de sus edges en formato numerico y una variable AUX para exportar nuestro hallazgos
    # calcula los cycles que poseen Oportunidad de arbitrage
    cycle_list = nx.algorithms.cycles.minimum_cycle_basis(G)
    for i in cycle_list:
        if len(i) > 2:
            cycle_mul = 0
            cycle_mul = [G.get_edge_data(i[b], i[b+1])['weight'] if (b < len(i)-1) else G.get_edge_data(i[-1], i[0])['weight'] for b in range(len(i))]
            print("chek funcion", cycle_mul, i)
            cycle_mul = np.prod(cycle_mul)
            if cycle_mul > 1:
                Aux.append((cycle_mul, i))
                
        else:
            continue