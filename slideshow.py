from gurobipy import Model, GRB
import sys

def lire_fichier(file_path):
    # Lit le fichier txt et extrait les photos horizontales et verticales
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    photos = []
    verticales = []
    
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        orientation, tags = parts[0], set(parts[2:])
        if orientation == 'H':
            photos.append((i - 1, tags))  # Photos horizontales
        else:
            verticales.append((i - 1, tags))  # Photos verticales
    
    return photos, verticales

def tri_verticale(verticales):
    # Associe les photos verticales en minimisant le coût 
    verticales.sort(key=lambda x: len(x[1]))  # Trier par nombre de tags croissant
    paires = []
    while len(verticales) > 1:
        v1 = verticales.pop()
        best_duo = min(verticales, key=lambda v: len(v[1] & v1[1]))
        verticales.remove(best_duo)
        paires.append(((v1[0], best_duo[0]), v1[1] | best_duo[1]))
    return paires

def facteur(tags1, tags2):
    # Calcule le facteur d'intérêt entre 2 diapositives
    commun = len(tags1 & tags2)
    dans_1 = len(tags1 - tags2)
    dans_2 = len(tags2 - tags1)
    return min(commun, dans_1, dans_2)

def solve(photos, verticales):
    slides = photos + tri_verticale(verticales)
    n = len(slides)
    
    model = Model()

    model.setParam('OutputFlag', 0)
    x = model.addVars(n, n, vtype=GRB.BINARY)
    
    # Chaque diapositive a un successeur
    for i in range(n):
        model.addConstr(sum(x[i, j] for j in range(n) if j != i) == 1)
    
    # Chaque diapositive a un prédécesseur
    for j in range(n):
        model.addConstr(sum(x[i, j] for i in range(n) if i != j) == 1)
    
    # Fonction objectif : maximiser la somme des scores des transitions
    obj = sum(facteur(slides[i][1], slides[j][1]) * x[i, j] for i in range(n) for j in range(n) if i != j)
    model.setObjective(obj, GRB.MAXIMIZE)
    
    model.optimize()
    
    solution = []
    num_transitions = -1  # Compteur pour le nombre de transitions
    
    for i in range(n):
        for j in range(n):
            if x[i, j].X > 0.5:
                solution.append(slides[i][0])
                num_transitions += 1  # Incrémenter le compteur pour chaque transition
                break
    
    return solution, model.objVal, num_transitions  # Retourner le nombre de transitions

def ecrire_solution(solution, output_file):
    # Écrit la solution optimisée dans un fichier 
    with open(output_file, 'w') as f:
        f.write(f"{len(solution)}\n")
        for slide in solution:
            if isinstance(slide, tuple):
                f.write(f"{slide[0]} {slide[1]}\n")
            else:
                f.write(f"{slide}\n")

if __name__ == "__main__":
    dataset_path = sys.argv[1]
    photos, verticales = lire_fichier(dataset_path)
    solution, total_score, num_transitions = solve(photos, verticales)
    ecrire_solution(solution, "slideshow.sol")
    print(f"Solution est enregistrée dans 'slideshow.sol' avec un score de {total_score}")
    print(f"Nombre de transitions : {num_transitions}")  # Afficher le nombre de transitions
