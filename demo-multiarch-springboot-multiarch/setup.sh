#!/usr/bin/env bash

# Change these values for your own environment
# it should match what values you use in the CDK app
# if you are using this script together to deploy
# the multi-arch demo

AWS_DEFAULT_REGION=eu-central-1
AWS_ACCOUNT=704533066374
AWS_ECR_REPO=demo-springboot-ecsanywhere
AWS_CC_REPO=demo-springboot-repo
COMMIT_HASH="abcdef"

# You can alter these values, but the defaults will work for any environment

IMAGE_TAG=${COMMIT_HASH:=latest}
ARM_TAG=${COMMIT_HASH}-arm64
AMD_TAG=${COMMIT_HASH}-amd64
DOCKER_CLI_EXPERIMENTAL=enabled
REPOSITORY_URI=$AWS_ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$AWS_ECR_REPO

# You do not need to change anything below. If successful, you will get a new ECR Repo
# with an x86 and Arm built container image and all the needed manifests

# Setup Source Code via CodeCommit

if (aws codecommit get-repository --repository-name $AWS_CC_REPO ) then
        echo "Skipping the create repo as already exists"
else
        echo "Creating repos as it does not exists"
        aws codecommit create-repository --region $AWS_DEFAULT_REGION --repository-name $AWS_CC_REPO
fi


# Login to ECR

$(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)

# create AWS ECR Repo

if (aws ecr describe-repositories --repository-names $AWS_ECR_REPO ) then
	echo "Skipping the create repo as already exists"
else
	echo "Creating repos as it does not exists"
	aws ecr create-repository --region $AWS_DEFAULT_REGION --repository-name $AWS_ECR_REPO
fi

# Build initial image and upload to ECR Repo

cd springbootdemo
./mvnw package

docker build -t $REPOSITORY_URI:latest .
docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$AMD_TAG
docker push $REPOSITORY_URI:$AMD_TAG

# Use buildx to build the arm image and upload to ECR Repo
# this works as we have enabled experimental support

docker buildx build --platform linux/arm64 -t $REPOSITORY_URI:latest .
docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$ARM_TAG
docker push $REPOSITORY_URI:$ARM_TAG

# Create the image manifests and upload to ECR

docker manifest create $REPOSITORY_URI:$COMMIT_HASH $REPOSITORY_URI:$ARM_TAG $REPOSITORY_URI:$AMD_TAG
docker manifest annotate --arch arm64 $REPOSITORY_URI:$COMMIT_HASH $REPOSITORY_URI:$ARM_TAG
docker manifest annotate --arch amd64 $REPOSITORY_URI:$COMMIT_HASH $REPOSITORY_URI:$AMD_TAG
docker manifest inspect $REPOSITORY_URI:$COMMIT_HASH
docker manifest push $REPOSITORY_URI:$COMMIT_HASH

