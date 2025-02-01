import math  

# distribuye serie en una o mas filas dentro del contenedor
# devuelve: container_width_opt, container_height, numero de filas y coordenadas de los sellos dentro del contenedor
# relativas a la esq. izq. superior.

def ubicar_serie_sellos(max_container_width, stamps, min_gaps_x= 0.25, min_gaps_y= 0.5):   # sellos =[ancho, alto, year, valor]

    def efective_width(serie):
        width= 0                      # Ancho con los gaps
        for stamp in serie:
            width += stamp[0] + gaps_x      
        return (width - gaps_x)         # ni a la izq del 1er sello ni a la der del ultimo hay gaps
    
    def row_height(serie):
        height = 0
        for stamp in serie:
            height = max(stamp[1], height)    
        return height        

    def gap_width(serie, container_width):   # para reajustar ancho de fila
        num_sellos = len(serie)
        width = 0
        for j in range(num_sellos):
            width += serie[j][0]  
        gap = ((container_width - width) / (num_sellos-1))    # no al ultimo                
        return gap            
       
    # distribuir la misma cantidad de sellos por fila. Luego ajustar el ancho del contenedor a la fila mas ancha
    # y reajustar los gaps de las otras filas.  
 
    x =container_x_up_left =0               # inicio coordenadas relativas del contenedor. incrementan hacia abajo y derecha
    container_height = container_width =0 
    coordenadas = []  
    gaps_x = min_gaps_x

    num_stamps = len(stamps)  
    rows=  math.ceil(efective_width(stamps) / max_container_width )   # max cnt de filas
    height = 0
 
   
    # ancho optimo del contenedor
    inicio = 0
    cociente, resto = divmod(num_stamps, rows)          # division modular. Resto = lo que resta entre el cociente y num_sellos
    for i in range(rows):
        fin = int(inicio + cociente + (1 if i < resto else 0))              
        tmp= efective_width(stamps[inicio:fin])  # for testing
        container_width = max(container_width, efective_width(stamps[inicio:fin]))  # al final se queda con el ancho de la fila mayor
        inicio = fin

    # repartir sellos y ajustar coordenadas
    fin = inicio = 0  
    for i in range(rows):
        fin = int(inicio + cociente + (1 if i < resto else 0))
        gaps_x = max(min_gaps_x, gap_width(stamps[inicio:fin], container_width))   # si es la fila mas ancha quedan igual
        height += row_height(stamps[inicio:fin])      
        container_height += row_height(stamps[inicio:fin]) + min_gaps_y
        for stamp in stamps[inicio:fin]:                                                             
            coordenadas.append((round(x,2), round(height,2), round(x+ stamp[0],2), round(height- stamp[1],2)))
            x += stamp[0] + gaps_x
        inicio = fin            
        x = container_x_up_left
        height += min_gaps_y

    result=[container_width, container_height, rows, coordenadas]

    return result






#_________________________________________________________________________________________________________________
#   Para probar el resultado de manera visual: 


import tkinter as tk

def visualizar_sellos(container_width, container_height, coordenadas):
    
    window = tk.Tk()
    window.withdraw()      
    contenedor = tk.Toplevel()  # Crea la nueva ventana

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.attributes('-fullscreen', True)
    window.configure(bg="black")

    adp = 0.8
    relacion = container_height* screen_height / container_width 
    while relacion* adp > screen_height:
        adp -= 0.1 

    # container:
    contenedor.title("Contenedor")
    contenedor.geometry(f"{int(screen_height*adp)}x{int(relacion*adp)}+{100}+{20}") 
    contenedor.focus_set()  # Mueve el cursor a la nueva ventana
    x= int(screen_height * adp) 
    y= int(container_height* screen_height / container_width* adp)
    canvas = tk.Canvas(contenedor, width= x, height= y) 
    canvas.pack()
    
    #sellos:
    for x, y, ancho, alto in coordenadas:
        x1= int(x * screen_height / container_width *adp)
        x2= int(ancho * screen_height / container_width *adp)
        y1= int(y * container_height* screen_height / container_width / container_height * adp)
        y2= int(alto * (container_height* screen_height / container_width) / container_height * adp)
        canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="black") 

    window.mainloop()

def generar_lista_sellos(cantidad, min_dim, max_dim, year1, year2, valormax):
    """Para genera una lista de sellos con dimensiones aleatorias para probar."""
    import random
    sellos = []
    lista = []
    for _ in range(cantidad):
        ancho = round(random.uniform(min_dim, max_dim),1)
        alto = round(random.uniform(min_dim, max_dim),1)
        year = random.randint(year1, year2)
        valor = random.randint(1, valormax)
        sellos.append([ancho, alto, year, valor])
    return sellos        # retorna lista sellos =[ancho, alto, year, valor]


def reorganizar_sellos(sellos, criterio):
    
    """ criterio: Una lista que especifica el orden y la dirección del ordenamiento.
                    Para cada elemento del criterio divide la cadena en dos partes:
                    el atributo ("y", "w", "h", "v") y la dirección ("up", "down")
                    Ejemplo: ["y_down", "w_up", "h_down", "v_up"]
        Retorna la tupla reorganizada según el criterio, o None si hay errores. """
    
    if not isinstance(sellos, list) or not all(isinstance(sello, list) and len(sello) == 4 for sello in sellos) or not isinstance(criterio, list) or len(criterio) != 4:
        return None  # Entradas inválidas

    lista_sellos = list(sellos)  # Convierte la tupla a lista
    lista_sellos.sort(key=comparar_sellos)  #Se utiliza el método sort() de la lista
                     # pasando como argumento key=comparar_sellos. De esa manera Sort()
                     # utiliza comparar_sellos() para determinar el orden de los elementos.
    sellos = None
    sellos = tuple(lista_sellos)

    return sellos

def comparar_sellos(sello):
    """Función para comparar sellos según el criterio."""
    valores = []
    for c in criterio:
        orden = c.split("_")
        atributo = orden[0]
        direccion = orden[1]
        if atributo == "w":
            valor = sello[0]
        elif atributo == "h":
            valor = sello[1]
        elif atributo == "y":
            valor = sello[2]
        elif atributo == "v":
            valor = sello[3]
        else:
            return None #criterio invalido
        if direccion == "down":
            valores.append(-valor)  # Invierte el valor para orden descendente
        else:
            valores.append(valor)
    return valores



# ________________PRUEBA:_______________________________________

# ( num de sellos, random alto y ancho, rango años, valor facial)
sellos = generar_lista_sellos(11, 0.8, 1.5, 1901, 1910, 50)   #  retorna lista sellos =[ancho, alto, year, valor]
#sellos = [[1,2,0,0],[2,1,0,0],[1,2,0,0],[2,1,0,0]]

criterio = ["y_down", "w_up", "h_down", "v_up"]  # Ordenar por año descendente, luego ancho ascendente, luego alto descendente y finalmente valor ascendente.
#sellos = reorganizar_sellos(sellos, criterio)   # si es necesario reorganizar serie previo a llamar la funcion 
max_container_width = 6

resultado = ubicar_serie_sellos(max_container_width, sellos)

if resultado:  # container_width_opt, container_height, numero de filas y coordenadas de los sellos dentro del contenedor
    container_width, container_height,rows, coordenadas = resultado     # [container_dim, container_height, rows, coordenadas]
    #for x, y, ancho_sello, alto_sello in coordenadas:
    #   print(f"({x}, {y}, {ancho_sello}, {alto_sello})")
   # generar_pdf("sellos_a4.pdf", container_width, container_height, coordenadas)
    visualizar_sellos(container_width, container_height, coordenadas)


# ___________________________________________________________________________________________________________________________________________________
#____________________________________________________________________________________________________________________________________________________


"""
    def ancho_serie_con_gaps(serie):                 # Devuelve el ancho de una serie (o intervalo) con los gaps
        width = 0                     
        num_sellos = len(serie)
        for pos in range(num_sellos):
            width += serie[pos][0] + min_gap
        width -= min_gap                             # quita el gap del ultimo sello. 
        return width

    def new_gap_width(serie, new_container_width):   # redistribuye la serie dentro del nuevo ancho de contenedor. Retorna new gap_witdh.
        num_sellos = len(serie)
        ancho = 0
        for j in range(num_sellos -1):
            ancho += serie[j][0] 
        gap_width = (new_container_width - ancho) / num_sellos              
        return gap_width

    def max_stamp_heigth(serie):                
        max_heigth = 0
        num_sellos = len(serie)
        for i in range(num_sellos):
            if serie[i][1] > max_heigth: max_heigth = serie[i][1]
        return max_heigth
  
    def ancho_subserie_en_subseries(subseries, fila, indice):              # subseries:{ 'fila': [subserie] }
        ancho = sum(valor[indice] for valor in subseries([fila]))     # indice= pos del valor 'ancho' en la subserie
        return ancho

      
"""
"""   series = []
    init_pos = last_pos = 0 
    row = 1
    num_sellos = len(sellos)
  
    while last_pos < num_sellos:
        while (efective_width(sellos[init_pos: last_pos+1]) <= max_container_width) and last_pos < num_sellos:
           to_lastpos = sellos[init_pos: last_pos+1] 
           last_pos +=1
        series.append(to_lastpos)
        row_heigth = efective_heigth(series[row-1])
        container_width = max(container_width, efective_width(to_lastpos))
        container_height += row_heigth + min_row_gap
        for j in range(init_pos, last_pos):                                                             
            coordenadas.append((round(x,1), round(container_height,1), round(x+ sellos[j][0], 1), round(row_heigth- sellos[j][1],1)))
            x += sellos[j][0] + min_gap
        x = container_x_up_left
        init_pos = last_pos
        rows = row
        row += 1
"""
