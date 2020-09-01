### Folder build_py_layer

We will need 2 layers to setup the backend in AWS lambda :

- python layer: contains the python packages in requirements

To build it, run:

```bash build_layer.sh```

Wait for the mypythonlibs36.zip to be created. This zip can be loaded as a Lambda layer from S3.

- ffmpeg layer

Can be built from this [link](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:145266761615:applications~ffmpeg-lambda-layer)


### Folder lambda_console

The lambda_function.py is the function to add to the console

test1.json is used for testing. This is the input format we will create in the webapp and send it through APi

Check this (link)[https://medium.com/analytics-vidhya/build-tesseract-serverless-api-using-aws-lambda-and-docker-in-minutes-dd97a79b589b?source=friends_link&sk=5c1c6948bc1a6c2a7e918e0874bf80c9] (begins at **2.2.**) for details on how to setup and test a lambda function and how to create a Rest Api


### app

This is the frontend of the webapp, When the api is deployed you need to replace the url in line 75