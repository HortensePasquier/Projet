from gurobipy import Model, GRB
import sys

def lire_fichier(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    photos = []
    verticales = []
    
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        orientation, tags = parts[0], set(parts[2:])
        if orientation == 'H':
            photos.append((i - 1, tags))
        else:
            verticales.append((i - 1, tags))
    
    return photos, verticales

def tri_verticale(verticales):
    verticales.sort(key=lambda x: len(x[1]))
    paires = []
    while len(verticales) > 1:
        v1 = verticales.pop()
        best_match = min(verticales, key=lambda v: len(v[1] & v1[1]))
        verticales.remove(best_match)
        paires.append(((v1[0], best_match[0]), v1[1] | best_match[1]))
    return paires

def facteur(tags1, tags2):
    commun = len(tags1 & tags2)
    dans_1 = len(tags1 - tags2)
    dans_2 = len(tags2 - tags1)
    return min(commun, dans_1, dans_2)

def solve(photos, verticales):
    slides = photos + tri_verticale(verticales)
    n = len(slides)
    
    model = Model()
    model.setParam('OutputFlag', 0)
    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")
    u = model.addVars(n, vtype=GRB.INTEGER, name="u")
    
    # Chaque diapositive a un unique successeur et un unique prédécesseur
    for i in range(n):
        model.addConstr(sum(x[i, j] for j in range(n) if j != i) == 1, name=f"successeur_{i}")
        model.addConstr(sum(x[j, i] for j in range(n) if j != i) == 1, name=f"predecesseur_{i}")
    
   
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1, name=f"mtz_{i}_{j}")
    
    # Fonction objectif : maximiser le score des transitions
    obj = sum(facteur(slides[i][1], slides[j][1]) * x[i, j] for i in range(n) for j in range(n) if i != j)
    model.setObjective(obj, GRB.MAXIMIZE)
    
    model.write("slideshow.lp")
    model.optimize()

    
   
    # Amélioration de la solution en suivant exactement x[i, j]
    solution = []
    visited = set()
    current = next(i for i in range(n) if sum(x[i, j].X for j in range(n) if j != i) > 0.5)
    total_score = 0
    num_transitions = 0
    
    while len(visited) < n:
        solution.append(slides[current][0])
        visited.add(current)
        
        next_slide = None
        for j in range(n):
            if j not in visited and x[current, j].X > 0.5:
                next_slide = j
                break
        
        if next_slide is None:
            break
        
        total_score += facteur(slides[current][1], slides[next_slide][1])
        num_transitions += 1
        current = next_slide
    
    
    return solution, total_score, num_transitions

def ecrire_solution(solution, output_file, num_transitions):
    with open(output_file, 'w') as f:
        f.write(f"{len(solution)}\n")
        f.write(f"{num_transitions}\n")
        for slide in solution:
            if isinstance(slide, tuple):
                f.write(f"{slide[0]} {slide[1]}\n")
            else:
                f.write(f"{slide}\n")

if __name__ == "__main__":
    dataset_path = sys.argv[1]
    photos, verticales = lire_fichier(dataset_path)
    solution, total_score, num_transitions = solve(photos, verticales)
    ecrire_solution(solution, "slideshow.sol", num_transitions)
    print(f"Solution enregistrée dans 'slideshow.sol' avec un score de {total_score}")
    print(f"Nombre de transitions : {num_transitions}")