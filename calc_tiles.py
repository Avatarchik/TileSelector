import math
import numpy as np
import numpy.ma as ma

import sys, string, os, subprocess

def calc_theta_phi(vertex):
    theta = round(math.degrees(math.atan(vertex[1] / vertex[0])), 4)
    phi = round(math.degrees(math.acos(vertex[2])), 4)
    return theta, phi

def get_quantization(point):
    r = get_distance(point, np.array([0,0,0]))
    x = point[0]
    y = point[1]
    z = point[2]
    new_x = x / r
    new_y = y / r
    new_z = z / r
    return np.array([new_x, new_y, new_z])

def calc_rotation(yaw, pitch, roll=0):
    yaw = math.radians(yaw)
    pitch = math.radians(pitch)
    roll = math.radians(roll)

    mat_yaw = np.matrix([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]])
    mat_pitch = np.matrix([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]])
    mat_roll = np.matrix([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]])

    R = mat_yaw.dot(mat_pitch.dot(mat_roll))

    return R

def get_distance(cp1, cp2):
    gap = cp1 - cp2
    return np.sqrt(np.power(gap[0], 2) + np.power(gap[1], 2) + np.power(gap[2], 2))

def ra2de(radi):
    return round(math.degrees(radi), 5)

def calc_euler(mat_rotate):
    cosine_for_pitch = math.sqrt(mat_rotate[0][0] ** 2 + mat_rotate[1][0] ** 2)
    is_singular = cosine_for_pitch < 10 ** -6
    if not is_singular:
        yaw = math.atan2(mat_rotate[1][0], mat_rotate[0][0])
        pitch = math.atan2(-mat_rotate[2][0], cosine_for_pitch)
        roll = math.atan2(mat_rotate[2][1], mat_rotate[2][2])
    else:
        yaw = math.atan2(-mat_rotate[1][2], mat_rotate[1][1])
        pitch = math.atan2(-mat_rotate[2][0], cosine_for_pitch)
        roll = 0
    return ra2de(yaw), ra2de(pitch), ra2de(roll)

### TESTSTSTSETST


binary_file_name = 'Gaslamp_qp22_10bit_MCTS_nuni4_3123.bin'
dir_name = binary_file_name.split('.')[0]

hor_name = None
horizontal_line = None
this_3x4 = False

if '_nuni3_494' in binary_file_name:
    hor_name, horizontal_line = ('_3'), ([-180, -60, 60, 180])
    ver_name, vertical_line = ('_494'), ([-90, -45, 45, 90])
elif '_nuni3_3123' in binary_file_name:
    hor_name, horizontal_line = ('_3'), ([-180, -60, 60, 180])
    ver_name, vertical_line = ('_141'), ([-90, -60, 60, 90])
elif '_uni33' in binary_file_name:
    hor_name, horizontal_line = ('_3'), ([-180, -60, 60, 180])
    ver_name, vertical_line = ('_333'), ([-90, -30, 30, 90])
elif '_nuni4_494' in binary_file_name:
    hor_name, horizontal_line = ('_4'), ([-180, -90, 0, 90, 180])
    ver_name, vertical_line = ('_494'), ([-90, -45, 45, 90])
    this_3x4 = True
elif '_nuni4_3123' in binary_file_name:
    hor_name, horizontal_line = ('_4'), ([-180, -90, 0, 90, 180])
    ver_name, vertical_line = ('_141'), ([-90, -60, 60, 90])
    this_3x4 = True
elif '_uni43' in binary_file_name:
    hor_name, horizontal_line = ('_4'), ([-180, -90, 0, 90, 180])
    ver_name, vertical_line = ('_333'), ([-90, -30, 30, 90])
    this_3x4 = True
else:
    print('fail to read file')

os.mkdir(dir_name)
FNULL = open(os.devnull, 'w')
args = []

args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 0 -tt 1 -o ' + dir_name + '\\0.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 1 -tt 1 -o ' + dir_name + '\\1.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 2 -tt 1 -o ' + dir_name + '\\2.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 3 -tt 1 -o ' + dir_name + '\\3.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 4 -tt 1 -o ' + dir_name + '\\4.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 5 -tt 1 -o ' + dir_name + '\\5.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 6 -tt 1 -o ' + dir_name + '\\6.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 7 -tt 1 -o ' + dir_name + '\\7.bin ')
args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 8 -tt 1 -o ' + dir_name + '\\8.bin ')

if this_3x4:
    args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 9 -tt 1 -o ' + dir_name + '\\9.bin ')
    args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 10 -tt 1 -o ' + dir_name + '\\10.bin ')
    args.append('Extractor.exe -b ' + binary_file_name + ' -te 0 -ts 11 -tt 1 -o ' + dir_name + '\\11.bin ')

for arg in args:
    subprocess.call(arg, stdout=FNULL, stderr=FNULL, shell=False)

bits = []

bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\0.bin >> '+dir_name+'\\0.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\1.bin >> '+dir_name+'\\1.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\2.bin >> '+dir_name+'\\2.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\3.bin >> '+dir_name+'\\3.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\4.bin >> '+dir_name+'\\4.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\5.bin >> '+dir_name+'\\5.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\6.bin >> '+dir_name+'\\6.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\7.bin >> '+dir_name+'\\7.csv ')
bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\8.bin >> '+dir_name+'\\8.csv ')

if this_3x4:
    bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\9.bin >> +'+dir_name+'\\9.csv')
    bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\10.bin >> +'+dir_name+'\\10.csv')
    bits.append('ffprobe.exe -select_streams v -show_entries packet=size:stream=bitrate -of compact=p=0:nk=1 '+dir_name+'\\11.bin >> +'+dir_name+'\\11.csv')

for bit in bits:
    subprocess.call(bit, stdout=FNULL, stderr=FNULL, shell=False)
    print('hi')

#view_name, view_start, view_end = ('_1st'), ([-45, -15]), ([45, 15])
#view_name, view_start, view_end = ('_2nd'), ([-201, -73]), ([-111, -43])

#view_name, view_start, view_end = ('_1st'), ([-51, -11]), ([39, 19])
#view_name, view_start, view_end = ('_2nd'), ([61, -15]), ([151, 15])

#view_name, view_start, view_end = ('_1st'), ([-83, -56]), ([7, -26])
#view_name, view_start, view_end = ('_2nd'), ([-140, 12]), ([-50, 42])

#view_name, view_start, view_end = ('_1st'), ([-114, -53]), ([-24, -23])
#view_name, view_start, view_end = ('_2nd'), ([13, -41]), ([103, -11])

view_name, view_start, view_end = ('_1st'), ([-180, 35]), ([-270, 5])
view_name, view_start, view_end = ('_2nd'), ([-65, -5]), ([25, 25])

#view_name, view_start, view_end = ('_1st'), ([210, -18]), ([300, 12])
#view_name, view_start, view_end = ('_2nd'), ([30, -44]), ([120, -14])

all_tiles = []

tiles = []
for frame in range(300):
    theta = view_start[0] + ((frame * (view_end[0] - view_start[0])) / 300)
    phi = view_start[1] + ((frame * (view_end[1] - view_start[1])) / 300)
    view_current = [theta, phi]
    cur_tile = 0
    if frame < 300:
        for i in range(len(horizontal_line)-1):
            if horizontal_line[i] < theta and theta <= horizontal_line[i+1]:
                cur_tile = i
        for i in range(len(vertical_line)-1):
            if vertical_line[i] < phi and phi <= vertical_line[i+1]:
                cur_tile = cur_tile + ((len(horizontal_line)-1) * i)

        point0 = calc_rotation(theta, phi).dot(calc_rotation(-37.5, -37.5).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point1 = calc_rotation(theta, phi).dot(calc_rotation(0, -37.5).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point2 = calc_rotation(theta, phi).dot(calc_rotation(37.5, -37.5).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point3 = calc_rotation(theta, phi).dot(calc_rotation(-37.5, 0).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point4 = calc_rotation(theta, phi).dot(calc_rotation(37.5, 0).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point5 = calc_rotation(theta, phi).dot(calc_rotation(-37.5, 37.5).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point6 = calc_rotation(theta, phi).dot(calc_rotation(0, 37.5).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]
        point7 = calc_rotation(theta, phi).dot(calc_rotation(37.5, 37.5).dot(np.array([1, 0, 0]).T).T).T.tolist()[0]

        points2 = [[point0, point2],
                   [point3, point4],
                   [point5, point7],
                   [point5, point0],
                   [point6, point1],
                   [point7, point2]]

        tiles.append(cur_tile)

        for vertecies in points2:
            p1 = np.array(np.matrix(vertecies[0]).tolist()[0])
            p2 = np.array(np.matrix(vertecies[1]).tolist()[0])
            p0 = np.array([0.0, 0.0, 0.0])

            PQ = p2-p0
            PR = p1-p0
            value = [(PQ[1] * PR[2]) - (PQ[2] * PR[1]), -((PQ[0] * PR[2]) - (PQ[2] * PR[0])), (PQ[0] * PR[1]) - (PQ[1] * PR[0])]
            value = np.array(value)
            divide = np.sqrt((np.power(value[0], 2) + np.power(value[1], 2) + np.power(value[2], 2)))
            vector_n = value / divide

            for hor, num in zip(horizontal_line[:-1], range(len(horizontal_line[:-1]))):
                for i in range(len(vertical_line)-1):
                    pt1 = np.array(np.matrix(calc_rotation(hor, vertical_line[i])).dot(np.matrix([1, 0, 0]).T).T.tolist())[0]
                    pt2 = np.array(np.matrix(calc_rotation(hor, vertical_line[i+1])).dot(np.matrix([1, 0, 0]).T).T.tolist())[0]
                    underU = vector_n.dot(pt2 - pt1)
                    upU = vector_n.dot(p1 - pt1)
                    upU2 = vector_n.dot(p2 - pt1)
                    if underU == 0:
                        continue
                    u = upU / underU
                    u2 = upU2 / underU
                    if u >= 0.0 and u <= 1.0 and u2 >= 0.0 and u2 <= 1.0:
                        cur_point = pt1 + (u * (pt2 - pt1))
                        dis_p1 = get_distance(cur_point, p1)
                        dis_p2 = get_distance(cur_point, p2)
                        purpose_distance = get_distance(p1, p2)
                        if dis_p1 <= purpose_distance and dis_p2 <= purpose_distance:
                            tiles.append(i * (len(horizontal_line)-1) + num)
                            tiles.append(i * (len(horizontal_line)-1) + ((num-1) % (len(horizontal_line)-1)))

            for ver, num in zip(vertical_line, range(len(vertical_line))):
                for i in range(len(horizontal_line)-1):
                    pt1 = np.array(np.matrix(calc_rotation(horizontal_line[i], ver)).dot(np.matrix([1, 0, 0]).T).T.tolist())[0]
                    pt2 = np.array(np.matrix(calc_rotation(horizontal_line[i+1], ver)).dot(np.matrix([1, 0, 0]).T).T.tolist())[0]
                    underU = vector_n.dot(pt2 - pt1)
                    upU = vector_n.dot(p1 - pt1)
                    upU2 = vector_n.dot(p2 - pt1)
                    if underU == 0:
                        continue
                    u = upU / underU
                    u2 = upU2 / underU
                    if u >= 0.0 and u <= 1.0 and u2 >= 0.0 and u2 <= 1.0:
                        cur_point = pt1 + (u * (pt2 - pt1))
                        dis_p1 = get_distance(cur_point, p1)
                        dis_p2 = get_distance(cur_point, p2)
                        purpose_distance = get_distance(p1, p2)
                        if dis_p1 <= purpose_distance and dis_p2 <= purpose_distance:
                            if num == 0:
                                tiles.append(0)
                                tiles.append(1)
                                tiles.append(2)
                                if (len(horizontal_line) == 5):
                                    tiles.append(3)
                            elif num == (len(vertical_line)-1):
                                tiles.append((len(horizontal_line)-1)*(len(vertical_line)-2))
                                tiles.append((len(horizontal_line)-1)*(len(vertical_line)-2)+1)
                                tiles.append((len(horizontal_line)-1)*(len(vertical_line)-2)+2)
                                if (len(horizontal_line) == 5):
                                    tiles.append((len(horizontal_line)-1)*(len(vertical_line)-2)+3)
                            else:
                                tiles.append(num * (len(horizontal_line)-1) + i)
                                tiles.append(num * (len(horizontal_line)-1) + i - (len(horizontal_line)-1))

    if frame % 32 == 31 or frame == 299:
        tiles = list(set(tiles))
        new_tiles = []
        for tile in tiles:
            if tile < (len(horizontal_line)-1):
                new_tiles.append(tile + ((len(horizontal_line)-1) * (len(vertical_line)-2)))
            elif tile >= ((len(horizontal_line)-1) * (len(vertical_line)-2)):
                new_tiles.append(tile - ((len(horizontal_line)-1) * (len(vertical_line)-2)))
            else:
                new_tiles.append(tile)
        new_tiles = list(set(new_tiles))
        all_tiles.append(new_tiles)
        tiles = []

print(all_tiles)

#plt.savefig(imageFileName)