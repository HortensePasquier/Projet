import sys
from itertools import combinations
from gurobipy import Model, GRB

def lire_fichier(file_path):
    #Lit le fichier txt et extrait les photos horizontales et verticales
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
    #Associe les photos verticales par paires 
    utilisee = set()
    paires = []
    for (i1, tags1), (i2, tags2) in combinations(verticales, 2):
        if i1 not in utilisee and i2 not in utilisee:
            combined_tags = tags1 | tags2
            paires.append(((i1, i2), combined_tags))
            utilisee.add(i1)
            utilisee.add(i2)
    return paires

def facteur(tags1, tags2):
    #Calcule le facteur d'intérêt entre 2 diapositives
    commun = len(tags1 & tags2)
    dans_1 = len(tags1 - tags2)
    dans_2 = len(tags2 - tags1)
    return min(commun, dans_1, dans_2)

def optimise(slides):
    #Ordonne les diapositives en maximisant le score total
    if not slides:
        return [], 0

    ordre_slides = [slides.pop(0)]
    photo_utilisee = set(ordre_slides[0][0]) if isinstance(ordre_slides[0][0], tuple) else {ordre_slides[0][0]}
    
    total_score = 0  # Initialisation du score total

    while slides:
        best_next = None
        best_score = -1
        for slide in slides:
            if isinstance(slide[0], tuple):
                if slide[0][0] in photo_utilisee or slide[0][1] in photo_utilisee:
                    continue
            else:
                if slide[0] in photo_utilisee:
                    continue
            
            score = facteur(ordre_slides[-1][1], slide[1])
            if score > best_score:
                best_next = slide
                best_score = score
        
        if best_next:
            ordre_slides.append(best_next)
            slides.remove(best_next)
            if isinstance(best_next[0], tuple):
                photo_utilisee.update(best_next[0])
            else:
                photo_utilisee.add(best_next[0])

            total_score += best_score  # Ajout du score de transition

    return ordre_slides, total_score
    

def solve(photos, verticales):
    #Créé et optimise l'ordre des diapositives, puis calcule le score final
    slides = photos + tri_verticale(verticales)
    slides, total_score = optimise(slides)
    
    solution = [s[0] for s in slides]
    print(f"\nNombre de transitions: {len(solution) - 1}")
    print(f"Score final optimisé : {total_score}\n")  

    return solution, total_score

def ecrire_solution(solution, output_file):
    #Écrit la solution optimisée dans un fichier 
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
    solution, total_score = solve(photos, verticales)
    ecrire_solution(solution, "slideshow.sol")

    print(f" Solution enregistrée dans 'slideshow.sol' avec un score de {total_score} ")
