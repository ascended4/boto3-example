
# Boto3 - demonstration

This project is example of how to work with AWS S3 buckets by using boto3
Work demonstration it running folowing actions:

- Creates 2 buckets:
    - Named: s3-client-{unique_id} (Via s3_client connection type)
    - Named: s3-resource-{unique_id} (Via s3_resource connection type)
- Creates 3 random files:
    - {unique_prefix}firstfile.txt
    - {unique_prefix}secondfile.txt
    - {unique_prefix}thirdfile.txt
- Upload first file to s3-resource bucket
- Downloads first file back to temp folder
- Copying first file from s3-resource bucket to s3-client bucket
- Deletes new file from s3-client bucket
- Upload second file to s3-resource bucket and making it public
- Print out ACL of the second file that was just uploaded
- Changes this file ACL to 'private' setting
- Enables file versioning in s3-resource bucket
- Try version control by uploading new version of first file
- Deletes created buckets

