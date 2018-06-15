import sys
import pysvn
import uuid


def get_svn_revision(local_path):
    try:
        cli = pysvn.Client(local_path)
        svn_info = cli.info(local_path)
    except Exception as exc:
        print("PySvn exception: %s" % repr(exc))
        print("No valid repository found at PATH = '%s' ?" % local_path)
        return None

    return svn_info.revision.number


def working_copy_in_sync(local_path):
    mod_files = []
    non_files = []
    try:
        cli = pysvn.Client(local_path)
        svn_statuses = cli.status(local_path, ignore=True, recurse=True)
        for stat in svn_statuses:
            file_name = stat.data['path']
            file_status = stat.data['text_status']
            if str(file_status) == 'modified':
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

    repo_local_copy_dir = sys.argv[1]
    print("Scanning path: %s" % repo_local_copy_dir)

    if num_args == 3:
        svn_revision_header_file = sys.argv[2]
    else:
        svn_revision_header_file = "svn_changeset.h"

    svn_changeset_num = get_svn_revision(repo_local_copy_dir)
    if svn_changeset_num is None:
        sys.exit(1)

    print("Got SVN revision = %d" % svn_changeset_num)

    is_synced, modified_files, unver_files = working_copy_in_sync(repo_local_copy_dir)
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


