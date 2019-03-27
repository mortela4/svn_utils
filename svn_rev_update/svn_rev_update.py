import sys
import pysvn
import uuid
import argparse


def get_svn_revision(local_path):
    try:
        cli = pysvn.Client(local_path)
        svn_info = cli.info(local_path)
    except Exception as exc:
        print("PySvn exception: %s" % repr(exc))
        print("No valid repository found at PATH = '%s' ?" % local_path)
        return None

    return svn_info.revision.number


def working_copy_in_sync(local_path, ignore_list=None):
    mod_files = []
    non_files = []
    try:
        cli = pysvn.Client(local_path)
        svn_statuses = cli.status(local_path, ignore=True, recurse=True)
        for stat in svn_statuses:
            file_name = stat.data['path']
            file_status = stat.data['text_status']
            if str(file_status) == 'modified':
                if file_name in ignore_list:
                    print("File '%s' is set to IGNORED - skipping status check ...")
                else:
                    mod_files.append(file_name)
            if str(file_status) == 'unversioned':
                non_files.append(file_name)
        #
        svn_status = (len(mod_files) == 0)
    except Exception as exc:
        print("PySvn exception: %s" % repr(exc))
        print("No valid repository found at PATH = '%s' ?" % local_path)
        return None

    return svn_status, mod_files, non_files


if __name__ == "__main__":
    num_args = len(sys.argv)
    if num_args < 2:
        print("ERROR: missing argument - repository local copy path must be specified!")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="'svn_rev_update' command-line utility.\r\n \
                                                Pre-requisites: last argument must be path to a SVN-versioned folder!")
    # (Versioned-)Files-to-ignore argument:
    parser.add_argument('--ignore', '-i', action="store", dest="ignore_files_list", type=str,
                        help='List of files to ignore, separate with comma.')
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
        # TODO: add path-existence check here!

    if cli_args.ignore_files_list is None:
        print("No files to ignore ...")
    else:
        ignore_files = cli_args.ignore_files_list.split(',')
        print("Files to be ignored: %s as SREC-path ..." % ignore_files)
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
        repo_local_copy_dir = cli_args.path # TODO: check existence of folder before anything else!
    print("Scanning path: %s" % repo_local_copy_dir)

    # Run:
    # ====
    svn_changeset_num = get_svn_revision(repo_local_copy_dir)
    if svn_changeset_num is None:
        sys.exit(1)

    print("Got SVN revision = %d" % svn_changeset_num)

    is_synced, modified_files, unver_files = working_copy_in_sync(repo_local_copy_dir, ignore_list=ignore_files)
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
    svn_changeset_def = "#define SVN_CHANGESET_NUM" + "\t" + str(svn_changeset_num) + "\n"
    svn_status_def = "#define SVN_STATUS" + "\t\t\t" + svn_status_def + "\n"
    uuid_def = "#define BUILD_UUID" + "\t\t\t" + str(int(unique_id)) + "\n"
    with open(svn_revision_header_file, 'w') as changeset_file:
        changeset_file.writelines(svn_changeset_def + svn_status_def + uuid_def)
    print("--> Finished updating SVN revision header file.")


