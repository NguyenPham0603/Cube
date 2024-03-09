import random
import cProfile
import time # thời gian trong hệ thống
import operator # các phép toán/ hành động
from cube import Cube # từ file cube.py (src) => gọi ra class Cube

# 1 cái list bước quay của từng mặt: U-D-F-B-L-R ( quay 90 và 180 )
SINGLE_MOVES = ["U", "U'", "U2", # mặt trên
                "D", "D'", "D2", # mặt dưới
                "F", "F'", "F2", # mặt trước
                "B", "B'", "B2", # mặt sau
                "L", "L'", "L2", # mặt trái
                "R", "R'", "R2", # mặt phải
                "M", "M'", "M2", # Lớp giữa mặt R- L
                "E", "E'", "E2", # lớp gữa mặt U - D
                "S", "S'", "S2"  # lớp giữa mặt F - B
                ]

# 1 cái list quay cả khối
FULL_ROTATIONS = ["x", "x'", "x2", #xoay theo chiều dọc từ trước ra sau hoặc sau ra trước
                  "y", "y'", "y2"] # xoay theo chiều ngang

ORIENTATIONS = ["z", "z'", "z2"] #xoay theo chiều dọc từ trái sang phải hoặc phải sang trái
#---------------------------------------------------------------------------
# rubik 3x3x3 có 54 ô nếu xoay 1 lần sẽ thay đổi vị trí của 20 ô => thay đổi 37% so với khối ban
# thay đổi quá lớn nếu áp dụng để tiến hóa, cho nên chọn ra những thay đổi nhỏ để áp dụng phương thức tiến hóa
# danh sách tất cả các hoán vị
PERMUTATIONS = [ # hàm split("") trả về 1 chuỗi con được cắt ra (seperate) bằng dấu cắt đã cho là " "
    # 2 cạnh của 3 mặt U - F - R
    "F' L' B' R' U' R U' B L F R U R' U".split(" "),
    # 2 cạnh của 3 mặt U - F - L
    "F R B L U L' U B' R' F' L' U' L U'".split(" "),
    #-----------------------------------------------
    # 2 góc - mỗi góc 3 mặt: U - F - R và U - F - L (1/9 khối)
    "U2 B U2 B' R2 F R' F' U2 F' U2 F R'".split(" "),
    # 2 góc - mỗi góc 3 mặt: U - F - L và U - L - B (1/9 khối)
    "U2 R U2 R' F2 L F' L' U2 L' U2 L F'". split(" "),
    #-----------------------------------------------
    # 2 cạnh của 3 mặt U - F - R và mặt L
    "U' B2 D2 L' F2 D2 B2 R' U'".split(" "),
    # 2 cạnh của 3 mặt U - F - L và mặt R
    "U B2 D2 R F2 D2 B2 L U".split(" "),
    #-----------------------------------------------
    # 1/9 khối _ 1 mặt có 2 ô khác màu: L
    "D' R' D R2 U' R B2 L U' L' B2 U R2".split(" "),
    # 1/9 khối _ 1 mặt có 2 ô khác màu: R
    "D L D' L2 U L' B2 R' U R B2 U' L2".split(" "),
    #-----------------------------------------------
    # 4 mặt xung quanh: màu khác nhau đối xứng qua đường chéo trục của khối
    "R' U L' U2 R U' L R' U L' U2 R U' L U'".split(" "),
    # 4 mặt xung quanh: màu khác nhau đối xứng qua đường chéo trục của khối
    "L U' R U2 L' U R' L U' R U2 L' U R' U".split(" "),
    #-----------------------------------------------
    # 1 góc (U - F - R), 2 ô có cạnh chung ngay góc: U - L và U - B
    "F' U B U' F U B' U'".split(" "),
    # 1 góc (U - F - L), 2 ô có cạnh chung ngay góc: U - R và U - B
    "F U' B' U F' U' B U".split(" "),
    #----------------------------------------------
    # 4 mặt theo chiều dọc ( U - F - D - B ): 1 ô rìa giữa
    "L' U2 L R' F2 R".split(" "),
    # 4 mặt theo chiều dọc ( U - F - D - B ): 1 ô rìa giữa (ngược lại)
    "R' U2 R L' B2 L".split(" "),
    #----------------------------------------------
    # 4 mặt xung quanh: 2 mặt đối diện đổi 1 ô cho nhau ( F - L - B - R)
    "M2 U M2 U2 M2 U M2".split(" ")
    ]

class Solver:

    def __init__(self, population_size, max_generations, max_resets, elitism_no):
        self.population_size = population_size # kich thuoc quan the
        self.max_generations = max_generations # thế hệ
        self.max_resets = max_resets
        self.elitism_no = elitism_no #chọn lọc

    #cac buoc xoay don ngau nhien:
    def random_single_moves(self):
        r = random.randint(0, len(SINGLE_MOVES) - 1)
        return [SINGLE_MOVES[r]]

    # Quay toàn phần ngẫu nhiên:
    def random_full_rotations(self):
        r = random.randint(0, len(FULL_ROTATIONS) - 1)
        return [FULL_ROTATIONS[r]]
    #
    def random_orientations(self):
        r = random.randint(0, len(ORIENTATIONS) - 1)
        return [ORIENTATIONS[r]]

    #chọn  ngẫu nhiên 1 hoán vị trong list
    def random_permutations(self):
        r = random.randint(0, len(PERMUTATIONS) - 1)
        return PERMUTATIONS[r]

    # copy
    def copy(self, cube_to, cube_from):
        for f in cube_from.faces:
            for i in range(0, 3):
                for j in range (0, 3):
                    cube_to.faces[f][i, j] = cube_from.faces[f][i, j]

        cube_to.move_history = [item for item in cube_from.move_history]
        cube_to.fitness = cube_from.fitness

    #giải pháp:
    def solve(self, scramble, verbose=False):
        start_time = time.time() #thời gian bat dau

        if verbose:
            print("Starting....")

        # 0 -> populations_size - 1
        for r in range(0, self.max_resets):
            #khởi tạo quần thể rubik:
            cubes = [] #khối rubik
            for i in range(0, self.population_size):
                cube = Cube()
                cube.execute(scramble) #xáo trộn các mặt để bắt đầu giải  3x3 => chuẩn 25 moves random
                # tiến hành ngẫu nhiên hóa bằng cách thực thi 2 bước di chuyển
                cube.execute(self.random_single_moves())
                cube.execute(self.random_single_moves())
                #thêm vào danh sách
                cubes.append(cube)




            #phát triển cube (evolve population)
            # lặp qua các thế hệ
            for g in range(0, self.max_generations):
                # sort by fitness
                cubes.sort(key=operator.attrgetter('fitness'))

                if verbose and g % 20 == 0 and g != 0:
                    print(f"World: {r + 1} - Generation: {g}")
                    print(f"Best solution so far")
                    print(f"{cubes[0].get_algorithm_str()}")
                    print(f"Fitness = {cubes[0].fitness}")
                    print("")

                # mục tiêu để làm nhỏ hàm số thích nghi
                for i in range(0, len(cubes)):
                    if cubes[i].fitness == 0: # rubik đã được giải thành công
                        print("Đã tìm thấy lời giải !")
                        print(f"world: {r + 1} - Generation: {g + 1}")
                        print(f"Scramble: {cubes[i].get_scramble_str()}") #in chuỗi cramble ra
                        print(f"Lời giải:")
                        print(f"{cubes[i].get_algorithm_str()}") # in lời giải
                        print(f"Moves: {len(cubes[i].get_algorithm())}") #số bước di chuyển
                        print(f"Fitness = {cubes[i].fitness}")
                        print(f"{time.time() - start_time} seconds")
                        print("")
                        return

                    # Phát triển: những cá thể tốt nhất được chuyễn sang cho thế hệ tiếp theo mà không thay đổi
                    # loại bỏ những giải pháp khác và thay thế nó
                    if i > self.elitism_no:
                        #sao chép khối đầu tiên ngẫu nhiên
                        self.copy(cubes[i], cubes[random.randint(0, self.elitism_no)])
                        evolution_type = random.randint(0, 5)

                        if evolution_type == 0:
                            cubes[i].execute(self.random_permutations())
                        elif evolution_type == 1:
                            cubes[i].execute(self.random_permutations())
                            cubes[i].execute(self.random_permutations())
                        elif evolution_type == 2:
                            cubes[i].execute(self.random_full_rotations())
                            cubes[i].execute(self.random_permutations())
                        elif evolution_type == 3:
                            cubes[i].execute(self.random_orientations())
                            cubes[i].execute(self.random_permutations())
                        elif evolution_type == 4:
                            cubes[i].execute(self.random_full_rotations())
                            cubes[i].execute(self.random_orientations())
                            cubes[i].execute(self.random_permutations())
                        elif evolution_type == 5:
                            cubes[i].execute(self.random_orientations())
                            cubes[i].execute(self.random_full_rotations())
                            cubes[i].execute(self.random_permutations())
            if verbose:
                print(f"Resetting the world")

        #Nếu xóa quần thể quá 10 lần thì dừng:
        print("")
        print(f"Solution not found.")
        print(f"{time.time() - start_time} seconds") # tinh thoi gian tim


# list quần thể rubik đã xáo trộn
LIST_SCRAMBLE = ["B' U L' B2 R' U' F B R' U2 L' F2 U2 L' B2 L2 U2 D2 L'",
                 "L B D2 F U2 F L2 R2 F2 U2 L2 R2 F2 D' B L D R2 B2 U B",
                 "L' U2 B2 L B2 R' B2 R' F2 D2 R' U2 D L2 R' D2 F' D' B2 U2 L'",
                 "L D L2 U2 L2 F2 U' L2 U' B2 R2 B2 U2 B U L2 R2 F' R B",
                 "F2 D2 R2 U' L2 D F2 D' F2 R2 U' F' R' D' B' L' D' R' D R' D'",
                 "R' U' L2 B2 U2 F L2 B' L' B D R B F2 L F R' B2 F' L B' D B2 R2 D' U B2 F' D R2",
                 "U2 B' F L B' F2 D' U B2 R' U B' F U F' R' U2 L' R' D F2 R' F' D2 L' R2 B' D L U2",
                 "B' R' U2 B' F D2 R2 B F' L2 R' B2 D2 L2 F' U L B2 D F L' F R B2 D' U' B' L' B' F2",
                 "F2 D2 U L' R' B2 L2 R2 B F L D' L2 D U' L' D' B2 D2 R' U L R' D' U L' R2 U F' L'",
                 "D' B2 D2 L2 U' L R' F L2 R2 U' L2 B' L D' B2 R2 B' R F U2 R B2 F' L' B2 L2 R F2 L'"
                 ]


#hàm main
def main():
    # Chọn ngẫu nhiên 1 quần thể trong danh sách để khởi tạo
    random_scramble = random.choice(LIST_SCRAMBLE)
    # tiến hành chia cắt quần thể vừa tạo
    scramble = random_scramble.split(" ")


    #input
    population_size = 500
    max_generations = 300
    max_resets = 10
    elitism_no = 50

    #gọi lớp Sovler
    solver = Solver(population_size, max_generations, max_resets, elitism_no)
    #gọi hàm giải quyết
    solver.solve(scramble, verbose=True)

if __name__== '__main__':
    main()
