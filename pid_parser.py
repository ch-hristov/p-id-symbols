from typing import List
import model
import os
import numpy as np
from PIL import Image


class PIDParser:

    def is_in_img(self, object: model.VisualObject, img_start_xy: List[float],
                  img_end_xy: List[float], img_size=1280):

        #object x,y start
        x_real = object.start_xy[0]
        y_real = object.start_xy[1]

        #object x,y end
        x1_real = object.end_xy[0]
        y1_real = object.end_xy[1]

        #image boundries (start)
        img_x_start = img_start_xy[0]
        img_x_end = img_end_xy[0]

        # image boundries (end)
        img_y_start = img_start_xy[1]
        img_y_end = img_end_xy[1]
        

        if x_real >= img_x_start and x1_real <= img_x_end and y_real >= img_y_start and y1_real <= img_y_end:

            x_img_real = x_real - img_x_start
            y_img_real = y_real - img_y_start

            x1_img_real = x1_real - img_x_start
            y1_img_real = y1_real - img_y_start

            if x_img_real < 0:
                return False

            if (y_img_real < 0):
                return False

            if (x1_img_real < 0):
                return False

            if (y1_img_real < 0):
                return False

            if (x_img_real >= img_size):
                return False

            if (y_img_real >= img_size):
                return False

            if (x1_img_real >= img_size):
                return False

            if (y1_img_real >= img_size):
                return False

            return True
        return False

    def to_label(self, type: str):
        if type == 'solid':
            return 0
        if type == 'dashed':
            return 1
        return 2

    def normalized_coords(self, start_xy: List[float], end_xy: List[float], img_size: List[float]):
        top_x = min(start_xy[0], end_xy[0]) / img_size[0]
        top_y = min(start_xy[1], end_xy[1]) / img_size[1]

        bot_x = max(start_xy[0]+3, end_xy[0]+3) / img_size[0]
        bot_y = max(start_xy[1]+3, end_xy[1]+3) / img_size[1]

        width = (bot_x - top_x)
        height = (bot_y - top_y)

        return top_x, top_y, width, height

    def generate_line_labels(self, pid_list: List[model.PID], img_path: str, labels_path: str):
        lines = {}
        img_size = 1280

        all_images = os.listdir("./images")

        for pid in pid_list:
            for line in pid.lines:
                if line.pid.id not in lines:
                    lines[line.pid.id] = []
                lines[line.pid.id].append(line)

        for img in all_images:
            spl = img.split('_')
            pid_id = spl[0]

            horizontal = float(spl[2].replace('.jpg', ""))
            vertical = float(spl[1])

            img_x_start, img_y_start = horizontal, vertical
            img_x_end, img_y_end = horizontal + img_size, vertical + img_size

            img_dir = img_path

            if not os.path.isdir(img_dir):
                try:
                    os.makedirs(img_dir)
                except Exception as ex:
                    print(ex)
                    pass

            for line in lines[pid_id]:

                #image boundries (start)
                is_in_img = self.is_in_img(line, [img_x_start, img_y_start], [img_x_end, img_y_end],
                      img_size=img_size)

                # debugstr = 'Checking if {0} is in {1} = {2}'.format([ [x_real, y_real] , [x1_real, y1_real]], 
                #                                             [[img_x_start, img_y_start], [img_x_end, img_y_end]], is_in_img)
                # print(debugstr)

                if not is_in_img:
                    continue

                format_img = '.png'
                format_label = '.txt'

                name = os.path.splitext(img)[0]

                img_name = os.path.join(img_dir, '{0}{1}'.format(
                    pid.id, format_img))

                label_name = os.path.join(labels_path, '{0}{1}'.format(
                    name, format_label))

                next = '{0} {1} {2} {3} {4}'.format(
                    self.to_label(line.types), *self.normalized_coords(
                        line.start_xy, line.end_xy, [pid.width, pid.height])
                )

                if not os.path.isdir(labels_path):
                    os.mkdir(labels_path)

                # Open the file in append & read mode ('a+')
                with open(label_name, "a+") as file_object:
                    # Move read cursor to the start of file.
                    file_object.seek(0)
                    # If file is not empty then append '\n'
                    data = file_object.read(100)
                    if len(data) > 0:
                        file_object.write("\n")
                    # Append text at the end of file
                    file_object.write(next)

    def parse_folder_npy(self, dataset_path='./dataset'):

        dirs = os.walk(dataset_path)

        pids = []

        for folder in dirs:
            folderName, folders, _ = folder
            for items in folders:
                files = os.walk(folderName + "/" + items)
                for fileWalk in files:
                    folder, _, _ = fileWalk

                    if 'ipynb_checkpoints' in folder:
                        continue

                    label = folder.split('/')[-1]

                    if not label.isdigit():
                        continue

                    path = folder + "/" + label
                    symbol_set, line_set, table_set, word_set, linker, key_value, other_lines = None, None, None, None, None, None, None

                    if os.path.isfile(path+"_symbols.npy"):
                        symbol_set = np.load(
                            path+"_symbols.npy", allow_pickle=True)

                    if os.path.isfile(path+"_lines.npy"):
                        line_set = np.load(
                            path+"_lines.npy", allow_pickle=True)

                    if os.path.isfile(path+"_Table.npy"):
                        table_set = np.load(
                            path+"_Table.npy", allow_pickle=True)

                    if os.path.isfile(path+"_words.npy"):
                        word_set = np.load(
                            path+"_words.npy", allow_pickle=True)

                    if os.path.isfile(path+"_linker.npy"):
                        linker = np.load(path+"_linker.npy", allow_pickle=True)

                    if os.path.isfile(path+"_KeyValue.npy"):
                        key_value = np.load(
                            path+"_KeyValue.npy", allow_pickle=True)

                    if os.path.isfile(path+"_lines2.npy"):
                        other_lines = np.load(
                            path+"_lines2.npy", allow_pickle=True)

                    pid = model.PID()

                    pid.id = label
                    pid.path = './dataset/real-life-images/{0}.jpg'.format(
                        label)

                    img_shape = Image.open(pid.path)
                    pid.width = img_shape.size[0]
                    pid.height = img_shape.size[1]

                    if symbol_set is not None:
                        for entry in symbol_set:
                            symbol = model.Symbol(
                                entry[0], entry[1][0:2], entry[1][2:], entry[2], pid)
                            pid.symbols.append(symbol)

                    if line_set is not None:
                        for entry in line_set:
                            line = model.Line(
                                entry[0], entry[1][0:2], entry[1][2:], entry[2], entry[3], pid)
                            pid.lines.append(line)

                    if other_lines is not None:
                        for entry in other_lines:
                            line = model.OtherLine(
                                entry[0:2], entry[2:4], entry[-1])
                            pid.otherLines.append(line)

                    if table_set is not None:
                        for entry in table_set:
                            pid.table.append(entry)

                    if word_set is not None:
                        for word in word_set:
                            pid.words.append(model.Word(
                                word[0], word[1][0:2], word[1][2:],  word[2], word[3]))

                    if linker is not None:
                        for word in linker:
                            pid.links.append(model.Link(word[0], word[1]))

                    if key_value is not None:
                        for item in key_value:
                            pid.details.append(item)

                    pids.append(pid)

        assert (len(pids) > 0)
        return pids
