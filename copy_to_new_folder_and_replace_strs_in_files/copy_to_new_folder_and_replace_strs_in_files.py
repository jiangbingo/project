import os
import sys
import re
import time
import platform
import shutil

params_change_file = "copy_to_new_folder_and replace_strs_param.ini"
cells_num = 20
current_dir = os.getcwd()
log_name = os.path.join(current_dir, "convert.log")
try:
    os.remove(log_name)
except:
    pass
finally:
    log_fd = os.open(log_name, os.O_RDWR | os.O_CREAT)
    os.close(log_fd)


def list_files(cases_dir):
    all_files = []
    for root, dirs, files in os.walk(cases_dir):
        for file in files:
            if root.count(".svn") == 0 and file.count(".svn") == 0 and file.count(".bak") == 0:
                all_files.append((root, file))
    return all_files


def handle_input_params():
    log_fd = os.open(log_name, os.O_RDWR | os.O_APPEND)
    # remove comments
    file_object = open(params_change_file)
    try:
        all_the_text = file_object.read()
        all_the_text = re.sub("\s*#.*", "", all_the_text)
    finally:
        file_object.close()
    # get cases_dir
    match = re.search(r"\s*new_cases_dir\s*=\s*[\'\"]+(.*)[\'\"]+", all_the_text, re.I)
    match_old = re.search(r"\s*old_cases_dir\s*=\s*[\'\"]+(.*)[\'\"]+", all_the_text, re.I)
    cases_dir_old = match_old.group(1)
    all_the_text = all_the_text.replace(match_old.group(0), "")
    if match is not None:
        cases_dir = match.group(1)
        print "cases_dir:%s" % cases_dir
        os.write(log_fd, "cases_dir:%s\n" % cases_dir)
        all_the_text = all_the_text.replace(match.group(0), "")
    else:
        raise Exception("not specify cases_dir")
    # get all params
    params_list_to_be_extend = []
    params_not_extend = []
    for line in all_the_text.splitlines():
        if len(line.strip()) != 0:
            if line.count("@distaName") or line.count("@name"):
                params_not_extend.append((line.split("to")[0].strip(), line.split("to")[1].strip()))
            elif line.count("\""):
                params_not_extend.append((line.split("\"")[1], line.split("\"")[3]))
            elif line.count("\'"):
                params_not_extend.append((line.split("\'")[1], line.split("\'")[3]))
            else:
                params_list_to_be_extend.append((line.split()[0], line.split()[1]))
                # extend input param for LNCEL
    print "parameters to be changed:"
    os.write(log_fd, "parameters to be changed:\n")
    for param_before_not_e, param_after_not_e in params_not_extend:
        print "'%s'\t\t'%s'" % (param_before_not_e, param_after_not_e)
        os.write(log_fd, "'%s'\t\t'%s'\n" % (param_before_not_e, param_after_not_e))
    
    params_extend_lncel = []
    for param_before, param_after in params_list_to_be_extend:
        print "%s\t\t%s" % (param_before, param_after)
        os.write(log_fd, "%s\t\t%s\n" % (param_before, param_after))
        params_extend_lncel.append((param_before, param_after))
        if param_before.count("LNCEL:") or param_before.count("LNCEL/"):
            for cell_id in range(1, cells_num + 1):
                # expression 1
                param_before_cell_1 = param_before.replace("LNCEL:", "LNCEL-${CELL%s_INFO.ID}:" % cell_id)
                param_before_cell_1 = param_before_cell_1.replace("LNCEL/", "LNCEL-${CELL%s_INFO.ID}/" % cell_id)
                param_after_cell_1 = param_after.replace("LNCEL:", "LNCEL-${CELL%s_INFO.ID}:" % cell_id)
                param_after_cell_1 = param_after_cell_1.replace("LNCEL/", "LNCEL-${CELL%s_INFO.ID}/" % cell_id)
                params_extend_lncel.append((param_before_cell_1, param_after_cell_1))
                # expression 2
                param_before_cell_2 = param_before.replace("LNCEL:", "${CELL%s_INFO.LNCELL}:" % cell_id)
                param_before_cell_2 = param_before_cell_2.replace("LNCEL/", "${CELL%s_INFO.LNCELL}/" % cell_id)
                param_after_cell_2 = param_after.replace("LNCEL:", "${CELL%s_INFO.LNCELL}:" % cell_id)
                param_after_cell_2 = param_after_cell_2.replace("LNCEL/", "${CELL%s_INFO.LNCELL}/" % cell_id)
                params_extend_lncel.append((param_before_cell_2, param_after_cell_2))
                # expression 3
                param_before_cell_3 = param_before.replace("LNCEL:", "LNCEL-%s:" % cell_id)
                param_before_cell_3 = param_before_cell_3.replace("LNCEL/", "LNCEL-%s/" % cell_id)
                param_after_cell_3 = param_after.replace("LNCEL:", "LNCEL-%s:" % cell_id)
                param_after_cell_3 = param_after_cell_3.replace("LNCEL/", "LNCEL-%s/" % cell_id)
                params_extend_lncel.append((param_before_cell_3, param_after_cell_3))

    # extend input param for LNBTS
    params_extend = []
    for param_before, param_after in params_extend_lncel:
        params_extend.append((param_before, param_after))
        if param_before.count("LNBTS:") or param_before.count("LNBTS/"):
            # expression 1
            param_before_lnbts_1 = param_before.replace("LNBTS:", "LNBTS-${BTS_INFO.ID}:")
            param_before_lnbts_1 = param_before_lnbts_1.replace("LNBTS/", "LNBTS-${BTS_INFO.ID}/")
            param_after_lnbts_1 = param_after.replace("LNBTS:", "LNBTS-${BTS_INFO.ID}:")
            param_after_lnbts_1 = param_after_lnbts_1.replace("LNBTS/", "LNBTS-${BTS_INFO.ID}/")
            params_extend.append((param_before_lnbts_1, param_after_lnbts_1))
            # expression 2
            param_before_lnbts_2 = param_before.replace("LNBTS:", "${BTS_INFO.LNBTS}:")
            param_before_lnbts_2 = param_before_lnbts_2.replace("LNBTS/", "${BTS_INFO.LNBTS}/")
            param_after_lnbts_2 = param_after.replace("LNBTS:", "${BTS_INFO.LNBTS}:")
            param_after_lnbts_2 = param_after_lnbts_2.replace("LNBTS/", "${BTS_INFO.LNBTS}/")
            params_extend.append((param_before_lnbts_2, param_after_lnbts_2))
            # expression 3
            param_before_lnbts_3 = param_before.replace("LNBTS:", "LNBTS-1:")
            param_before_lnbts_3 = param_before_lnbts_3.replace("LNBTS/", "LNBTS-1/")
            param_after_lnbts_3 = param_after.replace("LNBTS:", "LNBTS-1:")
            param_after_lnbts_3 = param_after_lnbts_3.replace("LNBTS/", "LNBTS-1/")
            params_extend.append((param_before_lnbts_3, param_after_lnbts_3))
    print "parameters after extension:"
    os.write(log_fd, "parameters after extension:\n")
    for param_before_not_e, param_after_not_e in params_not_extend:
        print "'%s'\t\t'%s'" % (param_before_not_e, param_after_not_e)
        os.write(log_fd, "'%s'\t\t'%s'\n" % (param_before_not_e, param_after_not_e))
    for param_before, param_after in params_extend:
        print "%s\t\t%s" % (param_before, param_after)
        os.write(log_fd, "%s\t\t%s\n" % (param_before, param_after))
    os.close(log_fd)

    print '\n\n\nCoping files from old folder to new folder,please wait...'
    return cases_dir, cases_dir_old, params_not_extend + params_extend


def main():
    wrong_files = []
    replace_files = []
    cases_dir, cases_dir_old, all_params = handle_input_params()
    shutil.copytree(cases_dir_old, cases_dir)
    all_files = list_files(cases_dir)
    log_fd = os.open(log_name, os.O_RDWR | os.O_APPEND)
    for root, file in all_files:
        find_flag = False
        print "handling file: %s" % os.path.join(root, file)
        os.write(log_fd, "handling file: %s\n" % os.path.join(root, file))
        tmp_file = "test.txt"
        bak_file = "bak.txt"
        os.chdir(root)
        try:
            os.remove(tmp_file)
            os.remove(bak_file)
        except:
            pass
        try:
            shutil.copy2(file, bak_file)
            infile = open(file, "r")
            outfile = open(tmp_file, "w")
            for line in infile:
                for param_before, param_after in all_params:
                    if line.count(param_before):
                        find_flag = True
                        line = line.replace(param_before, param_after)
                outfile.write(line)
            infile.close()
            outfile.close()
            if find_flag:
                print "replacing file: %s" % os.path.join(root, file)
                os.write(log_fd, "replacing file: %s" % os.path.join(root, file))
                replace_files.append(os.path.join(root, file))
                shutil.move(tmp_file, file)
                os.remove(bak_file)
            else:
                shutil.move(bak_file, file)
                os.remove(tmp_file)
        except Exception, err_info:
            print "%s" % err_info
            os.write(log_fd, "%s\n" % err_info)
            wrong_files.append(os.path.join(root, file))
    print "########################"
    os.write(log_fd, "########################\n")
    print "corrected files list"
    os.write(log_fd, "corrected files list\n")
    print "########################"
    os.write(log_fd, "########################\n")
    if len(replace_files):
        print "total %s files are corrected:" % len(replace_files)
        os.write(log_fd, "total %s files are corrected:\n" % len(replace_files))
        for file_r in replace_files:
            print "%s" % file_r
            os.write(log_fd, "%s\n" % file_r)
    else:
        print "no file need to correct"
        os.write(log_fd, "no file need to correct\n")

    if len(wrong_files):
        print "#################################v"
        os.write(log_fd, "#################################\n")
        print "files list which can't be correct"
        os.write(log_fd, "files list which can't be correct\n")
        print "#################################"
        os.write(log_fd, "#################################\n")
        print "%s files can't be converted, maybe the file length is too long:" % len(wrong_files)
        os.write(log_fd, "%s files can't be converted, maybe the file length is too long:\n" % len(wrong_files))
        for wrong_file in wrong_files:
            print "%s" % wrong_file
            os.write(log_fd, "%s\n" % wrong_file)
    os.chdir(current_dir)
    print "#################################"
    os.write(log_fd, "#################################\n")
    print "All outputs have been written to %s" % log_name
    os.close(log_fd)
    if platform.system() == "Windows":
        time.sleep(60)


if __name__ == "__main__":
    main()
