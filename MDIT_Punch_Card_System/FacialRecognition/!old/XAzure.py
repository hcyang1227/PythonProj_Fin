#臉部辨識服務存取受限於資格和使用準則，以支援我們的「負責任的 AI 原則」。 臉部辨識服務僅供 Microsoft 受管理的客戶和合作夥伴使用。

import asyncio
import io
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition

# 供應所有辨識的金鑰
KEY1 = '5d98e5a915894b54'
KEY2 = '83918098babfd698'
# 臉部辨識的終端機網址
ENDPOINT = 'https://mdit-facerec.cognitiveservices.azure.com/'
# 辨識所有臉部清單的位址
IMAGE_BASE_URL = '.\\'

# 在人員組操作和刪除人員組示例中使用。
# 可以調用 list_person_groups 來打印一個預先存在的 PersonGroups 列表。
# SOURCE_PERSON_GROUP_ID 應全部為小寫字母數字。 例如，“mygroupname”（破折號可以）。
PERSON_GROUP_ID = str(uuid.uuid4())  # 分配一個隨機 ID（或命名它）

# 創建一個經過身份驗證的 FaceClient。
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY1+KEY2))

'''
創建人員組
'''
# 創建空的人組。 人員組 ID 必須為小寫字母數字和/或帶有“-”、“_”。
print('人員組:', PERSON_GROUP_ID)
face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID, recognition_model='recognition_04')
# 定義女生朋友
woman = face_client.person_group_person.create(PERSON_GROUP_ID, name="Woman")
# 定義男生朋友
man = face_client.person_group_person.create(PERSON_GROUP_ID, name="Man")

'''
檢測人臉並將其註冊到每個人
'''
# 在工作目錄中查找朋友的所有 jpeg 圖像（TBD 從網絡中提取）
woman_images = [".\\Chilin01.jpg", ".\\Chilin02.jpg"]
man_images = [".\\Keaton01.jpg", ".\\Keaton02.jpg"]

# 增加女生朋友
for image in woman_images:
    # 檢查圖像的質量是否足以識別。
    sufficientQuality = True
    detected_faces = face_client.face.detect_with_url(
        url=image, detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
    for face in detected_faces:
        if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
            sufficientQuality = False
            break
        face_client.person_group_person.add_face_from_url(
            PERSON_GROUP_ID, woman.person_id, image)
        print("face {} added to person {}".format(
            face.face_id, woman.person_id))

    if not sufficientQuality:
        continue

# 增加男性朋友
for image in man_images:
    # 檢查圖像的質量是否足以識別。
    sufficientQuality = True
    detected_faces = face_client.face.detect_with_url(
        url=image, detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
    for face in detected_faces:
        if face.face_attributes.quality_for_recognition != QualityForRecognition.high:
            sufficientQuality = False
            break
        face_client.person_group_person.add_face_from_url(
            PERSON_GROUP_ID, man.person_id, image)
        print("face {} added to person {}".format(face.face_id, man.person_id))

    if not sufficientQuality:
        continue

'''
訓練人組
'''
# 訓練人員組
print("pg resource is {}".format(PERSON_GROUP_ID))
rawresponse = face_client.person_group.train(PERSON_GROUP_ID, raw=True)
print(rawresponse)

while (True):
    training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
        sys.exit('Training the person group has failed.')
    time.sleep(5)

'''
根據定義的人組識別人臉
'''
# 用於測試的圖像組
test_image = ".\\test.jpg"

print('Pausing for 10 seconds to avoid triggering rate limit on free account...')
time.sleep(10)

# Detect faces
face_ids = []
# We use detection model 3 to get better performance, recognition model 4 to support quality for recognition attribute.
faces = face_client.face.detect_with_url(test_image, detection_model='detection_03',
                                         recognition_model='recognition_04', return_face_attributes=['qualityForRecognition'])
for face in faces:
    # Only take the face if it is of sufficient quality.
    if face.face_attributes.quality_for_recognition == QualityForRecognition.high or face.face_attributes.quality_for_recognition == QualityForRecognition.medium:
        face_ids.append(face.face_id)

# Identify faces
results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
print('Identifying faces in image')
if not results:
    print('No person identified in the person group')
for person in results:
    if len(person.candidates) > 0:
        print('Person for face ID {} is identified in image, with a confidence of {}.'.format(
            person.face_id, person.candidates[0].confidence))  # Get topmost confidence score
    else:
        print('No person identified for face ID {} in image.'.format(person.face_id))

print()
print('End of quickstart.')
