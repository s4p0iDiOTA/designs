#import math  

# distribuye en una o mas filas dentro del container
# devuelve: container_width_opt, container_height, numero de filas y coordenadas de los sellos dentro del contenedor
# relativas a la esq. izq. superior.
def ubicar_serie_sellos(max_container_width, sellos, min_gap= 0.25, min_row_gap= 0.5):   # sellos =[ancho, alto, year, valor]

    def efective_width(serie):
        width= 0                      # Ancho con los gaps
        for stamp in serie:
            width += stamp[0] + min_gap
        return width 
    
    def efective_heigth(serie):       # Alto con los gaps
        heigth = 0
        for stamp in serie:
            heigth += stamp[1]
        heigth += min_row_gap   
        return heigth 

    x =container_x_up_left =0     # inicio coordenadas relativas del contenedor. incrementan hacia abajo y derecha
    y =container_y_up_left =0     # modificar para cambiar area de trabajo dentro del contenedor   
    container_height = container_width =0 
 
    coordenadas = []                # coordenadas del sello: x= esq. izq inferior , y= altura del sello mas alto  , ancho, alto
    sub_serie = []
    init_pos = last_pos = 0 
    row = 1
    num_sellos = len(sellos)

    while last_pos < num_sellos:
        to_lastpos = sellos[last_pos: last_pos+1]    
        while (efective_width(to_lastpos)< max_container_width) and last_pos < num_sellos:                
            last_pos +=1 
            to_lastpos = sellos[init_pos: last_pos]                                        
        sub_serie.append(to_lastpos)
        row_heigth = efective_heigth(sub_serie[row-1])
        container_width = max(container_width, efective_width(to_lastpos))
        container_height += row_heigth + min_row_gap
        for j in range(init_pos, last_pos):                                                             
            coordenadas.append((x, container_height, round(x+ sellos[j][0], 1), round(row_heigth- sellos[j][1],1)))
            x += sellos[j][0] + min_gap
        x = container_x_up_left
        init_pos = last_pos+1
        row += 1


# optimizar... distribuir lo mas parejo por filas          
 
    rows = len(sub_serie)
    result=[container_width, container_height, rows, coordenadas]

    return result












#_________________________________________________________________________________________________________________
#   Para probar el resultado de manera visual:
# ________________________________________________________________________________________________________________  



import tkinter as tk

def visualizar_sellos(container_width, container_height, coordenadas):
    def cerrar_window():
        window.destroy
    
   
    window = tk.Tk()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.attributes('-fullscreen', True)

    relacion_x = 80 
    relacion_y = 40

    # container:
   
    canvas = tk.Canvas(window, width= container_width* relacion_x, height= container_height * relacion_y, bg="blue")
    canvas.create_rectangle(0, 0, container_width* relacion_x , container_height* relacion_y, fill= "blue")
    canvas.pack()
    boton = tk.Button(window, text= "cerrar", command= cerrar_window)
    boton.pack

    #window.mainloop()

    #sellos
    for x, y, ancho_sello, alto_sello in coordenadas:
        canvas.create_rectangle(x, y, ancho_sello* relacion_x, alto_sello* relacion_y, fill= "white") 
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


sellos = generar_lista_sellos(12, 0.5, 1.2, 1901, 1910, 50)   #  retorna lista sellos =[ancho, alto, year, valor]
criterio = ["y_down", "w_up", "h_down", "v_up"]  # Ordenar por año descendente, luego ancho ascendente, luego alto descendente y finalmente valor ascendente.
#sellos = reorganizar_sellos(sellos, criterio)   # si es necesario reorganizar serie previo a llamar la funcion 
max_container_width = 6.5

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