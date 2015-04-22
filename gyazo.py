#coding:utf-8
import cgi
import boto
import hashlib
import datetime
from wsgiref.simple_server import make_server
import boto.s3.connection
from boto.s3.connection import S3Connection

ACCESS_KEY = ""
SECRET_KEY = ""
BUCKET_NAME = ""
RETURN_BASE_URL = ""

# if need
#S3Connection.DefaultHost='s3-ap-northeast-1.amazonaws.com'


def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def gyazo(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "image/png")]
    start_response(status, headers)
    
    if environ["REQUEST_METHOD"] == "POST":
        post_env = environ.copy()
        post_env["QUERY_STRING"] = ""
        post = cgi.FieldStorage(fp=environ["wsgi.input"],
                                environ=post_env,
                                keep_blank_values=True
                                )
        if "imagedata" in post.keys():
            imagedata = post["imagedata"].value
            gyazo_id = post["id"].value
            conn = boto.connect_s3(aws_access_key_id=ACCESS_KEY,
                                   aws_secret_access_key=SECRET_KEY,
                                   calling_format=boto.s3.connection.OrdinaryCallingFormat(),
                                   )
            gyazo = conn.get_bucket(BUCKET_NAME)
            h = hashlib.sha224(imagedata + gyazo_id + current_time()).hexdigest()
            while gyazo.get_key(h):
                h = hashlib.sha224(imagedata + gyazo_id + current_time()).hexdigest()
            k = gyazo.new_key("".join([h, ".png"]))
            k.set_metadata("Content-Type", "image/png")
            k.set_contents_from_string(imagedata)
            k.make_public()
            k.close()
            return ["".join([RETURN_BASE_URL, k.name])]
    return [RETURN_BASE_URL]

httpd = make_server("", 8080, gyazo)
print "Serving on port 8080..."

httpd.serve_forever()
