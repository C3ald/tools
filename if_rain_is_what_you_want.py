import sys
import os
import argparse
import requests as r
import boto3
import threading as th
import time as t


# def scan_for_buckets(target: str):
#     try:
#         req = r.get(f'http://{target}')
#         print(f'possible s3 buckets found for target!')
#         return 1

#     except r.exceptions.ConnectionError:
#         None


def upload_file(s3, file, bucket):
        print(f'uploading: {file}......')
        s3.upload_file(file)
        print('uploaded!')


def list_buckets(s3) -> list:
        response = s3.list_buckets()['Buckets']
        buckets = []
        for bucket in response:
                try:
                        print('Bucket name: {}, Created on: {}'.format(bucket['Name'], bucket['CreationDate']))
                        buckets.append(str(bucket['Name']))
                except:
                        None
        return buckets


def list_bucket_contents(bucket, s3):
        print('-----------------------------------------')
        print(f'contents of bucket: {bucket}')
        bucket = s3.Bucket(bucket)
        contents = []
        for bucket_obj in bucket.objects.all():
                print(bucket_obj.key)
                contents.append(bucket_obj.key)
        return contents
        

def download_contents_of_bucket(bucket:str, s3, contents:list):
        os.system(f'mkdir dumps')
        os.system(f'mkdir dumps/{bucket}')
        for content in contents:
                try:
                        if r'/' in content:
                                content_parsed = content.replace(r'/', '')         
                        else:
                                content_parsed = content
                        
                        s3.Bucket(bucket).download_file(content, f'./dumps/{bucket}/{content_parsed}')
                except Exception as e:
                        print(e)

if __name__ == '__main__':
        print('\n'*10)
        banner = """ 
                             000      00
                           0000000   0000
              0      00  00000000000000000
            0000 0  000000000000000000000000       0
         000000000000000000000000000000000000000 000
        0000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000
              / / / / / / / / / / / / / / / /
            / / / / / / / / / / / / / / /
            / / / / / / / / / / / / / / /
          / / / / / / / / / / / / / /
          / / / / / / / / / / / / /
        / / / / / / / / / / / /
        / / / / / / / / / /
        if rain is what you want... s3 bucket scanner and dumper"""
        print(banner)
        parser = argparse.ArgumentParser()
        parser.add_argument('--target', help='required for finding s3 bucket', type=str)
        parser.add_argument('--key_id', help='access key, not required', type=str, required=False)
        parser.add_argument('--mode', help='1 for scanning and listing bucket contents, 2 for dumping all contents of data, 3 is for uploading files to a bucket. default is 1', default=1, type=int)
        parser.add_argument('--key_secret', help='access key secret, not required', type=str, required=False)
        parser.add_argument('--file_to_upload', help='file to upload for mode 3', required=False)
        parser.add_argument('--bucket', help='specify bucket to upload file to.', required=False)
        args = parser.parse_args()
        target = args.target
        key_id = args.key_id
        mode = args.mode
        key_secret = args.key_secret
        file = args.file_to_upload
        target_bucket = args.bucket
        if not target:
                print("no target found! EXITING....")
                exit()
        if key_id and key_secret:
                s3session = boto3.Session(aws_access_key_id=key_id, aws_secret_access_key=key_secret)
                s3 = s3session.client('s3', endpoint_url=f'http://{target}')
                keys = 1
        else:
                print('missing secret key or access key, continuing.....')
                s3 = boto3.client('s3', endpoint_url=f'http://{target}')
                keys = 0
                
        if mode == 1:
                buckets = list_buckets(s3)
                
                if keys == 0:
                        s3 = boto3.resource('s3', endpoint_url=f'http://{target}')
                else:
                        s3 = s3session.resource('s3', endpoint_url=f'http://{target}')
                
                for bucket in buckets:
                	contents = list_bucket_contents(bucket, s3)
        elif mode == 2:
                buckets = list_buckets(s3)

                if keys == 0:
                        s3 = boto3.resource('s3', endpoint_url=f'http://{target}')
                else:
                        s3 = s3session.resource('s3', endpoint_url=f'http://{target}')
                
                
                for bucket in buckets:
                        contents = list_bucket_contents(bucket, s3)
                        download_contents_of_bucket(bucket, s3, contents)
        
        elif mode == 3:
                bucket = target_bucket
                if keys == 0:
                        s3 = boto3.client('s3', endpoint_url=f'http://{target}')
                else:
                        s3 = s3session.client('s3', endpoint_url=f'http://{target}')
                upload_file(s3, file, bucket)
                        
                        
        else:
                print('invalid mode found, exiting.......')
                exit()
