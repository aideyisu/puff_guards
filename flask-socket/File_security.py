import os
import json
import time

def check_files(filePath=os.getcwd(), size=0):
    path =  os.getcwd()
    B = os.walk(path)
    num = 0
    Set = ''
    for root, dirs, files in B:
        if Set == '':
            Set = root
        #     print("网站根目录")
        # else:
        #     print(f"当前目录： {root.split(Set)[-1]}")
        # print(f"    内含子目录 ： {dirs}")
        # print(f"    包含文件 ： {files}")
        num += len(files)
    size = getFileSize()
    return num, size


def getFileSize(filePath=os.getcwd(), size=0):
    for root, _, files in os.walk(filePath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))

    return size

def check_safe():
    safe_file = open('safe.json', 'r+')
    safe_content = safe_file.readline()
    if safe_content == '':
        safe_content = {'safe_size': 1}
    else:
        safe_content = eval(safe_content)
    _, corrent_size = check_files()
    safe_status = True if safe_content['file_size'] == corrent_size else False 
    print("safe") if safe_status == True else print("NOT safe")

    safe_file.close()


def set_safe_content(filePath=os.getcwd(), size=0):
    safe_file = open('safe.json', 'r+')
    first_Catalog_list = []
    second_Catalog_list = []
    other_Catalog_list = []

    file_list = []
    Set = ''
    num = 0
    for root, _, files in os.walk(filePath):
        if Set == '':
            Set = root
            current_root = 'root'
        else:
            current_root = root.split(Set)[-1]
            if len(current_root.split('\\')) == 2:
                first_Catalog_list.append(current_root)
            elif len(current_root.split('\\')) == 3:
                second_Catalog_list.append(current_root)
            else:
                other_Catalog_list.append(current_root)
                
        for f in files:
            file_size = os.path.getsize(os.path.join(root, f))
            size += file_size
            num += 1
            file_list.append({'file_name': f, 'file_root': current_root, 'file_size': file_size})
    
    # last_modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    last_modify_time = time.strftime("%Y-%m-%d", time.localtime())
    last_modify_time = last_modify_time.split(' ')[0]
    safe_content = {'file_num': num, 'file_size': size, 'file_list': file_list ,\
        'last_modify_time' : last_modify_time, 'first':first_Catalog_list, \
            'second': second_Catalog_list, 'other': other_Catalog_list}
    print(safe_content)
    safe_file.write(json.dumps(safe_content))
    safe_file.close()


def read_safe_content(filePath=os.getcwd(), size=0):
    safe_file = open('safe.json', 'r+')
    safe_content = json.loads(safe_file.readline())
    safe_file.close()
    return safe_content

# set_safe_content()
# 通过运行这个函数

# A = read_safe_content()
# check_safe()

# for i in A:
#     print(A[i])

