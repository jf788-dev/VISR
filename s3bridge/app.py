# s3bridge/app.py
import os, datetime
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import boto3
from botocore.config import Config

ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
ACCESS   = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
SECRET   = os.getenv("MINIO_SECRET_KEY", "minioadmin")
EXPIRES  = int(os.getenv("PRESIGN_EXPIRES", "3600"))

app = Flask(__name__)
CORS(app)

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS,
    aws_secret_access_key=SECRET,
    config=Config(signature_version="s3v4"),
)

@app.get("/health")
def health():
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()+"Z"}

@app.get("/buckets")
def list_buckets():
    out = []
    resp = s3.list_buckets()
    for b in resp.get("Buckets", []):
        out.append({"name": b["Name"], "created": b["CreationDate"].isoformat()})
    return jsonify(out)

@app.get("/objects")
def list_objects():
    bucket = request.args.get("bucket")
    if not bucket:
        abort(400, "missing bucket")
    prefix    = request.args.get("prefix", "")
    delimiter = request.args.get("delimiter", "/")
    maxkeys   = int(request.args.get("max_keys", "1000"))
    token     = request.args.get("token")

    kwargs = {"Bucket": bucket, "Prefix": prefix, "Delimiter": delimiter, "MaxKeys": maxkeys}
    if token: kwargs["ContinuationToken"] = token

    resp = s3.list_objects_v2(**kwargs)

    # folders (common prefixes)
    prefixes = [p["Prefix"] for p in resp.get("CommonPrefixes", [])]

    # objects
    objects = []
    for o in resp.get("Contents", []):
        key = o["Key"]
        # skip the “folder marker” itself if present
        if key.endswith("/") and key == prefix:
            continue
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=EXPIRES,
        )
        objects.append({
            "key": key,
            "size": o.get("Size", 0),
            "last_modified": o["LastModified"].isoformat(),
            "etag": o.get("ETag", "").strip('"'),
            "url": url
        })

    return jsonify({
        "bucket": bucket,
        "prefix": prefix,
        "prefixes": prefixes,
        "objects": objects,
        "is_truncated": resp.get("IsTruncated", False),
        "next_token": resp.get("NextContinuationToken")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7070)