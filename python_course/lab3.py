class FigureError(Exception):
    pass

class TriangleError(FigureError):
    def __init__(self, message, figure_id):
        self.figure_id = figure_id
        super().__init__(message) 

class PentagonError(FigureError):
    def __init__(self, message, figure_id):
        self.figure_id = figure_id
        super().__init__(message)

#формула шнурков по точкам
def polygon_area(verticles):
    n = len(verticles)
    area = 0

    for i in range(n):
        x1, y1 = verticles[i]
        x2, y2 = verticles[(i+1)%n]

        area += x1*y2 - x2*y1
    return abs(area)/2

class Triangle:

    def __init__(self, id, vertices):
        if len(vertices) != 3:
            raise TriangleError("Треугольник должен иметь 2 вершины", f"ID: {id}")
        
        if polygon_area(verticles) <= 0:
            raise TriangleError("Такого треугольника не существует", f"ID: {id}")
        self.id = id
        self.vertices = vertices
    
    def move(self, deltax, deltay):
        new_vertices = []

        for x, y in self.vertices:
            new_vertices.append((x + deltax, y+deltay))
        
        self.vertices = new_vertices

class Pentagon:
    def __init__(self, id, vertices):
        if len(vertices) != 5:
            raise PentagonError("Пятиугольник должен иметь 5 вершин", f"ID: {id}")
        
        if polygon_area(verticles) <= 0:
            raise PentagonError("Такого пятиугольника не существует", f"ID: {id}")
        self.id = id
        self.vertices = vertices
    
    def move(self, deltax, deltay):
        new_vertices = []

        for x, y in self.vertices:
            new_vertices.append((x+deltax, y+deltay))
        
        self.vertices = new_vertices


def is_intersect(T1, T2):
    xs1 = [x for x, y in T1.vertices]
    ys1 = [y for x, y in T1.vertices]

    xs2 = [x for x, y in T2.vertices]
    ys2 = [y for x, y in T2.vertices]

    minx1 = min(xs1)
    maxx1 = max(xs1)
    miny1 = min(ys1)
    maxy1 = max(ys1)

    minx2 = min(xs2)
    maxx2 = max(xs2)
    miny2 = min(ys2)
    maxy2 = max(ys2)

    if maxx1 < minx2 or maxx2 < minx1:
        return False
    if maxy1 < miny2 or maxy2 < miny1:
        return False
    
    return True


try:

    tr = Triangle(
        "T1",
        [(0,0), (4,0), (2,3)]
    )

    pen = Pentagon(
        "P1",
        [(1,1), (5,1), (6,3), (3,5), (1,3)]
    )

    print("Triangle:", tr.vertices)
    print("Pentagon:", pen.vertices)


    tr.move(1,1)
    pen.move(3, 4)

    print("\n После мува:")
    print(tr.vertices)
    print(pen.vertices)


    print("\nПересечение:", is_intersect(tr, pen))


except TriangleError as e:
    print("Ошибка треугольника:", e)

except PentagonError as e:
    print("Ошибка пятиугольника:", e)

except Exception as e:
    print("Другая ошибка:", e)