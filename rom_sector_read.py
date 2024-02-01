# -*- coding:utf-8 -*-
# проверка связи rs
import time
import csv

import shortClasses

import add_import_paths  # не удалять тут пути прописываются
add_import_paths.add_public_path()
import support_scripts
import techChannel
import datetime
import logger


# создание csv
def writer(_data):
    csv_file = open("Data_From_GVM.csv", 'w')
    _writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
    _len = len(_data)
    str_len = 16

    for j in range(_len / str_len):
        tmp = list()
        for i in range(str_len):
            tmp.append(_data[i + j * str_len])
        _writer.writerow(tmp)
    # tmpstring = '0x' + ("".join(format(_data[i], '02x') for i in range(4)))
    # print(tmpstring)


# чтение целого сектора
# НАДО ОБГОВОРИТЬ. Закомментил проверку КС в techMonitor.py, чтобы после теста можно было считывать данные с ПЗУ.
def read_sector(work_obj, number_sector, fast=False):
    sector_address = work_obj.get_flash_info(number_sector, 1).data | 0xA0000000
    # print(hex(sector_address))
    sector_size = shortClasses.GVM_PZU_K[number_sector]
    max_read_count = 0xe0  # 224 (7 строк по 32 )
    next_sector_address = sector_address + sector_size

    ptr = sector_address
    data = list()

    if fast:
        # быстрый вариант (первые 7 строк для проверки работы)
        tmp = work_obj.read_memory_long(ptr, max_read_count).data
        if type(tmp) == list:
            return tmp
        else:
            print(tmp.print_all_data())
            return list()

    while ptr + max_read_count < next_sector_address:
        data.extend(work_obj.read_memory_long(ptr, max_read_count).data)
        ptr += max_read_count
    if ptr != sector_address:
        remaining_space = next_sector_address - ptr
        data.extend(work_obj.read_memory_long(ptr, remaining_space).data)

    return data


temp = support_scripts.get_path_logger_file(__file__)
logger_instance = logger.Logger(temp["path"])

# вывод времени начала скрипта
print(temp["time"])

# вывод информации о скрипте
TEST_TEXT_NUMBER = u"Скрипт для проверки пункта ТУ !!!!!"
TEST_DESCRIPTION = u"Проверка соединения по тех. каналу RS232"

fact_error = False

# создаем рабочий класс
work_object = techChannel.TechChannel(protocol_type="GVM_Mon", number_vm=0)
fact_error |= support_scripts.test_check_rs232(work_object)

# чтение сектора
print("Reading sector...")
time.clock()
data_from_gvm = read_sector(work_obj=work_object, number_sector=30, fast=False)
print("time passed: {}s.".format(time.clock()))
writer(data_from_gvm)

return_data = work_object.close_link()

# печать дополнительной информации только в лог
return_data.print_data_into_log()

support_scripts.print_status_scripts(fact_error)  # Вывод результатов тестирования

# вывод времени конца скрипта
print(u"<Log> {}".format(datetime.datetime.now()))
logger_instance.closeLogger()
# ----------------------------------------------------------------------------------------------------------------------
