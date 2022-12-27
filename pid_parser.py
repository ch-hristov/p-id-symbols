import model
import os
import numpy as np
from PIL import Image

class PIDParser:
    def parse_folder_npy(dataset_path = '/content/drive/MyDrive/pid_dataset/dataset_p1/DigitizePID_Dataset'):

        dirs = os.walk(dataset_path)

        pids = []

        for folder in dirs: 
            folderName, folders, _ = folder
            for items in folders:
                files = os.walk(folderName + "/"+ items)
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
                        symbol_set = np.load(path+"_symbols.npy", allow_pickle = True)
                        
                    if os.path.isfile(path+"_lines.npy"):
                        line_set = np.load(path+"_lines.npy", allow_pickle = True)
                        
                    if os.path.isfile(path+"_Table.npy"):
                        table_set = np.load(path+"_Table.npy", allow_pickle = True)
                        
                    if os.path.isfile(path+"_words.npy"):
                        word_set = np.load(path+"_words.npy", allow_pickle = True)
                        
                    if os.path.isfile(path+"_linker.npy"):
                        linker = np.load(path+"_linker.npy", allow_pickle = True)
                        
                    if os.path.isfile(path+"_KeyValue.npy"):
                        key_value = np.load(path+"_KeyValue.npy", allow_pickle = True)
                        
                    if os.path.isfile(path+"_lines2.npy"):
                        other_lines = np.load(path+"_lines2.npy", allow_pickle = True)

                    pid = model.Symbol()
                    
                    pid.id = label
                    pid.path = '/content/drive/MyDrive/pid_dataset/dataset_p1/DigitizePID_Dataset/real-life-images/{0}.jpg'.format(label)
                    
                    img_shape = Image.open(pid.path)
                    pid.width = img_shape.size[0]
                    pid.height = img_shape.size[1]
                    
                    if symbol_set is not None:
                        for entry in symbol_set:
                            symbol = model.Symbol(entry[0], entry[1][0:2], entry[1][2:], entry[2], pid)
                            pid.symbols.append(symbol)

                    if line_set is not None:
                        for entry in line_set:
                            line = model.Line(entry[0], entry[1][0:2], entry[1][2:], entry[2], entry[3])
                            pid.lines.append(line)

                    if other_lines is not None:
                        for entry in other_lines:
                            line = model.OtherLine(entry[0:2], entry[2:4], entry[-1])
                            pid.otherLines.append(line)
            
                    if table_set is not None:
                        for entry in table_set:
                            pid.table.append(entry)
            
                    if word_set is not None:
                        for word in word_set:
                            pid.words.append(model.Word(word[0], word[1][0:2], word[1][2:],  word[2], word[3]))
                            
                    if linker is not None:
                        for word in linker:
                            pid.links.append(model.Link(word[0], word[1]))

                    if key_value is not None:
                        for item in key_value:
                            pid.details.append(item)
                            
                    pids.append(pid)
                    
        assert(len(pids) > 0)
        print(len(pids))