import kfp
from kfp import dsl
from kubernetes.client.models import V1EnvVar
from kfp.components import func_to_container_op, InputPath, OutputPath
import os


def minio_download_op(url):
	return dsl.ContainerOp(
        name='Minio Download',
        image='amazon/aws-cli',
        command=['aws'],
        arguments=[# argumentsにのみ変数を利用できる
			'--endpoint', MINIO_ENDPOINT, 
			's3', 'cp', url, f'/tmp/result/data/', '--recursive'
		],
		# 下流(downstream)のタスクにデータを受け渡したいときは、
        # ファイルに書き出してそのパスをfile_outputsに渡すと値を渡せる(テキストのみ？)
        file_outputs={
            'data': '/tmp/result/data'
        }
    )

def train_op(data):
	return dsl.ContainerOp(
        name='Train Mnist',
        image='takumi2786/mnist-runner:latest',
		# file_outputsに記載したartifactをコンテナにアタッチできる
		artifact_argument_paths=[
            dsl.InputArgumentPath(
                argument=data, 
				path=INPUT_PATH,
			),
        ],
		# command=["ls", "/tmp/inputs/data"]
        command=['python', '/app/train.py', '--epochs', '1', '--save-model'],
		# argumentsにのみ変数を利用できる
        arguments=[],
		file_outputs={
			# modelが出力される
            'data': OUTPUT_PATH
        }
    )

INPUT_PATH = "/tmp/inputs/data"
OUTPUT_PATH = "/tmp/result/data"
MINIO_ENDPOINT = 'http://minio-service.kubeflow.svc.cluster.local:9000'

@dsl.pipeline(
    name='Train Mnis',
    description='A pipeline with two sequential steps.'
)
def pipeline(url='s3://lake/mnist'):
	"""A pipeline with two sequential steps."""
	access_key = V1EnvVar(name='AWS_ACCESS_KEY_ID', value='minio')
	access_secret = V1EnvVar(name='AWS_SECRET_ACCESS_KEY', value='minio123')
	region = V1EnvVar(name='AWS_DEFAULT_REGION', value='ap-northeast-1')

	download_step = minio_download_op(url)\
		.add_env_variable(access_key)\
		.add_env_variable(access_secret)\
		.add_env_variable(region)
	
	train_task = train_op(download_step.outputs["data"])

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(pipeline, __file__ + '.yaml')
