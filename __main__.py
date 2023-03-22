import boto3
import uuid
import os


s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
# =================
# === FUNCTIONS ===
# =================

def create_bucket_name(bucket_prefix):
    """
    Description:
        Creates a unique name for an s3 bucket
        (bucket name must be between 3 and 63 chars long)

    Requires:
        bucket_prefix - the prefix for the bucket's name

    Return:
        string - a unique name for the bucket
    """
    return ''.join([bucket_prefix, str(uuid.uuid4())])

def create_bucket(bucket_prefix, s3_connection):
    """
    Description:
        Creates a s3 bucket

    Requires:
        bucket_prefix - the prefix for the bucket's name
        s3_connection - handle type of connection client or resource
    
    Return:
        bucket_name - a unique name of the s3 bucket
        bucket_response - dictionary containing information about the created s3 bucket 
    """
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
        'LocationConstraint': current_region})
    print(bucket_name, current_region)
    return bucket_name, bucket_response

def create_temp_file(size, file_name, file_content):
    """
    Description:
        Creates simple file with unique name 
        containing some simple payload

    Requires:
        size - multiplier for a file_content payload
        file_name - prefix for a temp file
        file_content - payload that will be multiplied by size and inserted to temp file
    
    Return:
        string - a unique file name of the generated file
    """
    random_file_name = ''.join([str(uuid.uuid4().hex[:6]), file_name])
    with open(random_file_name, 'w') as f:
        f.write(str(file_content) * size)
    return random_file_name

def copy_to_bucket(bucket_from_name, bucket_to_name, file_name):
    """
    Description:
        Creates a copy of a file
        that is located in different s3 bucket

    Requires:
        bucket_from_name - name of the s3 bucket where is file located
        bucket_to_name - name of the s3 bucket where to copy file
        file_name - name of the file that is located in s3 bucke
    """
    copy_source = {
        'Bucket': bucket_from_name,
        'Key': file_name
    }
    s3_resource.Object(bucket_to_name, file_name).copy(copy_source)

def enable_bucket_versioning(bucket_name):
    """
    Description:
        Enables file versioning on the s3 bucket
        Read more on: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html

    Requires:
        bucket_name - name of the s3 bucket on which is action will be aplied
    """
    bkt_versioning = s3_resource.BucketVersioning(bucket_name)
    bkt_versioning.enable()
    print(bkt_versioning.status)

def suspend_bucket_versioning(bucket_name):
    """
    Description:
        Suspend file versioning on the s3 bucket
        Read more on: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html

    Requires:
        bucket_name - name of the s3 bucket on which is action will be aplied
    """
    bkt_versioning = s3_resource.BucketVersioning(bucket_name)
    bkt_versioning.suspend()
    print(bkt_versioning.status)

def delete_all_objects(bucket_name):
    """
    Description:
        Delete all object within s3 bucket
        WARNING: That is also deletes files with versioning enabled

    Requires:
        bucket_name - name of the s3 bucket on which is action will be aplied
    """
    res = []
    bucket=s3_resource.Bucket(bucket_name)
    for obj_version in bucket.object_versions.all():
        res.append({'Key': obj_version.object_key,
                    'VersionId': obj_version.id})
    print(res)
    bucket.delete_objects(Delete={'Objects': res})

# =====================
# === HOMEWORK TEST ===
# =====================

def pause():
    input("Press enter to continue...")
    print()

def homework_test():
    """
    Description:
        This function is to test and demonstrate s3 basic functionality

    Requires:
        AWS CLI must be installed and configurated
        An AWS account have to logged withinh AWS CLI

    Actions:
        1) Creates 2 buckets:
            - Named: s3-client-{unique_id}
                Via s3_client connection type
            - Named: s3-resource-{unique_id}
                Via s3_resource connection type

        2) Creates 3 random files:
            - {unique_prefix}firstfile.txt
            - {unique_prefix}secondfile.txt
            - {unique_prefix}thirdfile.txt

        3) Upload first file to s3-resource bucket
        4) Downloads first file back to temp folder
        5) Copying first file from s3-resource bucket to s3-client bucket
        6) Deletes new file from s3-client bucket
        7) Upload second file to s3-resource bucket and making it public
        8) Print out ACL of the second file that was just uploaded
        9) Changes this file ACL to 'private' setting
        10) Enables file versioning in s3-resource bucket
        11) Try version control by uploading new version of first file
        12) Deletes created buckets
    """
    print("ACTION (1): Creates 2 buckets")
    try:
        client_bucket_name, client_bucket_response = create_bucket("s3-client", s3_resource.meta.client)
    except Exception as e:
        print("An exception has occurred:", type(e).__name__)

    try:
        resource_bucket_name, resource_bucket_response = create_bucket("s3-resource", s3_resource)
    except Exception as e:
        print("An exception has occurred:", type(e).__name__)
    print("ACTION: COMPLETED")
    print("ACTION: To check buckets go to links bellow:\n")
    session = boto3.session.Session()
    current_region = session.region_name
    print(f"client_bucket: https://s3.console.aws.amazon.com/s3/buckets/{client_bucket_name}?region={current_region}")
    print(f"resource_bucket: https://s3.console.aws.amazon.com/s3/buckets/{resource_bucket_name}?region={current_region}")
    pause()

    print("ACTION (2): Creates 3 random files:")
    first_file_name = create_temp_file(300, 'firstfile.txt', 'FIRSTFILE_TEXT_CONTENT')
    second_file_name = create_temp_file(400, 'secondfile.txt', 'SECONDFILE_TEXT_CONTENT')  
    third_file_name  = create_temp_file(300, 'thirdfile.txt', 'THIRDFILE_TEXT_CONTENT')
    print("ACTION: COMPLETED")
    print("ACTION: To check generated files you can go and open them by this pathes:\n")
    print(f"1) {os.path.realpath(first_file_name)}")
    print(f"2) {os.path.realpath(second_file_name)}")
    print(f"3) {os.path.realpath(third_file_name)}")
    #pause()

    print("ACTION (3): Upload first file to s3-resource bucket")
    resource_bucket = s3_resource.Bucket(name=resource_bucket_name)
    first_object = s3_resource.Object(
        bucket_name=resource_bucket_name, key=first_file_name)
    try:
        first_object.upload_file(first_file_name)
    except Exception as e:
        print("An exception has occurred:", type(e).__name__)
    print("ACTION: COMPLETED")
    print("ACTION: To check uploaded file go to link bellow:\n")
    print(f"https://s3.console.aws.amazon.com/s3/object/{resource_bucket_name}?region={current_region}&prefix={first_file_name}")
    #pause()

    print("ACTION (4): Downloads first file back to temp folder")
    try:
        s3_resource.Object(resource_bucket_name, first_file_name).download_file(
            f'/tmp/{first_file_name}')
    except Exception as e:
        print("An exception has occurred:", type(e).__name__)
    print("ACTION: COMPLETED")
    print("ACTION: To check downloaded file you can go and open it by this path:\n")
    print(f"{os.getcwd()}/tmp/{first_file_name}")
    pause()

    print("ACTION (5): Copying first file from s3-resource bucket to s3-client bucket")
    copy_to_bucket(resource_bucket_name, client_bucket_name, first_file_name)
    print("ACTION: COMPLETED")
    print("ACTION: To check copied file go to link bellow:\n")
    print(f"https://s3.console.aws.amazon.com/s3/object/{client_bucket_name}?region={current_region}&prefix={first_file_name}")
    pause()

    print("ACTION (6): Deletes new file from s3-client bucket")
    s3_resource.Object(client_bucket_name, first_file_name).delete()
    print("ACTION: COMPLETED")
    print("ACTION: You can go to links bellow and check if file have been deleted:\n")
    print(f"Deleted file: https://s3.console.aws.amazon.com/s3/object/{client_bucket_name}?region={current_region}&prefix={first_file_name}")
    print(f"client_bucket_name: https://s3.console.aws.amazon.com/s3/buckets/{client_bucket_name}?region={current_region}")
    pause()

    print("ACTION (7): Upload second file to s3-resource bucket and making it public")
    second_object = s3_resource.Object(resource_bucket_name, second_file_name)
    second_object.upload_file(second_file_name, ExtraArgs={'ACL': 'public-read'})
    print("ACTION: COMPLETED")
    print("ACTION: You can try to download this file in Incognito Mode to check if it's public:\n")
    print(f"https://{resource_bucket_name}.s3.{current_region}.amazonaws.com/{second_file_name}")
    pause()

    print("ACTION (8): Print out ACL of the second file that was just uploaded")
    second_object_acl = second_object.Acl()
    print(second_object_acl.grants)
    print("ACTION: COMPLETED")
    print("ACTION: You can check ACL properties by yourself via this link:\n")
    print(f"https://s3.console.aws.amazon.com/s3/object/{resource_bucket_name}?region={current_region}&prefix={second_file_name}&tab=permissions")
    pause()

    print("ACTION (9): Changes this file ACL to 'private' setting")
    response = second_object_acl.put(ACL='private')
    print(second_object_acl.grants)
    print("ACTION: COMPLETED")
    print("ACTION: Again, you can check ACL properties by yourself via this link:\n")
    print(f"https://s3.console.aws.amazon.com/s3/object/{resource_bucket_name}?region={current_region}&prefix={second_file_name}&tab=permissions")
    print("\nACTION: You could also check if this file is private by open your browser in Incognito Mode:")
    print("WARNING: You need to reopen browser in Incognito Mode!\n")
    print(f"https://{resource_bucket_name}.s3.{current_region}.amazonaws.com/{second_file_name}")
    pause()

    print("ACTION (10) Enables file versioning in s3-resource bucket")
    enable_bucket_versioning(resource_bucket_name)
    print("ACTION: COMPLETED")
    print("ACTION: You can check bucket properties by yourself via this link:\n")
    print(f"https://s3.console.aws.amazon.com/s3/buckets/{resource_bucket_name}?region={current_region}&tab=properties")
    pause()

    print("ACTION (11) Try version control by uploading new version of second file")
    s3_resource.Object(resource_bucket_name, second_file_name).upload_file(second_file_name)
    print(s3_resource.Object(resource_bucket_name, second_file_name).version_id)
    print("ACTION: COMPLETED")
    print("ACTION: You can check versions by yourself via this link:\n")
    print(f"https://s3.console.aws.amazon.com/s3/object/{resource_bucket_name}?region={current_region}&prefix={second_file_name}&tab=versions")
    pause()

    print("ACTION (12) Deletes created buckets")
    try:
        delete_all_objects(resource_bucket_name)
        #delete_all_objects(client_bucket_name)
        s3_resource.Bucket(resource_bucket_name).delete()
        s3_resource.meta.client.delete_bucket(Bucket=client_bucket_name)
    except Exception as e:
        print("An exception has occurred:", type(e).__name__)
    print("ACTION: COMPLETED")
    print("ACTION: You can check buckets list by yourself via this link:\n")
    print(f"https://s3.console.aws.amazon.com/s3/buckets?region={current_region}")
    return

if __name__ == '__main__':
    homework_test()

print("END OF THE FILE")