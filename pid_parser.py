from typing import List
import model
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class PIDParser:

    def is_in_img(self,
                  object_start: List[float], object_end: List[float],
                  img_start_xy: List[float], img_end_xy: List[float], img_size=1280):

        # object x,y start
        x_real = object_start[0]
        y_real = object_start[1]

        # object x,y end
        x1_real = object_end[0]
        y1_real = object_end[1]

        # image boundries (start)
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

    def normalized_coords(self, start_xy: List[float], end_xy: List[float],
                          img_start: List[float],
                          img_size: List[float]):

        x_top = start_xy[0] - img_start[0]
        y_top = start_xy[1] - img_start[1]

        x_end = end_xy[0] - img_start[0]
        y_end = end_xy[1] - img_start[1]

        top_x = x_top
        top_y = y_top

        bot_x = x_end
        bot_y = y_end

        width = (bot_x - top_x)
        height = (bot_y - top_y)

        if (width < 0):
            top_x = bot_x

        if (height < 0):
            top_y = bot_y

        if width < 50:
            width = 50

        if height < 650:
            height = 50

        return top_x / img_size[0], top_y / img_size[1], abs(width) / img_size[0], abs(height) / img_size[1]

    def generate_line_labels(self,
                             pid_list: List[model.PID],
                             img_path: str,
                             labels_path: str,
                             visual_objects: dict[str, list[model.VisualObject]],
                             img_size=1280):

        all_images = os.listdir("./test_images")

        for img in all_images:
            spl = img.split('_')
            pid_id = spl[0]
            pid_original = [pid for pid in pid_list if pid.id == pid_id][0]
            # gather the boundires of the image
            horizontal = float(spl[2].replace('.jpg', ""))
            vertical = float(spl[1])

            img_x_start, img_y_start = horizontal, vertical
            img_x_end, img_y_end = horizontal + img_size, vertical + img_size
            img_dir = img_path

            self.create_dirs(img_dir)

            all_data = []
            for obj in visual_objects[pid_id]:
                # image boundries (start)
                is_in_img_fully = self.is_in_img(obj.start_xy, obj.end_xy,
                                                 [img_x_start, img_y_start],
                                                 [img_x_end, img_y_end],
                                                 img_size=img_size)

                if not is_in_img_fully:
                    continue

                format_label = '.txt'

                name = os.path.splitext(img)[0]

                # format_img = '.png'
                # img_name = os.path.join(img_dir, '{0}{1}'.format(
                #     pid_id, format_img))

                label_name = os.path.join(labels_path, '{0}{1}'.format(
                    name, format_label))

                next = '{0} {1} {2} {3} {4}'.format(
                    obj.get_label(),
                    *self.normalized_coords(
                        obj.start_xy,
                        obj.end_xy,
                        [img_x_start, img_y_start],
                        [img_size, img_size])
                )

                all_data.append([obj.start_xy[0], obj.start_xy[1],
                                obj.end_xy[0], obj.end_xy[1],
                                obj.get_category()])

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

            self.render_samples(pid_original, img_x_start, img_y_start, img_x_end, img_y_end, all_data)

    def render_samples(self, pid_original, img_x_start, img_y_start, img_x_end, img_y_end, all_data):
        im = Image.open(pid_original.path)
        fig, ax = plt.subplots()

        fig.set_size_inches(30, 30)
        rect = patches.Rectangle((img_x_start, img_y_start), img_y_end - img_y_start, img_x_end-img_x_start,
                                 fill=None, alpha=1, color = 'red')
        ax.add_artist(rect)
        i = 1
        import random

        number_of_colors = 8

        for coord in all_data:
            color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]

            rect = patches.Rectangle((coord[0], coord[1]), coord[2]+3-coord[0], coord[3]+3-coord[1],
                                     linewidth=2, label=coord[4], color = color[0])

            ax.add_artist(rect)
            rx, ry = rect.get_xy()
            cx = rx + rect.get_width()
            cy = ry + rect.get_height()
            i = i + 1
            # ax.annotate(coord[4], (cx, cy), color='blue', weight='bold',
            #             fontsize=20)
        ax.imshow(im)

    def create_dirs(self, img_dir):
        if not os.path.isdir(img_dir):
            try:
                os.makedirs(img_dir)
            except Exception as ex:
                print(ex)
                pass

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
