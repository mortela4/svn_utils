import sys
import os
import pysvn
import uuid
import argparse

from pathlib import Path   # To adjust file-paths to OS-specific format (i.e. 'unification')


VER_MAJOR = 1           # I.e. first 'production' variant.
VER_MINOR = 0
VER_SUBMINOR = 3        # Fix: "-s" option skip-folders have their PATH normalized per OS-type, before checking (i.e. mix of '/' and '\' slashes is OK).

APP_VER = [VER_MAJOR, VER_MINOR, VER_SUBMINOR]     
VER_STR = str("%s.%s.%s" % (APP_VER[0], APP_VER[1], APP_VER[2]))


# **************** HELPERS **************************

def ignore_or_skip(file_path, local_path, ignore_list=None, skip=None, debug=False):
    # First, check files to be ignored:
    if ignore_list is not None and len(ignore_list)>0:
        base_file_name = os.path.basename(file_path)
        if base_file_name in ignore_list:
            if debug:
                print("File '%s' is set to IGNORED - skipping status check ..." % base_file_name)
            return True
    # Second, check folders to be skipped:
    if skip is not None and len(skip) > 0:
        for skip_folder in skip:
            full_skip_path = os.path.join(local_path, skip_folder)
            # NOTE: adjustment of file-paths necessary!! (may contain mix of '/' and '\' slahes!)
            os_generic_skip_path = str( Path(full_skip_path) )
            os_generic_file_path = str( Path(file_path) )
            # NOW we can compare ...
            if debug:
                print("Checking path='%s' against skip-path='%s' ..." % (os_generic_file_path, os_generic_skip_path))
            if os_generic_file_path.startswith(os_generic_skip_path):
                if debug:
                    print("Folder '%s' is set to SKIP - skipping status check for file %s beneath this folder ..." %
                          (os_generic_skip_path, os_generic_file_path))
                return True
        # Default:
        return False


# **************** SVN functions *********************************

def get_svn_revision(cli, local_path):
    try:
        # cli = pysvn.Client(local_path)
        svn_info = cli.info2(local_path, recurse=True)
        rev_info = svn_info[0][1]['rev']
    except Exception as exc:
        print("PySvn exception: %s" % repr(exc))
        print("No valid repository found at PATH = '%s' ?" % local_path)
        return None

    return rev_info.number


def working_copy_in_sync(cli, local_path, ignore_list=None, skip=None, debug=False):
    mod_files = list()
    non_files = list()
    highest_rev_found = 0
    try:
        # cli = pysvn.Client(local_path)
        svn_statuses = cli.status(local_path, ignore=True, recurse=True, )
        for stat in svn_statuses:
            file_name = stat.data['path']
            if debug:
                print("INFO: checking file = %s" % file_name)
            file_status = stat.data['text_status']
            if str(file_status) == 'modified':
                if ignore_or_skip(file_path=file_name, local_path=local_path, ignore_list=ignore_list, skip=skip):
                    print("Skipping status check for '%s' ..." % file_name)
                else:
                    mod_files.append(file_name)
            if str(file_status) == 'unversioned':
                non_files.append(file_name)
            else:
                file_rev_no = get_svn_revision(cli=cli, local_path=file_name)
                if file_rev_no > highest_rev_found:
                    highest_rev_found = file_rev_no
        #
        svn_status = (len(mod_files) == 0)
    except AttributeError as exc:
        print("File-PATH check failed: %s" % repr(exc))
        return None
    except Exception as exc:
        print("Possible 'PySvn' exception: %s" % repr(exc))
        print("No valid repository found at PATH = '%s' ?" % local_path)
        return None

    return svn_status, mod_files, non_files, highest_rev_found


# ****************************** Command-Line Argument Handling and Processing **************************
if __name__ == "__main__":
    print("svn_rev_update ver." + VER_STR)
    print("")
    num_args = len(sys.argv)
    if num_args < 2:
        print("ERROR: missing argument - repository local copy path must be specified!")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="'svn_rev_update' command-line utility.\r\n \
                                                Pre-requisites: last argument must be path to a SVN-versioned folder!")
    # Timestamp flag (add timestamp string to version-info file):
    parser.add_argument('--time', '-t', action='store_true', dest='time_stamp',
                        help='Add (build-time) timestamp string to version-info file.')
    # (Versioned-)Files-to-ignore argument:
    parser.add_argument('--ignore', '-i', action="store", dest="ignore_files_list", type=str,
                        help='List of files to ignore, separate with comma.')
    # (Versioned-)Paths-to-ignore argument:
    parser.add_argument('--skip', '-s', action="store", dest="skip_paths_list", type=str,
                        help='List of paths to skip, separate with comma.')
    # Output-file ('svn_changeset.h' default) argument:
    parser.add_argument('--out', '-o', action="store", dest="out_file", type=str,
                        help='Output SVN-info file, default svn_changeset.h')
    # Path to SVN-versioned folder:
    parser.add_argument(action="store", dest="path", type=str,
                        help="Path to SVN-versioned project folder. Default '.'")

    # Parse:
    # ======
    try:
        cli_args = parser.parse_args(sys.argv[1:])
    except Exception as e:
        print("Got '%s' exception - hmmm, how to suppress ...???" % e)

    if cli_args.time_stamp:
        from datetime import datetime
        time_now = datetime.now().replace(microsecond=0)
        print("Adding NOW-timestamp '%s' ..." % time_now)
    #
    if cli_args.ignore_files_list is None:
        print("No files to ignore ...")
        ignore_files = list()
    else:
        ignore_files = cli_args.ignore_files_list.split(',')
        print("Files to be ignored: %s" % ignore_files)
    #
    if cli_args.skip_paths_list is None:
        print("No paths to skip ...")
        skip_paths = list()
    else:
        skip_paths = cli_args.skip_paths_list.split(',')
        print("Paths (under local copy) to be skipped: %s" % skip_paths)
    #
    if cli_args.out_file is None:
        svn_revision_header_file = "svn_changeset.h"
    else:
        svn_revision_header_file = cli_args.out_file
    print("SVN-info file: '%s'" % svn_revision_header_file)
    # Last argument is always Path to SVN-versioned folder to check:
    if cli_args.path is None:
        repo_local_copy_dir = "."
        print("Warning - using working directory as default path!")
    else:
        # TODO: check existence of folder before anything else!
        repo_local_copy_dir = cli_args.path
    print("Scanning path: %s" % repo_local_copy_dir)

    # Run:
    # ====
    # Create SVN-client instance - do NOT specify a local-PATH as argument
    # (as this will create "auth"/"server"/"config"/"readme.txt" files in that folder)
    svn_client = pysvn.Client()

    svn_changeset_num = get_svn_revision(cli=svn_client, local_path=repo_local_copy_dir)
    if svn_changeset_num is None:
        sys.exit(1)

    print("Got SVN revision = %d" % svn_changeset_num)

    is_synced, modified_files, unver_files, highest_rev_no = \
        working_copy_in_sync(cli=svn_client, local_path=repo_local_copy_dir, ignore_list=ignore_files, skip=skip_paths)

    if svn_changeset_num < highest_rev_no:
        print("WARNING: some files in project has been SELECTIVELY updated! This may be DANGEROUS!!!")
        print("+++++++++ Please update project from top-level!! +++++++++++")
        top_level_updated = False   # May use this to ABORT build f.ex.
    else:
        print("UPDATE-status: Project is correctly updated from top-level recursively down ...")
        top_level_updated = True
        
    if is_synced:
        print("Working copy CLEAN.\r\nStatus in header file definition SVN_STATUS set to 'clean'")
        svn_status_def = "\"clean\""
    else:
        svn_status_def = "\"dirty\""
        print("Warning: working copy DIRTY!\r\nStatus in header file definition SVN_STATUS set to 'dirty'")
        print("Modified files and/or directories:")
        print("==========================================================================================")
        for f in modified_files:
            print(f)
        print("==========================================================================================")
    if len(unver_files) > 0:
        print("")
        print("Note: there are unversioned files and/or directories:")
        print("==========================================================================================")
        for f in unver_files:
            print(f)
        print("==========================================================================================")

    # Create unique ID number:
    unique_id = uuid.uuid4()
    print("UUID for this build: %d" % unique_id)

    # Update header file:
    print("--> Updating SVN revision header file '%s' ..." % svn_revision_header_file)
    svn_changeset_def = "#define SVN_CHANGESET_NUM" + "\t\t" + str(svn_changeset_num) + "\n"
    svn_status_def = "#define SVN_STATUS" + "\t\t\t\t" + svn_status_def + "\n"
    svn_is_clean_def = "#define LOCAL_IS_CLEAN" + "\t\t\t" + str(is_synced).lower() + "\n"
    svn_is_top_level_updated_def = "#define IS_TOP_LEVEL_UPDATED" + "\t" + str(top_level_updated).lower() + "\n"
    uuid_def = "#define BUILD_UUID" + "\t\t\t\t" + str(int(unique_id)) + "\n"
    if cli_args.time_stamp:
        date_stamp, time_stamp = str(time_now).split()
        time_stamp_def = "#define TIME_STAMP" + "\t\t\t\t\"" + time_stamp + "\"\n"
        date_stamp_def = "#define DATE_STAMP" + "\t\t\t\t\"" + date_stamp + "\"\n"
    else:
        # No time or date info added ...
        time_stamp_def = ""
        date_stamp_def = ""
    #
    info_file_heading = "/****** Generated by 'svn_rev_update' ver." + VER_STR + " ***********/\n\n"
    #
    with open(svn_revision_header_file, 'w') as changeset_file:
        changeset_file.writelines(info_file_heading +
                                  svn_changeset_def +
                                  svn_status_def +
                                  svn_is_clean_def +
                                  svn_is_top_level_updated_def +
                                  uuid_def +
                                  date_stamp_def +
                                  time_stamp_def)
    #
    print("--> Finished updating SVN revision header file.")


