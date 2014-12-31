import json

MAX_RENDER_SIZE = (1024 ** 2) * 3

ALLOWED_ORIGIN = '*'

OSF_USER = 'osf-user{0}'
OSF_USER_POLICY_NAME = 'osf-user-policy'
OSF_USER_POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt1392138408000",
                "Effect": "Allow",
                "Action": [
                    "hdfs:*"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Sid": "Stmt1392138440000",
                "Effect": "Allow",
                "Action": [
                    "iam:DeleteAccessKey",
                    "iam:DeleteUser",
                    "iam:DeleteUserPolicy"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]
    }
)
