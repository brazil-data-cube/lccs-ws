#!/usr/bin/env bash
#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
#
# Land Cover Classification System Web Service. is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

echo "BUILD STARTED"
echo
echo "NEW TAG - lccs:"
read LCCS_TAG

IMAGE_LCCS="lccs"
IMAGE_LCCS_FULL="${IMAGE_LCCS}:${LCCS_TAG}"

docker build -t ${IMAGE_LCCS_FULL} -f docker/Dockerfile . --no-cache
docker push ${IMAGE_LCCS_FULL}

echo "BUILD ${IMAGE_LCCS_FULL} FINISHED"